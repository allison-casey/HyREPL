HyREPL 
======
  
Experimental! 
=============
Requires Python3.  
  
Install  
`pip install -r requirements`  

To run the tests, simply execute `nosetests-3.4 -v`. The tests create (and bind
to) a socket at `/tmp/HyREPL-test`.

Using HyREPL with fireplace
===========================
Open a Hy file and set the file type to `clojure`: `set filetype=clojure`. Then
run `main.hy` in your target directory. Connect vim to the REPL with `:Connect`.
Use `nrepl` as the protocol, `localhost` as the host and the port number HyREPL
printed on start.

Missing features
----------------
* `:Require[!]` does not yet work. Use `:%Eval` to evaluate complete files.
* fireplace is not automatically loaded when editing Hy files. You need to set
  the file type to `clojure` manually.
* fireplace uses a lot of clojure-specific pieces of code. Most of these could
  be transformed with workarounds.
