(clear-all)

(define-model williams-task-model

  (sgp :v t :needs-mouse nil :process-cursor t)
  (sgp :jni-hostname "localhost" :jni-port 6666 :jni-sync t)
  (sgp :visual-num-finsts 48 :visual-finst-span 60)

  (chunk-type task subgoal)
  (chunk-type (probe-txt-color (:include text)))
  (chunk-type (probe-txt-shape (:include text)))
  (chunk-type (probe-txt-size (:include text)))
  (chunk-type (probe-txt-id (:include text)))
  (chunk-type probe color shape size id)
  (chunk-type (object (:include visual-object)) tshape tsize id)

  (start-hand-at-mouse)

  (p start-trial-0
     ?goal>
     buffer empty
     ==>
     -visual>
     -visual-location>
     -imaginal>
     +goal>
     isa task
     subgoal "start"
     )

  (p start-trial-1
     =goal>
     isa task
     subgoal "start"
     ?visual-location>
     buffer empty
     state free
     ?visual>
     buffer empty
     state free
     ==>
     =goal>
     +visual-location>
     isa visual-location
     kind text
     )


  (p start-trial-2
     =goal>
     isa task
     subgoal "start"
     =visual-location>
     isa visual-location
     kind text
     ?visual>
     buffer empty
     state free
     ==>
     =goal>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )


  (p start-trial-3
     =goal>
     isa task
     subgoal "start"
     =visual>
     isa text
     value "Click mouse when ready!"
     ?manual>
     state free
     ==>
     -visual>
     -visual-location>
     +manual>
     isa click-mouse
     =goal>
     subgoal "study-probe"
     )

  (p study-probe-0
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     buffer empty
     state free
     ?manual>
     state free
     ==>
     =goal>
     -visual>
     -visual-location>
     +imaginal>
     isa probe
     )

  (p study-probe-1-color
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     color nil
     ?visual-location>
     buffer empty
     state free
     ?visual>
     buffer empty
     state free
     ==>
     =imaginal>
     =goal>
     +visual-location>
     isa visual-location
     kind probe-txt-color
     )

  (p study-probe-2-color
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     color nil
     ?visual-location>
     state free
     =visual-location>
     isa visual-location
     kind probe-txt-color
     ?visual>
     state free
     buffer empty
     ==>
     =imaginal>
     =goal>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p study-probe-3-color
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     color nil
     ?visual-location>
     state free
     ?visual>
     state free
     =visual>
     isa probe-txt-color
     value =color
     ==>
     =imaginal>
     color =color
     =goal>
     -visual>
     -visual-location>
     )

  (p study-probe-1-shape
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     shape nil
     ?visual-location>
     buffer empty
     state free
     ?visual>
     buffer empty
     state free
     ==>
     =imaginal>
     =goal>
     +visual-location>
     isa visual-location
     kind probe-txt-shape
     )

  (p study-probe-2-shape
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     shape nil
     ?visual-location>
     state free
     =visual-location>
     isa visual-location
     kind probe-txt-shape
     ?visual>
     state free
     buffer empty
     ==>
     =imaginal>
     =goal>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p study-probe-3-shape
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     shape nil
     ?visual-location>
     state free
     ?visual>
     state free
     =visual>
     isa probe-txt-shape
     value =shape
     ==>
     =imaginal>
     shape =shape
     =goal>
     -visual>
     -visual-location>
     )

  (p study-probe-1-size
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     size nil
     ?visual-location>
     buffer empty
     state free
     ?visual>
     buffer empty
     state free
     ==>
     =imaginal>
     =goal>
     +visual-location>
     isa visual-location
     kind probe-txt-size
     )

  (p study-probe-2-size
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     size nil
     ?visual-location>
     state free
     =visual-location>
     isa visual-location
     kind probe-txt-size
     ?visual>
     state free
     buffer empty
     ==>
     =imaginal>
     =goal>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p study-probe-3-size
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     size nil
     ?visual-location>
     state free
     ?visual>
     state free
     =visual>
     isa probe-txt-size
     value =size
     ==>
     =imaginal>
     size =size
     =goal>
     -visual>
     -visual-location>
     )

    (p study-probe-1-id
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     id nil
     ?visual-location>
     buffer empty
     state free
     ?visual>
     buffer empty
     state free
     ==>
     =imaginal>
     =goal>
     +visual-location>
     isa visual-location
     kind probe-txt-id
     )

  (p study-probe-2-id
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     id nil
     ?visual-location>
     state free
     =visual-location>
     isa visual-location
     kind probe-txt-id
     ?visual>
     state free
     buffer empty
     ==>
     =imaginal>
     =goal>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p study-probe-3-id
     =goal>
     isa task
     subgoal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     id nil
     ?visual-location>
     state free
     ?visual>
     state free
     =visual>
     isa probe-txt-id
     value =id
     ==>
     =imaginal>
     id =id
     =goal>
     -visual>
     -visual-location>
     )

  (p study-probe-4
     =goal>
     isa task
     subgoal "study-probe"
     =imaginal>
     isa probe
     - color nil
     - shape nil
     - size nil
     - id nil
     ?manual>
     state free
     ==>
     =imaginal>
     =goal>
     subgoal "search"
     +manual>
     isa click-mouse
     )

  (p search-1-color
     =goal>
     isa task
     subgoal "search"
     =imaginal>
     isa probe
     color =color
     ?visual-location>
     buffer empty
     state free
     ?visual>
     buffer empty
     state free
     ==>
     =imaginal>
     =goal>
     +visual-location>
     isa visual-location
     kind object
     color =color
     :attended nil
     )

  (p search-2-color
     =goal>
     isa task
     subgoal "search"
     =imaginal>
     isa probe
     color =color
     ?visual-location>
     state free
     =visual-location>
     isa visual-location
     kind object
     - color =color
     value =value
     ?visual>
     buffer empty
     state free
     ==>
     !output! (ID of visual-location is =value)
     =imaginal>
     =goal>
     +visual-location>
     isa visual-location
     kind object
     color =color
     :attended nil
     )

  (p search-3-color
     =goal>
     isa task
     subgoal "search"
     =imaginal>
     isa probe
     color =color
     ?visual-location>
     state free
     =visual-location>
     isa visual-location
     kind object
     color =color
     value =value
     ?visual>
     buffer empty
     state free
     ==>
     !output! (ID of visual-location is =value)
     =imaginal>
     =goal>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p search-4-color-found-target
     =goal>
     isa task
     subgoal "search"
     =imaginal>
     isa probe
     id =id
     ?visual>
     state free
     =visual>
     isa object
     id =id
     screen-pos =pos
     ?manual>
     state free
     ==>
     !output! "FOUND TARGET"
     =goal>
     subgoal "click"
     +manual>
     isa move-cursor
     loc =pos
     =imaginal>
     =goal>
     )

  (p search-4-color-not-target
     =goal>
     isa task
     subgoal "search"
     =imaginal>
     isa probe
     id =id
     ?visual>
     state free
     =visual>
     isa object
     - id =id
     ==>
     !output! "NOT TARGET"
     =imaginal>
     =goal>
     -visual>
     -visual-location>
     )
    
  (p click-1
     =goal>
     isa task
     subgoal "click"
     ?manual>
     state free
     ==>
     +manual>
     isa click-mouse
     -goal>
     -visual>
     -visual-location>
     -imaginal>
     )
  
)