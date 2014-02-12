import nrepl


c = nrepl.connect("nrepl://localhost:8888")
c.write({"op": "eval", "code": '(def a (input))'})

test_st = "d4:code21:(reduce + (range 20))2:op4:evale"
test_st2 = "d4:code21:(reduce + (ran"


print(c.read())

c.write({"op": "stdin", "value": "test"})
print(c.read())

c.write({"op": "eval", "code": "n"})
print(c.read())
print(c.read())
print(c.read())

