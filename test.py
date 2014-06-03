# import nrepl


# c = nrepl.connect("nrepl://localhost:1337")

# # stdout test
# c.write({"op": "eval", "code": "(print 1)"})
# print(c.read())
# print(c.read())
# print(c.read())



# # stdin test
# c.write({"op": "eval", "code": '(def a (input))'})

# print(c.read())

# c.write({"op": "stdin", "value": "test"})
# print(c.read())

# c.write({"op": "eval", "code": "n"})
# print(c.read())
# print(c.read())
# print(c.read())

