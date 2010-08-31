(asdf:load-system 'actr6.extras.emma)

(clear-all)

(define-model json-rpc-device-test
  
  (sgp
   :v t
   :needs-mouse nil
   :process-cursor t
   :incremental-mouse-moves nil 
   :cursor-noise nil
   :esc t
   :er t)
  
  (register-slot-availability-function 'color 'color-availability!)
  (register-slot-availability-function 'shape-t 'shape-availability!)
  (register-slot-availability-function 'size-t 'size-availability!)
  
  (chunk-type (probe (:include visual-object)) status id color size shape)
  (chunk-type (shape-loc (:include visual-location)) shape-t size-t)
  (chunk-type (shape (:include visual-object)) id)
  
  (start-hand-at-mouse)
  
  (p start
     ?goal>
     buffer empty
     ==>
     +visual-location>
     isa visual-location
     kind PROBE
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
     kind PROBE
     )
  
  (p found-probe
     =goal>
     isa chunk
     =visual-location>
     isa visual-location
     kind PROBE
     ?visual>
     state free
     ?visual>
     preparation free
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
  
  (p search-for-exact-probe
     =goal>
     isa probe
     id =id
     color =color
     size =size
     shape =shape
     status 0
     ?visual-location>
     buffer empty
     ==>
     +visual-location>
     isa shape-loc
     color =color
     size-t =size
     shape-t =shape
     :attended nil
     )
  
  (p search-for-probe-color
     =goal>
     isa probe
     status 0
     color =color
     ?visual-location>
     buffer empty
     ==>
     +visual-location>
     isa shape-loc
     color =color
     :attended nil
     )
  
  (p found-shape
     =goal>
     isa probe
     status 0
     =visual-location>
     isa shape-loc
     ?visual>
     state free
     preparation free
     ==>
     !eval! (incf *fixations*)
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
     screen-pos =visual-location
     ==>
     !output! (Object =sid is probe =id)
     =goal>
     status 2
     screen-pos =visual-location
     +visual-location>
     isa visual-location
     kind CURSOR
     +retrieval>
     isa cursor
     )
  
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
     isa shape-loc
     color =color
     :attended nil
     )
  
  (p found-cursor-loc
     =goal>
     isa probe
     id =id
     status 2
     =visual-location>
     isa visual-location
     kind CURSOR
     ?visual>
     preparation free
     ==>
     !output! (Cursor-loc found)
     =goal>
     status 3
     +visual>
     isa move-attention
     screen-pos =visual-location
     )
  
  (p attending-cursor-loc
     =goal>
     isa probe
     id =id
     status 3
     screen-pos =visual-location
     =visual>
     isa CURSOR
     ?manual>
     state free
     ?visual>
     preparation free
     ==>
     !output! (Attending cursor)
     !output! (Move attention and cursor to target)
     =goal>
     status 4
     +visual>
     isa move-attention
     screen-pos =visual-location
     +manual>
     isa move-cursor
     loc =visual-location
     )
  
  (p click-mouse
     =goal>
     isa probe
     status 4
     screen-pos =visual-location
     ?manual>
     state free
     =visual>
     isa shape
     screen-pos =visual-location     
     ==>
     !output! (Clicking on target)
     =goal>
     status 5
     +manual>
     isa click-mouse)
  
  (p found-cursor-obj
     =goal>
     isa probe
     id =id
     status 2
     =retrieval>
     isa cursor
     ==>
     !output! (Cursor-obj found)
     =goal>
     status 3
     )
  
  )

;; -----------------------------------------------------------------------------
;; Some helper methods that will be removed once testing is done
;; -----------------------------------------------------------------------------

(defun print-visicon2 ()
  "Print the Vision Module's visicon. For debugging."
  (awhen (get-module :vision)  ;; Test that there is a vision module
    (update-new it)
    (check-finsts it) 
    (command-output "Loc        Att   Kind           Size              Shape             Color           ID")
    (command-output "---------  ---   -------------  ----------------  ----------------  --------------  -------------")
    
    (mapcar 'print-icon-feature2 (visicon-chunks it t))
    nil))

(defun print-icon-feature2 (chunk)
  (command-output "(~3D ~3D)~11T~A~17T~A~32T~S~50T~A~66T~A~82T~A"
                  (chunk-slot-value-fct  chunk 'screen-x) 
                  (chunk-slot-value-fct  chunk 'screen-y) 
                  (feat-attended chunk (get-module :vision))
                  (chunk-slot-value-fct  chunk 'kind)
                  (chunk-slot-value-fct chunk 'size-t)
                  (chunk-slot-value-fct chunk 'shape-t)
                  (chunk-slot-value-fct  chunk 'color) 
                  (chunk-visicon-entry chunk)))

(defun test-device (host port)
  (setf *fixations* 0)
  #+emma
  (let ((device (make-instance 'json-rpc-device :host host :port port)))
    (install-device device)
    (run-device device 1)
    (set-eye-loc (get-module :vision) (vector
                                       (/ (aref (screen-res device) 0) 2)
                                       (/ (aref (screen-res device) 1) 2)))
    (proc-display)
    (run 20 :real-time t))
  #-emma
  (warn "EMMA module not loaded"))