(clear-all)

(define-model williams-task-model

  (sgp :v t) 
  (sgp :needs-mouse nil :process-cursor t)
  (sgp :jni-hostname "localhost" :jni-port 6666)

  (chunk-type task subgoal)
  (chunk-type (probe-txt-color (:include text)))
  (chunk-type (probe-txt-shape (:include text)))
  (chunk-type (probe-txt-size (:include text)))
  (chunk-type (probe-txt-id (:include text)))
  (chunk-type probe color shape size id)
  (chunk-type (object (:include visual-object)) tshape tsize id)

  (start-hand-at-mouse)

  (p start-trial-1a
     ?goal>
     buffer empty
     ?visual-location>
     buffer empty
     ==>
     +visual-location>
     isa visual-location
     kind text
     )

  (p start-trial-1b
     ?goal>
     buffer empty
     =visual-location>
     isa visual-location
     - kind text
     ==>
     +visual-location>
     isa visual-location
     kind text
     )

  (p start-trial-2
     ?goal>
     buffer empty
     =visual-location>
     isa visual-location
     kind text
     ?visual>
     state free
     ==>
     +visual>
     isa move-attention
     screen-pos =visual-location
     +goal>
     isa task
     subgoal "attend-start"
     )

  (p start-trial-3
     =goal>
     isa task
     subgoal "attend-start"
     =visual>
     isa text
     value "Click mouse when ready!"
     ?manual>
     state free
     ==>
     +manual>
     isa click-mouse
     =goal>
     subgoal "start-clicked"
     )

  (p start-trial-4
     =goal>
     isa task
     subgoal "start-clicked"
     ?manual>
     state free
     ==>
     =goal>
     subgoal "study-probe"
     +imaginal>
     isa probe
     )

  (p study-probe-color
     =goal>
     isa task
     subgoal "study-probe"
     =imaginal>
     isa probe
     color nil
     ?visual-location>
     state free
     ==>
     =imaginal>
     =goal>
     subgoal "study-probe-attend"
     +visual-location>
     isa visual-location
     kind probe-txt-color
     )

  (p study-probe-attend-color
     =goal>
     isa task
     subgoal "study-probe-attend"
     =imaginal>
     isa probe
     color nil
     =visual-location>
     isa visual-location
     kind probe-txt-color
     ?visual>
     state free
     ==>
     =imaginal>
     =goal>
     subgoal "study-probe-attending"
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p study-probe-attending-color
     =goal>
     isa task
     subgoal "study-probe-attending"
     =imaginal>
     isa probe
     color nil
     =visual>
     isa visual-location
     kind probe-txt-color
     value =val
     ==>
     =goal>
     subgoal "study-probe"
     =imaginal>
     color =val
     )


)

#|


  (p study-probe-shape
     =goal>
     isa task
     subgoal "study-probe"
     =imaginal>
     isa probe
     shape nil
     ?visual-location>
     state free
     ==>
     =imaginal>
     +visual-location>
     isa visual-location
     kind probe-txt-shape
     =goal>
     subgoal "study-probe-attend"
     )

  (p study-probe-size
     =goal>
     isa task
     subgoal "study-probe"
     =imaginal>
     isa probe
     size nil
     ?visual-location>
     state free
     ==>
     =imaginal>
     +visual-location>
     isa visual-location
     kind probe-txt-size
     =goal>
     subgoal "study-probe-attend"
     )

  (p study-probe-id
     =goal>
     isa task
     subgoal "study-probe"
     =imaginal>
     isa probe
     id nil
     ?visual-location>
     state free
     ==>
     =imaginal>
     +visual-location>
     isa visual-location
     kind probe-txt-id
     =goal>
     subgoal "study-probe-attend"
     )

  (p study-probe-attend-shape
     =goal>
     isa task
     subgoal "study-probe-attend"
     =visual-location>
     isa probe-txt-shape
     ?visual>
     buffer empty
     ==>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p study-probe-attending-shape
     =goal>
     isa task
     subgoal "study-probe-attend"
     =imaginal>
     isa probe
     =visual>
     isa probe-txt-shape
     value =val
     ==>
     =imaginal>
     shape =val
     =goal>
     subgoal "study-probe"
     )

  (p study-probe-attend-size
     =goal>
     isa task
     subgoal "study-probe-attend"
     =visual-location>
     isa probe-txt-size
     ?visual>
     buffer empty
     ==>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p study-probe-attending-size
     =goal>
     isa task
     subgoal "study-probe"
     =imaginal>
     isa probe
     ?visual>
     state free
     =visual>
     isa probe-txt-size
     value =val
     ==>
     =imaginal>
     size =val
     =goal>
     subgoal "study-probe"
     )

  (p study-probe-attend-id
     =goal>
     isa task
     subgoal "study-probe-attend"
     =visual-location>
     isa probe-txt-id
     ?visual>
     buffer empty
     ==>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p study-probe-attending-id
     =goal>
     isa task
     subgoal "study-probe"
     =imaginal>
     isa probe
     ?visual>
     state free
     =visual>
     isa probe-txt-id
     value =val
     ==>
     =imaginal>
     id =val
     =goal>
     subgoal "study-probe"
     )















  (p study-probe-2b
     =goal>
     isa start-trial
     status "clicked"
     ?manual>
     state free
     =visual-location>
     isa visual-location
     kind probe-txt-shape
     ?visual>
     state free
     ==>
     +visual>
     isa move-attention
     screen-pos =visual-location
     +goal>
     isa study-probe
     )

  (p study-probe-2c
     =goal>
     isa start-trial
     status "clicked"
     ?manual>
     state free
     =visual-location>
     isa visual-location
     kind probe-txt-size
     ?visual>
     state free
     ==>
     +visual>
     isa move-attention
     screen-pos =visual-location
     +goal>
     isa study-probe
     )

  (p study-probe-2d
     =goal>
     isa start-trial
     status "clicked"
     ?manual>
     state free
     =visual-location>
     isa visual-location
     kind probe-txt-id
     ?visual>
     state free
     ==>
     +visual>
     isa move-attention
     screen-pos =visual-location
     +goal>
     isa study-probe
     )

  (p study-probe-3-color
     =goal>
     isa study-probe
     color nil
     =visual>
     isa probe-txt-color
     value =val
     ==>
     =visual>
     =goal>
     color =val
     )

  (p study-probe-3-shape
     =goal>
     isa study-probe
     shape nil
     =visual>
     isa probe-txt-shape
     value =val
     ==>
     =visual>
     =goal>
     shape =val
     )

  (p study-probe-3-size
     =goal>
     isa study-probe
     size nil
     =visual>
     isa probe-txt-color
     value =val
     ==>
     =visual>
     =goal>
     size =val
     )

  (p study-probe-3-id
     =goal>
     isa study-probe
     id nil
     =visual>
     isa probe-txt-color
     value =val
     ==>
     =visual>
     =goal>
     id =val
     )

  (p study-probe-4
     =goal>
     isa study-probe
     - color nil
     color =color
     - shape nil
     shape =shape
     - size nil
     size =size
     - id nil
     id =id
     ?manual>
     preparation free
     ==>
     +manual>
     isa click-mouse
     +goal>
     isa search
     color =color
     shape =shape
     size =size
     id =id
     )

  (p search-1a
     =goal>
     isa search
     color =color
     ?visual>
     buffer empty
     ==>
     +visual-location>
     isa visual-location
     kind object
     color =color
  )

  (p search-1b
     =goal>
     isa search
     color =color
     =visual>
     isa object
     - color =color
     ==>
     +visual-location>
     isa visual-location
     kind object
     color =color
  )

  (p search-2
     =goal>
     isa search
     color =color
     id =id
     =visual>
     isa object
     color =color
     id =id
     screen-pos =location
     ?manual>
     preparation free
     ==>
     +goal>
     isa found
     +manual>
     isa move-cursor
     loc =location
     )
|#