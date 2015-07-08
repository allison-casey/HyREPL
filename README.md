HyREPL
======

HyREPL is an implementation of the [nREPL](https://github.com/clojure/tools.nrepl)
protocol for [Hy](https://github.com/hylang/hy).

[![asciicast](https://asciinema.org/a/0wdozdb8ohccuktt7henyt1r4.png)](https://asciinema.org/a/0wdozdb8ohccuktt7henyt1r4)

Experimental!
=============
HyREPL requires Python3 and is still a work in progress. It is suitable for
daily usage though :)

To install, run

    pip install -r requirements

Then set your `PYTHONPATH` to include the path to HyREPL:

    export PYTHONPATH=~/src/HyREPL

To run the tests, simply execute `nosetests-3.4 -v`. The tests create (and bind
to) a UNIX domain socket at `/tmp/HyREPL-test`.

Confirmed working nREPL clients
-------------------------------

This list is not exhaustive, and HyREPL does not support all features offered by
these clients, such as advanced debugger integration, profiling or tracing. Jump
to source is also not supported.

### Vim
* `fireplace` with [vim-hy](https://github.com/hylang/vim-hy) to provide the
  necessary glue

### Emacs
* `cider`
* `monroe`

### Console
* `python-nrepl-client`

Using HyREPL with fireplace
===========================
Open a Hy file and set the file type to `clojure`: `set filetype=clojure`. Then
run `hy -m HyREPL.server` in your target directory.  Connect vim to the REPL
with `:Connect`.  Use `nrepl` as the protocol, `localhost` as the host and the
port number HyREPL printed on start.

Missing features
----------------
* `:Require[!]` does not yet work. Use `:%Eval` to evaluate complete files.
* fireplace is not automatically loaded when editing Hy files. You need to set
  the file type to `clojure` manually.
* fireplace uses a lot of clojure-specific pieces of code. Most of these could
  be transformed with workarounds.

Using HyREPL inside your own programs
=====================================
You can use HyREPL to add a remote control to your own programs. The following
steps are a small example:

    (import sys time
      [HyREPL.server :as repl] [HyREPL.middleware.eval :as repl-mw])
    (setv (. repl-mw eval-module) (get (. sys modules) '--main--))
    (defmain [&rest args]
      (let [[s (repl.start-server)]]
        (print (.format "Listening on {}" (. (second s) server-address)))
        (while True
          (time.sleep 1))))

Made with ♥
===========

If you encounter bugs or missing features, please create an [issue
report](https://github.com/Foxboron/HyREPL/issues). Patches are always welcome.
If you have questions, we hang out in `#hy` on Freenode.
