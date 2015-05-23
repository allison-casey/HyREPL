import traceback

def work_around_it(session, msg, transport):
    def wfn(m):
        m["id"] = msg["id"]
        session.write(m, transport)
    hints[msg["code"]](session, msg, wfn)

def work_around_init_1(session, msg, w):
    w({"out": "success"})
    w({"value": "::/home/fox/.lein/self-installs/leiningen-2.3.4-standalone.jar", "ns": "Hy"})
    w({"status": ["done"]})

def work_around_init_2(session, msg, w):
    w({"out": "success"})
    w({"value": "[\"/\" \"::/home/fox/.lein/self-installs/leiningen-2.3.4-standalone.jar\"]", "ns": "Hy"})
    w({"status": ["done"]})

def work_around_traceback(session, msg, w):
    # function(file:line)
    w({"out": "success"})
    items = []
    for fname, line, func, text in traceback.extract_tb(session.last_traceback):
        items.append("{2}({0}:{1})".format(fname, line, func, text))
    rets = "[\n\b\n" + "\n".join(items) + "\n\b\n nil nil nil]"
    w({"value": rets, "ns": msg.get("ns", "Hy")})
    w({"status": ["done"]})

def work_around_last(session, msg, w):
    w({"out": "success"})
    w({"value": "nil"})
    w({"status": ["done"]})

hints = {'(do (println "success") (symbol (str (System/getProperty "path.separator") ' +
        '(System/getProperty "java.class.path"))))': work_around_init_1,
        '[(System/getProperty "path.separator") (System/getProperty "java.class.path")]': work_around_init_2,
        '[(symbol (str "\\n\\b" (apply str (interleave (repeat "\\n") (map str (.getStackTrace *e)))) "\\n\\b\\n")) *3 *2 *1]': work_around_traceback,
        '(*1 1)': work_around_last,
        '(*2 2)': work_around_last,
        '(*3 3)': work_around_last,
        }
