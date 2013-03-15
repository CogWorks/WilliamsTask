(defmacro defp (&rest body)
  `(p-fct ',body))

(defmacro defp* (&rest body)
  `(p*-fct ',body))

(clear-all)

(define-model williams-task-model)

(sgp :v t :needs-mouse nil :process-cursor t)
(sgp :jni-hostname "localhost" :jni-port 6666 :jni-sync t)
(sgp :show-focus t)

(sgp :er t)

(sgp :eye-tracking t) ;; PAAV

(sgp :bottom-up-act-w 1.1) ;; PAAV
(sgp :top-down-act-w 0.45) ;; PAAV
(sgp :vis-act-s 0.2) ;; PAAV
  
(sgp :fcolor-acuity-a 0.104) ;; PAAV
(sgp :fcolor-acuity-b 0.85) ;; PAAV
  
(sgp :fsize-acuity-a 0.14) ;; PAAV
(sgp :fsize-acuity-b 0.96) ;; PAAV
  
(sgp :fshape-acuity-a 0.142) ;; PAAV
(sgp :fshape-acuity-b 0.96) ;; PAAV


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

(set-similarities
 (w67-small w67-medium .67)
 (w67-medium w67-large .67)
 (w67-small w67-large .33)
 
 (w67-oval w67-star .25)
 (w67-oval w67-crescent .25)
 (w67-oval w67-cross .25)
 (w67-star w67-crescent .25)
 (w67-star w67-cross .25)
 (w67-crescent w67-cross .25)
 
 (w67-red w67-yellow .8)
 (w67-red w67-green .6)
 (w67-red w67-blue .4)
 (w67-yellow w67-green .8)
 (w67-yellow w67-blue .6)
 (w67-green w67-blue .8)
 )
                  
(start-hand-at-mouse)
(set-gaze-loc-center) ;; PAAV 
(ready-the-eye) ;; PAAV

(defp **start-experiment
      ?goal> buffer empty
      ==>
      +goal> isa task goal "start"
      )

(defp **start-trial?
      =goal> isa task goal "start"
      ?abstract-location> buffer empty
      ==>
      +abstract-location> isa abstract-location
      )

(defp **start-trial!
      =goal> isa task goal "start"
      =abstract-location> isa abstract-location
      =visual-location> isa visual-location
      ==>
      +visual> isa move-attention screen-pos =visual-location
      )

(defp **starting-trial
      =goal> isa task goal "start"
      =visual> isa text value "Click mouse when ready!"
      ?manual> state free
      ==>
      +manual> isa click-mouse
      =goal> goal "study-probe"
      +imaginal> isa probe
      )

(defp **attend-probe
      =goal> isa task goal "study-probe"
      ?imaginal> state free
      =imaginal> isa probe
      ?visual> buffer empty
      =visual-location> isa visual-location kind probe-text
      ==>
      =imaginal>
      +visual> isa move-attention screen-pos =visual-location
      )

(defp **imagine-id
      =goal> isa task goal "study-probe"
      ?imaginal> state free
      =imaginal> isa probe
      =visual> isa probe-text value =value abstract nil
      ?visual-location> state free
      ==>
      =imaginal> id =value
      +visual-location> isa visual-location kind probe-text :attended nil
      )

(defp **retrieve-probe-component
      =goal> isa task goal "study-probe"
      ?imaginal> state free
      =imaginal> isa probe
      =visual> isa probe-text value =value abstract t
      ==>
      =imaginal>
      +retrieval> isa feature-word word =value
      )

(defp **retrieve-probe-feature
      =goal> isa task goal "study-probe"
      ?imaginal> state free
      =imaginal> isa probe
      =retrieval> isa feature-word feature =feature
      ==>
      =imaginal>
      +retrieval> =feature
      )

(defp* **imagine-probe-feature
       =goal> isa task goal "study-probe"
       =imaginal> isa probe
       =retrieval> isa visual-feature slot-name =slot-name
       ?visual-location> state free
       ==>
       =imaginal>
       =imaginal> =slot-name =retrieval
       +visual-location> isa visual-location kind probe-text :attended nil
       )

(defp **done-studying-probe
      =goal> isa task goal "study-probe"
      =imaginal> isa probe
      ?visual-location> state error
      ?manual> state free
      ==>
      -visual>
      -visual-location>
      -abstract-location>
      =imaginal>
      =goal> goal "search-wait"
      +manual> isa click-mouse
      )

(defp **start-search
      =goal> isa task goal "search-wait"
      ?manual> state free
      ==>
      -visual>
      -visual-location>
      -abstract-location>
      =goal> goal "search"
      )

(defp **attend-object
      =goal> isa task goal "search"
      =imaginal> isa probe
      =abstract-location> isa abstract-location kind visual-object
      =visual-location> isa visual-location
      ?visual> buffer empty state free
      ==>
      =imaginal>
      +visual> isa move-attention screen-pos =visual-location
      )

(defp **found-target
      =goal> isa task goal "search"
      =imaginal> isa probe id =id
      =visual> isa visual-object value =id screen-pos =screen-pos
      ==>
      !output! (OBJECT IS TARGET)
      =imaginal>
      =goal> goal "move-mouse"
      +visual> isa move-attention screen-pos =screen-pos
      )

(defp **attend-target
      =goal> isa task goal "move-mouse"
      =imaginal> isa probe id =id
      =visual> isa visual-object value =id screen-pos =screen-pos
      ?manual> state free
      ==>
      =imaginal>
      =visual>
      +manual> isa move-cursor loc =screen-pos
      =goal> goal "click-target"
      )

(defp **click-target
      =goal> isa task goal "click-target"
      =imaginal> isa probe id =id
      =visual> isa visual-object value =id screen-pos =screen-pos
      ?manual> state free
      ==>
      +manual> isa click-mouse
      -goal>
      )

(defp **not-target
      =goal> isa task goal "search"
      =imaginal> isa probe id =id
      =visual> isa visual-object - value =id
      ==>
      !output! (OBJECT IS NOT TARGET)
      =imaginal>
      -visual>
      -visual-location>
      )

(defp **search-by-color
      =goal> isa task goal "search"
      =imaginal> isa probe id =id fcolor =fcolor
      ?visual-location> buffer empty state free
      ==>
      =imaginal>
      +abstract-location> isa abstract-location fcolor =fcolor - kind probe-text :attended nil :nearest current
      )

(defp **search-by-size
      =goal> isa task goal "search"
      =imaginal> isa probe id =id fsize =fsize
      ?visual-location> buffer empty state free
      ==>
      =imaginal>
      +abstract-location> isa abstract-location fsize =fsize - kind probe-text :attended nil :nearest current
      )

(defp **search-by-shape
      =goal> isa task goal "search"
      =imaginal> isa probe id =id fshape =fshape
      ?visual-location> buffer empty state free
      ==>
      =imaginal>
      +abstract-location> isa abstract-location fshape =fshape - kind probe-text :attended nil :nearest current
      )