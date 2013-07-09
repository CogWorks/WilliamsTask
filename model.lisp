(defun simple-size (vis-loc)
  (let ((w (chunk-slot-value-fct vis-loc 'width))
        (h (chunk-slot-value-fct vis-loc 'height)))
    (when (and (numberp w) (numberp h))
      (* (round 
          (sqrt (+ (* (pm-pixels-to-angle w) (pm-pixels-to-angle w))
                   (* (pm-pixels-to-angle h) (pm-pixels-to-angle h)))) .01) .01))))

(defun get-vis-loc-center (x-loc y-loc width height)
  (list x-loc y-loc))

(defun set-fval-dissim (feature-val-one feature-val-two dissim)
  (setf (gethash (create-fval-dissim-ht-key feature-val-one feature-val-two) (fval-dissim-ht (get-module :vision))) dissim))

(defmacro defp (&rest body)
  `(p-fct ',body))

(defmacro defp* (&rest body)
  `(p*-fct ',body))

(defun run-until-break (&key (real-time nil))
  (run-until-condition (lambda () nil) :real-time real-time))

(defparameter **trials** '())
(defparameter **trial-stats** '(0 0 0 0 0))

(defun get-trial-id (probe-shape probe-color probe-size)
  (+
   (if (tornil probe-shape) 0 4)
   (if (tornil probe-color) 0 2)
   (if (tornil probe-size) 0 1)))    

(defun tabulate-fixation (probe-shape probe-color probe-size obj-shape obj-color obj-size)
  (incf (second **trial-stats**))
  (when (and probe-size (equal probe-size obj-size)) (incf (third **trial-stats**)))
  (when (and probe-color (equal probe-color obj-color)) (incf (fourth **trial-stats**)))
  (when (and probe-shape (equal probe-shape obj-shape)) (incf (fifth **trial-stats**))))

(clear-all)

(define-model williams-task-model)

(jni-register-event-hook :trial-complete (lambda () (schedule-break-after-all)))
;(jni-register-event-hook :exp-complete (lambda () (schedule-break-after-all)))
;(jni-register-event-hook :break (lambda () (schedule-break-after-all)))


(sgp :v t :needs-mouse nil :process-cursor t :trace-mouse nil)

(sgp :jni-hostname "localhost" :jni-port 6666 :jni-sync t)

(sgp :show-focus t :show-gaze t)

(sgp :viewing-distance 26)

(sgp :er t :esc t :ul t)

(sgp :eye-tracking nil)

(sgp :md 0 :ms 1)

(sgp :bottom-up-act-w 1.1)
(sgp :top-down-act-w 0.45)
(sgp :vis-act-s 0.2)

(sgp :fcolor-acuity-a 0.84)
(sgp :fcolor-acuity-b 0.65)

(sgp :fshading-acuity-a 0.147)
(sgp :fshading-acuity-b 0.96)

(sgp :fsize-acuity-a 0.14)
(sgp :fsize-acuity-b 0.96)

(sgp :fshape-acuity-a 0.142)
(sgp :fshape-acuity-b 0.96)

(sgp :fcolor-sim-w 100)
(sgp :fshape-sim-w 10)

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

 (w67-null isa visual-feature feature-name "null")
 
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
 
 #|(w67-oval w67-star .25)
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
 (w67-green w67-blue .8)|#
 )
                  
(start-hand-at-mouse)
(set-gaze-loc-center) 
(ready-the-eye)

(defp **start-experiment
      ?goal> buffer empty
      ==>
      +goal> isa task goal "start"
      )

(defp **start-trial?
      =goal> isa task goal "start"
      ?visual-location> buffer empty state free
      ==>
      +visual-location> isa visual-location kind visual-object :attended new
      )

(defp **start-trial!
      =goal> isa task goal "start"
      =visual-location> isa visual-location kind visual-object
      ?visual> state free buffer empty
      ==>
      =visual-location>
      +visual> isa move-attention screen-pos =visual-location
      )

(defp **starting-trial
      =goal> isa task goal "start"
      =visual> isa visual-object value "Click mouse when ready!"
      ?manual> state free
      ?visual> state free
      ==>
      -visual>
      -visual-location>
      -abstract-location>
      +manual> isa click-mouse
      =goal> goal "study-probe"
      +imaginal> isa probe fshape w67-null fcolor w67-null fsize w67-null
      )

(defp **find-first-probe-component
      =goal> isa task goal "study-probe"
      ?imaginal> state free
      =imaginal> isa probe id nil fcolor w67-null fshape w67-null fsize w67-null
      ?visual> state free buffer unrequested
      ?visual-location> state free buffer unrequested
      ?manual> state free
      ==>
      =imaginal>
      +visual-location> isa visual-location kind probe-text screen-y lowest
      )

(defp **attend-probe
      =goal> isa task goal "study-probe"
      ?imaginal> state free
      =imaginal> isa probe
      ?visual-location> state free buffer requested
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
      =goal> goal "search-wait"
      +manual> isa click-mouse
      )

(defp **retrieve-probe-component
      =goal> isa task goal "study-probe"
      ?imaginal> state free
      =imaginal> isa probe
      ?visual> buffer requested
      =visual> isa probe-text value =value abstract t
      ?retrieval> state free
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
       =imaginal> =slot-name =retrieval
       +visual-location> isa visual-location kind probe-text :nearest current :attended nil
       -visual>
       )

(defp **start-search
      =goal> isa task goal "search-wait"
      ?manual> state free
      ?visual> state free
      =imaginal> isa probe id =id fshape =probe-shape fcolor =probe-color fsize =probe-size
      ==>
      !eval! (progn (setf **trial-stats** (list (get-trial-id =probe-shape =probe-color =probe-size) 0 0 0 0)) t)
      =imaginal>
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
      =imaginal> isa probe id =id fshape =probe-shape fcolor =probe-color fsize =probe-size
      =visual> isa visual-object value =id screen-pos =screen-pos fshape =obj-shape fcolor =obj-color fsize =obj-size
      ==>
      !output! (OBJECT IS TARGET)
      !eval! (progn (tabulate-fixation =probe-shape =probe-color =probe-size =obj-shape =obj-color =obj-size) t)
      !eval! (progn (print-warning "~S" **trial-stats**) t)
      !eval! (progn (pushnew **trial-stats** **trials**) t)
      =imaginal>
      =goal> goal "move-mouse"
      +visual> isa move-attention screen-pos =screen-pos
      )

(defp **not-target
      =goal> isa task goal "search"
      =imaginal> isa probe id =id fshape =probe-shape fcolor =probe-color fsize =probe-size
      =visual> isa visual-object - value =id fshape =obj-shape fcolor =obj-color fsize =obj-size
      ==>
      !output! (OBJECT IS NOT TARGET)
      !eval! (progn (tabulate-fixation =probe-shape =probe-color =probe-size =obj-shape =obj-color =obj-size) t)
      =imaginal>
      -visual>
      -visual-location>
      )

(defp **attend-target
      =goal> isa task goal "move-mouse"
      =imaginal> isa probe
      =visual> isa visual-object screen-pos =screen-pos
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
      =imaginal>
      +manual> isa click-mouse
      =goal> goal "clicking-target"
      )

(defp **clicked-target
      =goal> isa task goal "clicking-target"
      ?manual> state free
      ==>
      !eval! (progn (purge-abstract-locations (get-module :vision)) t)
      -goal>
      -imaginal>
      -visual>
      -visual-location>
      -abstract-location>
      )

#|
(defp **search-by-color
      =goal> isa task goal "search"
      =imaginal> isa probe fcolor =fcolor fshape =fshape fsize =fsize
      ?visual> state free
      ?visual-location> buffer empty state free
      ?abstract-location> - state error state free
      ==>
      =imaginal>
      +abstract-location> isa abstract-location - kind probe-text fcolor =fcolor :attended nil :nearest current
      )
|#

(defp **search-by-all-features
      =goal> isa task goal "search"
      =imaginal> isa probe fcolor =fcolor fshape =fshape fsize =fsize
      ?visual> state free
      ?visual-location> buffer empty state free
      ?abstract-location> - state error state free
      ==>
      =imaginal>
      +abstract-location> isa abstract-location - kind probe-text fcolor =fcolor fshape =fshape fsize =fsize :attended nil :nearest current
      )