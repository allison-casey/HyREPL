

def work_around_it(session, sessions, msg):
    hints[msg["code"]](session, sessions, msg)
    return


def work_around_fireplace(session, sessions, msg):
    session.write({"out": "success"})
    session.write({"value": "::/home/fox/.lein/self-installs/leiningen-2.3.4-standalone.jar", "ns": "Hy"})
    session.write({"status": ["done"]})
    return




hints = {'(do (println "success") (symbol (str (System/getProperty "path.separator") (System/getProperty "java.class.path"))))': work_around_fireplace}
