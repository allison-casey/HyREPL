(import [HyREPL.ops [ops]])
(require [HyREPL.ops [*]])

(defop test [s m t]
       {"doc" "Test operation"
        "requires" {}
        "optional" {}
        "returns" {"test" "Test string"}}
        (.write s {"status" ["done"]
                   "id" (.get m "id")
                   "test" "Here be dragons"}
                   t))
