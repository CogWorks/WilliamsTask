(clear-all)

(define-model json-rpc-device-test
  
  (sgp
   :v t
   :needs-mouse nil
   :process-cursor t
   :incremental-mouse-moves nil 
   :cursor-noise nil
   :esc t
   :bll .5 
   :ol t 
   :er t 
   :ncnar nil 
   :lf 0 
   :rt -60
   :ans .2
   :mp 10.0)
  
  (chunk-type (probe (:include visual-object)) status id color size shape)
  (chunk-type (shape (:include visual-object)) id color size shape)
  
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
     kind SHAPE
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
     kind SHAPE
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
     isa visual-location
     kind SHAPE
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

(defun test-device (host port)
  (install-device (make-instance 'json-rpc-device :host host :port port))
  (run-device (current-device) 1)
  (proc-display)
  (run 20 :real-time t))