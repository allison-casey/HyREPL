HyREPL
=======

NREPL server for Hy. Experminel/Hack project at this very moment.
The current debug enviorment relies on sockets:

1. install these dependencies: `blessings` and `nrepl-python-client`
2. Connect with netcat too port `13337`.  
3. Run `client.py` and `main.py` (main.py is the server while client just sends basic commands)   
4. Watch the magic in the netcat session  

TODO:
1. Fork it (yes, you!)
2. Add lisence
3. Get code running
4. Fill in blank stuff
5. ???
6. Tests

Current structure is a simple multi-threaded TCP server using socketserver's example code on exactly that (copypastaaaaaa), sessions will be kept in classes and each session (a session is just a random generated UUID) will have a repl class to keep the code in place.

Sources:  
https://github.com/cemerick/nrepl-python-client (the readme gives some examples how the nrepl works)  
https://github.com/clojure/tools.nrepl/blob/master/doc/ops.md   
  
