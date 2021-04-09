from os import truncate
from typing import Any


codefile: str = "code.txt"
code: list = open(codefile, "r").readlines()

urcl: list = []
urclfuncs: list = []
class Var:
    def __init__(self, name: str, index: int, space: str, reg: int = 0, ram: int = 0):
        self.name  = name
        self.index = index
        self.space = space
        self.reg   = reg
        self.ram   = ram

    def print(self):
        print(f"variable {self.name} in space {self.space} with index {self.reg if self.space == 'reg' else self.ram} and variable index {self.index}")
class Func:
    def __init__(self, name, address, args):
        self.name = name
        self.address = address
        self.args = args

    def print(self):
        print(f"function {self.name} at address {self.address} with args:")
        for arg in self.args:
            arg: Var
            arg.print()
vars: dict = {}
funcs: dict = {}

haderror: bool = False
errors = 0
def error(msg: str):
    global haderror, errors
    print(f"Error! -> {msg}")
    haderror = True; errors += 1

def invars(name: str) -> bool:
    for element in vars:
        if element == name:
            return True
    return False

def toint(raw) -> Any:
    if type(raw) == str:
        if raw.isnumeric():
            return int(raw)
        else:
            error("immediate value is not int")
    elif type(raw) == int: return raw

def toop(raw: str) -> str:
    if invars(raw): return f"R{vars[raw].reg}"
    else: return raw

def varregram(raw: str) -> bool:
    if invars(raw):
        var = vars[raw]
        if var.space == "ram": return False
        elif var.space == "reg": return True
    else: return True

def ram(mode: str, f: str, t: Var) -> list:
    result = []

    if mode == "store": # to is ram
        if invars(f):
            if vars[f].space == "reg":
                result += [f"STR {t.ram}, R{vars[f].reg}"]

            elif vars[f].space == "ram":
                result += [
                    f"LOD R1, {vars[f].ram}",
                    f"STR {t.ram}, R1"
                ]

        else:
            result += [f"STR {t.ram}, {toint(f)}"]

    elif mode == "load": # from is ram; to is reg
        result += [f"LOD {t.reg}, R{vars[f].ram}"]

    return result

def set(x: Var, y: str) -> list:
    result = [] # x: to; y: from

    if x.space == "reg":
        if invars(y): # MOV
            y: Var = vars[y]

            if y.space == "reg":
                result += [f"MOV R{y.reg}, R{x.reg}"]
            elif y.space == "ram": # reg -> ram (store)
                result += ram("store", x, y)
        else: # IMM
            result += [f"IMM R{x.reg}, {toint(y)}"]

    elif x.space == "ram":
        if invars(y): # MOV
            y: Var = vars[y]

            if y.space == "reg":
                result += [f"MOV R{y.reg}, R{x.reg}"]
            elif y.space == "ram": # ram -> ram
                result += ram("store", x, y)
        else: # IMM
            result += ram("store", toint(y), x)

    return result

def op(op: str, x: Var, y: str, z: str) -> str:
    result = []

    if x.space == "reg":
        if varregram(y):
            if varregram(z): # reg reg
                result += [f"{ops[op]} R{x.reg}, {toop(y)}, {toop(z)}"]
            else: # reg ram
                result += [
                    f"LOD R3, {vars[z].ram}",
                    f"{ops[op]} R{x.reg}, {toop(y)}, R3"
                ]
        else:
            if varregram(z): # ram reg
                result += [
                    f"LOD R2, {vars[y].ram}",
                    f"{ops[op]} R{x.reg}, R2, {toop(z)}"
                ]
            else: # ram ram
                result += [
                    f"LOD R3, {vars[z].ram}",
                    f"LOD R2, {vars[y].ram}",
                    f"{ops[op]} R{x.reg}, R2, R3"
                ]
            
    elif x.space == "ram":
        if varregram(y):
            if varregram(z): # reg reg
                result += [
                    f"{ops[op]} R1, {toop(y)}, {toop(z)}",
                    f"STR {x.ram}, R1"
                ]
            else: # reg ram
                result += [
                    f"LOD R3, {vars[z].ram}",
                    f"{ops[op]} R1, {toop(y)}, R3",
                    f"STR {x.ram}, R1"
                ]
        else:
            if varregram(z): # ram reg
                result += [
                    f"LOD R2, {vars[y].ram}",
                    f"{ops[op]} R1, R2, {toop(z)}",
                    f"STR {x.ram}, R1"
                ]
            else: # ram ram
                result += [
                    f"LOD R3, {vars[z].ram}",
                    f"LOD R2, {vars[y].ram}",
                    f"{ops[op]} R1, R2, R3",
                    f"STR {x.ram}, R1"
                ]
    
    return result

operators = ["+", "-", "/", "*", "%", "|", "&", "^"]
ops: dict = {
    "+": "ADD",
    "-": "SUB",
    "/": "DIV",
    "*": "MLT",
    "%": "MOD",
    "|": "OR" ,
    "&": "AND",
    "^": "XOR"
}
latestindex = 0
latestreg = 4 # first 3 regs are temp regs (for ram variables)
latestram = 0
ramspaces = []
for i in range(16): ramspaces.append(i)
spaces = ["reg", "ram"]

def addvar(name: str, space: str):
    global vars, latestindex, latestreg, latestram

    if space == "reg":
        vars[name] = Var(name, latestindex, space, reg=latestreg)
        latestreg += 1

    elif space == "ram":
        vars[name] = Var(name, latestindex, space, ram=ramspaces[latestram])
        latestram += 1

    latestindex += 1

# clean the code
for i in range(len(code)):
    code[i] = code[i].replace("\n", "")

    split = code[i].split(" ")
    if len(split) == 0: continue

    new = []
    for element in split:
        if element != "//" and element != "#" and element != ";":
            new.append(element)
        else:
            break

    code[i] = " ".join(new)

print("code to compile:")

print("#####")
for line in code:
    print(line)
print("#####")

print("")
print("starting to compile...")

def compileline(split: list):
    global vars, urcl, latestindex, latestreg

    first = split[0]

    if first == "var": # initializing a variable
        space = split[1]
        name = split[2]
        addvar(name, space)
        if len(split) > 3:
            compileline(split[2:])

    elif first == "func": # declaring a function
        name = split[1]
        limitofargs = split.index("{")
        strargs = split[2:limitofargs-1]

        funcs[name] = Func(name, len(urclfuncs), strargs)

        # TODO compile the function and add it to urclfuncs

    elif first == "del":
        name = split[1]
        vars.pop(name)

    if invars(first): # doing something to a variable
        operation = split[1]
        if operation == "=":
            # setting: setting from operation or setting from variable
            if len(split) == 3: # setting from variable (x = y)
                operand = split[2]
                urcl += set(vars[first], operand)

            elif len(split) == 5: # setting from operation (x = y + z)
                operand1 = split[2]
                o = split[3]
                operand2 = split[4]
                urcl += op(o, vars[first], operand1, operand2)

        elif operation in operators: # (x + y)
            operand = split[2]
            urcl.append(op(operation, vars[first], first, operand))

for line in code:
    split = line.split(" ")

    if len(split) < 3: continue

    compileline(split)

if haderror == False:
    print("code succesfully compiled!")
else:
    print(f"encountered {errors} errors while compiling!")

print("")
print("variables:")
for varname in vars:
    vars[varname].print()

print("")
print("compiled urcl code:")

print("#####")
for line in urcl:
    print(line)
print("#####")

output = "output.urcl"
with open(output, "w") as f:
    for line in urcl:
        f.write(line + "\n")