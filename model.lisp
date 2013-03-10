(clear-all)

(define-model williams-task-model

  (sgp :v t :needs-mouse nil :process-cursor t)
  (sgp :jni-hostname "localhost" :jni-port 6666 :jni-sync t)
  ;(sgp :visual-num-finsts 48 :visual-finst-span 60)

  (sgp :er t)

  (sgp :bottom-up-act-w 1.1)
  (sgp :top-down-act-w 0.45)
  (sgp :vis-act-s 0.2)
  
  (sgp :fcolor-acuity-a 0.104)
  (sgp :fcolor-acuity-b 0.85)
  
  (sgp :fsize-acuity-a 0.14)
  (sgp :fsize-acuity-b 0.96)
  
  (sgp :fshape-acuity-a 0.142)
  (sgp :fshape-acuity-b 0.96)

  (chunk-type (probe-text (:include text)) abstract)
  (chunk-type task goal subgoal)
  (chunk-type probe fcolor fshape fsize id)
  (chunk-type feature-word word feature feature-kind)
  
  (add-dm
   
   (w67-red isa color-feature feature-name "w67-red")
   (w67-yellow isa color-feature feature-name "w67-yellow")
   (w67-green isa color-feature feature-name "w67-green")
   (w67-blue isa color-feature feature-name "w67-blue")
   
   (w67-oval isa shape-feature feature-name "w67-oval")
   (w67-star isa shape-feature feature-name "w67-star")
   (w67-crescent isa shape-feature feature-name "w67-crescent")
   (w67-cross isa shape-feature feature-name "w67-cross")
   
   (w67-small isa size-feature feature-name "w67-small")
   (w67-medium isa size-feature feature-name "w67-medium")
   (w67-large isa size-feature feature-name "w67-large")

   (word-red isa feature-word word "red" feature w67-red)
   (word-yellow isa feature-word word "yellow" feature w67-yellow)
   (word-green isa feature-word word "green" feature w67-green)
   (word-blue isa feature-word word "blue" feature w67-blue)

   (word-oval isa feature-word word "oval" feature w67-oval)
   (word-star isa feature-word word "star" feature w67-star)
   (word-crescent isa feature-word word "crescent" feature w67-crescent)
   (word-cross isa feature-word word "cross" feature w67-cross)

   (word-small isa feature-word word "small" feature w67-small)
   (word-medium isa feature-word word "medium" feature w67-medium)
   (word-large isa feature-word word "large" feature w67-large)

   )

  (start-hand-at-mouse)

  (p start-experiment
     ?goal>
     buffer empty
     ==>
     +goal>
     isa task
     goal "start"
     )

  (p start-trial?
     =goal>
     isa task
     goal "start"
     =visual-location>
     isa visual-location
     ==>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p starting-trial
     =goal>
     isa task
     goal "start"
     =visual>
     isa text
     value "Click mouse when ready!"
     ?manual>
     state free
     ==>
     +manual>
     isa click-mouse
     =goal>
     goal "study-probe"
     +imaginal>
     isa probe
     )

  (p attend-probe
     =goal>
     isa task
     goal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     ?visual>
     buffer empty
     =visual-location>
     isa visual-location
     kind probe-text
     ==>
     =imaginal>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p imagine-id
     =goal>
     isa task
     goal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     =visual>
     isa probe-text
     value =value
     abstract nil
     ?visual-location>
     state free
     ==>
     =imaginal>
     id =value
     +visual-location>
     isa visual-location
     kind probe-text
     :attended nil
     )

  (p retrieve-probe-component
     =goal>
     isa task
     goal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     =visual>
     isa probe-text
     value =value
     abstract t
     ==>
     =imaginal>
     +retrieval>
     isa feature-word
     word =value
     )

  (p retrieve-probe-feature
     =goal>
     isa task
     goal "study-probe"
     ?imaginal>
     state free
     =imaginal>
     isa probe
     =retrieval>
     isa feature-word
     feature =feature
     ==>
     =imaginal>
     +retrieval> =feature
     )

  (p* imagine-probe-feature
      =goal>
      isa task
      goal "study-probe"
      =imaginal>
      isa probe
      =retrieval>
      isa visual-feature
      slot-name =slot-name
      ?visual-location>
      state free
      ==>
      =imaginal>
      =slot-name =retrieval
      +visual-location>
      isa visual-location
      kind probe-text
      :attended nil
      )

  (p done-studying-probe
     =goal>
     isa task
     goal "study-probe"
     =imaginal>
     isa probe
     ?visual-location>
     state error
     ?manual>
     state free
     ==>
     -visual>
     -visual-location>
     -abstract-location>
     =imaginal>
     =goal>
     goal "search-wait"
     +manual>
     isa click-mouse
     )

  (p start-search
     =goal>
     isa task
     goal "search-wait"
     ?manual>
     state free
     ==>
     -visual>
     -visual-location>
     -abstract-location>
     =goal>
     goal "search"
     )

  (p attend-object
     =goal>
     isa task
     goal "search"
     =imaginal>
     isa probe
     =visual-location>
     isa visual-location
     kind visual-object
     ?visual>
     buffer empty
     state free
     ==>
     =imaginal>
     +visual>
     isa move-attention
     screen-pos =visual-location
     )

  (p found-target
     =goal>
     isa task
     goal "search"
     =imaginal>
     isa probe
     id =id
     =visual>
     isa visual-object
     value =id
     ==>
     !output! (OBJECT IS TARGET)
     =imaginal>
     =goal>
     goal "click-target"
     )
     
  (p not-target
     =goal>
     isa task
     goal "search"
     =imaginal>
     isa probe
     id =id
     fcolor =fcolor
     =visual>
     isa visual-object
     - value =id
     ==>
     !output! (OBJECT IS NOT TARGET)
     =imaginal>
     -visual>
     -visual-location>
     )

  (p search-by-color
     =goal>
     isa task
     goal "search"
     =imaginal>
     isa probe
     id =id
     fcolor =fcolor
     ?visual-location>
     buffer empty
     state free
     ==>
     =imaginal>
     +visual-location>
     isa visual-location
     fcolor =fcolor
     - kind probe-text
     :attended nil
     )
  
    (p search-by-size
     =goal>
     isa task
     goal "search"
     =imaginal>
     isa probe
     id =id
     fsize =fsize
     ?visual-location>
     buffer empty
     state free
     ==>
     =imaginal>
     +visual-location>
     isa visual-location
     fsize =fsize
     - kind probe-text
     :attended nil
     )

  (p search-by-shape
     =goal>
     isa task
     goal "search"
     =imaginal>
     isa probe
     id =id
     fshape =fshape
     ?visual-location>
     buffer empty
     state free
     ==>
     =imaginal>
     +visual-location>
     isa visual-location
     fshape =fshape
     - kind probe-text
     :attended nil
     )


)