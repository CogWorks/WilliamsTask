(handler-case
    (asdf:load-system 'actr6)
  (error () #-:ACT-R-6.0 (load "~/workspace/actr6/load-act-r-6.lisp")))

(define-model williams-task-model

  (chunk-type probe feature1 feature2 feature3 id)

  (sgp :v t) 
  (sgp :needs-mouse nil :process-cursor t)
  (sgp :jni-hostname "localhost" :jni-port 6666)
  (start-hand-at-mouse)

  )
