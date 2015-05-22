def work_around_it(session, msg, transport):
    def wfn(m):
        m["id"] = msg["id"]
        session.write(m, transport)
    hints[msg["code"]](session, msg, wfn)

def work_around_fireplace_1(session, msg, w):
    w({"out": "success"})
    w({"value": "::/home/fox/.lein/self-installs/leiningen-2.3.4-standalone.jar", "ns": "Hy"})
    w({"status": ["done"]})

def work_around_fireplace_2(session, msg, w):
    w({"out": "success"})
    w({"value": "[\"/\" \"::/home/fox/.lein/self-installs/leiningen-2.3.4-standalone.jar\"]", "ns": "Hy"})
    w({"status": ["done"]})

hints = {'(do (println "success") (symbol (str (System/getProperty "path.separator") ' +
        '(System/getProperty "java.class.path"))))': work_around_fireplace_1,
        '[(System/getProperty "path.separator") (System/getProperty "java.class.path")]': work_around_fireplace_2
        }
