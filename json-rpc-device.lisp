;; -----------------------------------------------------------------------------
;; ASDF Dependencies
;; -----------------------------------------------------------------------------

(asdf:oos 'asdf:load-op :iolib)
(asdf:oos 'asdf:load-op :cl-json)
(asdf:oos 'asdf:load-op :bordeaux-threads)

;; -----------------------------------------------------------------------------
;; Temporary for testing external to ACT-R tree
;; -----------------------------------------------------------------------------

#-:act-r-6.0
(load "~/actr6/load-act-r-6.lisp")

;; -----------------------------------------------------------------------------
;; JSON-CLOS Prototypes
;; -----------------------------------------------------------------------------

(defclass json-rpc-request ()
  (method params id))

(defclass json-rpc-response ()
  (result error id))

;; -----------------------------------------------------------------------------
;; Misc
;; -----------------------------------------------------------------------------

(defvar *mouse-pos* (vector 0 0))

(defmethod to-chunk ((obj hash-table))
  "Convert a hashtable to ACT-R chunk"
  (let ((isa (gethash 'isa obj))
        (chunk '(ISA)))
    (push (read-from-string isa) chunk)
    (loop for k being the hash-key of obj do
          (if (not (equalp k 'isa))
              (let ((v (gethash k obj)))
                (push k chunk)
                (push v chunk))))
    (reverse chunk)))

;; -----------------------------------------------------------------------------
;; JSON-RPC Methods
;; -----------------------------------------------------------------------------

(json-rpc:defun-json-rpc
 actr.proc-display () :streaming
 ;(schedule-event-relative 0 'proc-display :priority :max)
 (format nil "{\"error\":0,\"result\":\"~A\"}~%" (schedule-event-relative 0 'proc-display :priority :max)))

(json-rpc:defun-json-rpc
 actr.run-indefinite () :streaming
 (format nil "{\"error\":0,\"result\":\"~A\"}~%"
         (bordeaux-threads:make-thread #'(lambda () (run 10)))))
         ;(bordeaux-threads:make-thread #'(lambda () (run-until-condition (lambda () nil))))))

;; -----------------------------------------------------------------------------
;; The JSON-RPC Device
;; -----------------------------------------------------------------------------

(defclass json-rpc-device ()
  ((rhost :initarg :rhost :accessor rhost)
   (rport :initarg :rport :accessor rport)
   (event-base-to :accessor event-base-to)
   (event-base-from :accessor event-base-from)
   (to-socket :accessor to-socket)
   (from-socket :accessor from-socket)
   (to-lock :accessor to-lock)
   (from-lock :accessor from-lock)
   (from-thread :accessor from-thread)
   (from-thread2 :accessor from-thread2)
   (init-lock :accessor init-lock)
   (init-cond :accessor init-cond)
   (connection :accessor connection)))

;; THIS IS VERY HACKISH RIGHT NOW
;;
;; Here is a general overview of what happens here:
;;
;;  1. Create a TCP socket connection with an external experiment which should
;;     already be waiting for a connection from ACT-R. This is a synchronous 
;;     connection is used for sending commands (like 'build-vis-locs-for') to 
;;     (and recieving the responses from) the external experiment.
;;
;;  2. Spawn a thread and wait for an incoming connection from the external
;;     experiment. This connection is also synchronous but is used by the
;;     external experiment to send commands (like 'proc-display') to ACT-R.  
;;
;;  3. Send a command to the external experiment to connect on this new TCP
;;     port.
;;
;;  4. Once both connections are established, return.
;;
;; Supposedly this is still buggy due to spurious wakeups. This should be
;; in some sort of loop like:
;; (with-mutex (...) (loop (if condition (return) (condition-wait cvar lock)))
(defmethod initialize-instance :after ((device json-rpc-device) &key)
  (setf (to-lock device) (bordeaux-threads:make-lock))
  (setf (from-lock device) (bordeaux-threads:make-lock))
  (setf (init-lock device) (bordeaux-threads:make-lock))
  (setf (init-cond device) (bordeaux-threads:make-condition-variable))
  (unwind-protect
    (progn
      (bordeaux-threads:acquire-lock (init-lock device) t)
      (handler-case
       (connect-to device)
       (iolib:socket-connection-refused-error ()
         (format t
                 "Connection refused to ~A:~A. Maybe the server isn't running?~%"
                 (lookup-hostname (remote-host device)) (remote-port device))))
      (bordeaux-threads:condition-wait (init-cond device) (init-lock device))
      (bordeaux-threads:acquire-lock (init-lock device) t)
      (handler-case
       (connect-from device))
      (bordeaux-threads:condition-wait (init-cond device) (init-lock device)))))

(defmethod ipc-request-to ((device json-rpc-device) message)
  (let (line)
    (bordeaux-threads:acquire-lock (to-lock device) t)
    (format (to-socket device) "~A~%" message)
    (finish-output (to-socket device))
    (setf line (read-line (to-socket device)))
    (bordeaux-threads:release-lock (to-lock device))
    line))

(defmethod connect-to ((device json-rpc-device))
  (setf (to-socket device) (iolib:make-socket :connect :active
                                              :address-family :internet
                                              :type :stream
                                              :external-format '(:utf-8 :eol-style :crlf)
                                              :ipv6 nil))
  (iolib:connect (to-socket device) (iolib:lookup-hostname (rhost device)) :port (rport device) :wait t)
  (format t "Connected to server ~A:~A from my local connection at ~A:~A!~%"
          (iolib:remote-name (to-socket device)) (iolib:remote-port (to-socket device))
          (iolib:local-name (to-socket device)) (iolib:local-port (to-socket device)))
  (bordeaux-threads:condition-notify (init-cond device)))

(defmethod handle-connection ((device json-rpc-device))
  (format t "A thread is handling the connection from ~A:~A!~%"
                 (rhost device) (iolib:local-port (from-socket device)))
  (loop
   (let* ((line (read-line (from-socket device)))
          (response (json-rpc:invoke-rpc line)))
     (format t "~A~%" response)
     (format (from-socket device) "~A~%" response)
     (finish-output (from-socket device)))))

(defmethod connect-from-thread ((device json-rpc-device))
  (setf (from-socket device) (iolib:make-socket :connect :passive
                                                :address-family :internet
                                                :type :stream
                                                :external-format '(:utf-8 :eol-style :crlf)
                                                :ipv6 nil))
  (format t "Created socket: ~A[fd=~A]~%" (from-socket device) (iolib:socket-os-fd (from-socket device)))
  (iolib:bind-address (from-socket device) iolib:+ipv4-loopback+ :port 0 :reuse-addr t)
  (format t "Bound socket: ~A~%" (from-socket device))
  (iolib:listen-on (from-socket device) :backlog 1)
  (format t "Listening on socket bound to: ~A:~A~%"
          (iolib:local-host (from-socket device))
          (iolib:local-port (from-socket device)))
  (ipc-request-to device (format nil "{\"method\":\"ipc.connect\",\"params\":[{\"host\":~S,\"port\":~A}]}~%"
                                 (iolib:address-to-string (iolib:local-host (from-socket device)))
                                 (iolib:local-port (from-socket device))))
  (format t "Waiting to accept a connection...~%")
  (setf (from-socket device) (iolib:accept-connection (from-socket device)))
  (bordeaux-threads:make-thread #'(lambda () (handle-connection device)))
  (bordeaux-threads:condition-notify (init-cond device)))

(defmethod connect-from ((device json-rpc-device))
  (setf (from-thread device) (bordeaux-threads:make-thread #'(lambda () (connect-from-thread device)))))

(defmethod disconnect ((device json-rpc-device))
  (format t "Disconnecting socket: ~A~%" (ipc-socket device))
  (close (ipc-socket device)))

;; -----------------------------------------------------------------------------
;; The generic ACT-R device methods defined
;; -----------------------------------------------------------------------------

(defmethod device-move-cursor-to ((device json-rpc-device) loc)
  (setf *mouse-pos* loc))

(defmethod get-mouse-coordinates ((device json-rpc-device))
  (format t "Get mouse coords~%")
  ;this is broken in my test app right now
  #|(let ((result (ipc-request-to device "{\"method\":\"actr.get-mouse-coordinates\"}~%")))
    (format t "~A~%" result))|#
  *mouse-pos*)

(defmethod device-handle-click ((device json-rpc-device))
  nil)

(defmethod device-handle-keypress ((device json-rpc-device) key)
  (format t "Key pressed: ~A!~%" key)
  (ipc-request-to device (format nil "{\"method\":\"actr.device-handle-keypress\",\"params\":[{\"key\":\"~A\"}]}~%" key)))

(defmethod device-speak-string ((device json-rpc-device) string)
  nil)

(defmethod cursor-to-vis-loc ((device json-rpc-device))
  nil)

(defmethod build-vis-locs-for ((device json-rpc-device) vis-mod)
  (json:with-decoder-simple-clos-semantics
   (let* ((json:*json-symbols-package* nil)
          (response (json:decode-json-from-string
                     (ipc-request-to device
                                  "{\"method\":\"actr.build-vis-locs-for\"}~%"))))
     (if (zerop (slot-value response 'error))
         (let ((chunks '()))
           (loop for x across (slot-value response 'result) do
                 (push (define-chunks-fct (list (to-chunk x))) chunks))
           chunks)
         nil))))

(defmethod vis-loc-to-obj ((device json-rpc-device) vis-loc)
  (json:with-decoder-simple-clos-semantics
   (let* ((json:*json-symbols-package* nil)
          (response (json:decode-json-from-string
                     (ipc-request-to device 
                                  (format nil "{\"method\":\"actr.vis-loc-to-obj\",\"params\":[{\"index\":~A}]}~%" (chunk-slot-value-fct vis-loc 'index))))))
     (if (zerop (slot-value response 'error))
         (car (define-chunks-fct (list (to-chunk (slot-value response 'result)))))
         nil))))

;; -----------------------------------------------------------------------------
;; Some helper methods that will be removed once testing is done
;; -----------------------------------------------------------------------------

(defun test-device (host port)
  (format t "========= initialize json-rpc-device begin =========~%")  
  (setf *ipc* (make-instance 'json-rpc-device :rhost host :rport port))
  (format t "========= initialize json-rpc-device end =========~%")
  (install-device *ipc*)
  (run 10)
  ;(proc-display)
  ;(run-until-condition (lambda () nil))
  )

(defun do-trials (trials)
  (ipc-request-to *ipc* (format nil "{\"method\":\"start\",\"params\":[{\"trials\":~A}]}~%" trials))
  t)

;; -----------------------------------------------------------------------------
;; A test model that will be removed once testing is done
;; -----------------------------------------------------------------------------

(clear-all)

(define-model json-rpc-device-test

  (chunk-type (visual-location-ext (:include visual-location)) index)
  (chunk-type (probe (:include visual-object)) status screen-x screen-y id size shape index)
  (chunk-type (shape (:include visual-object)) screen-x screen-y id size shape index)
  
  (start-hand-at-mouse)
  
  (p start
     ?goal>
     buffer empty
     ==>
     !output! (!!!START!!!)
     !eval! (do-trials 5)
     +visual-location>
     isa visual-location
     kind "probe"
     +goal>
     isa chunk
     )
  
  (p wait-for-probe
     =goal>
     isa chunk
     ?visual-location>
     buffer empty
     state error
     ==>
     +visual-location>
     isa visual-location
     kind "probe"
     )
  
  (p found-probe
     =goal>
     isa chunk
     =visual-location>
     isa visual-location
     kind "probe"
     ?visual>
     state free
     ==>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )
  
  (p attending-probe
     =goal>
     isa chunk
     =visual>
     isa probe
     id =id
     color =color
     size =size
     shape =shape
     ?manual>
     state free
     ==>
     !output! (Found probe id =id color =color size =size shape =shape)
     +goal>
     isa probe
     id =id
     color =color
     size =size
     shape =shape
     status 0
     +manual>
     ISA press-key
     key "f"
     )
  
  (p search-for-object
     =goal>
     isa probe
     id =id
     color =color
     status 0
     ?visual-location>
     buffer empty
     ==>
     +visual-location>
     isa visual-location
     kind "shape"
     color =color
     :attended nil
     )
  
  (p found-shape
     =goal>
     isa probe
     color =color
     status 0
     =visual-location>
     isa visual-location
     kind "shape"
     color =color
     ?visual>
     state free
     ==>
     =goal>
     status 1
     =visual-location>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )
  
  (p attending-shape-found
     =goal>
     isa probe
     id =id
     status 1
     =visual>
     isa shape
     id =sid
     id =id
     ==>
     !output! (Object =sid is probe =id)
     =goal>
     status 2)
  
  (p attending-shape-not-found
     =goal>
     isa probe
     id =id
     color =color
     status 1
     =visual>
     isa shape
     id =sid
     - id =id
     ==>
     !output! (Object =sid is not probe =id)
     =goal>
     status 0
     +visual-location>
     isa visual-location
     kind "shape"
     color =color
     :attended nil)
  
  )