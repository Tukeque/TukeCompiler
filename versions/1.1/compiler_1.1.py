from typing import List
import sys

### code variables
codefile: str = "code.txt"
codefile: str = sys.argv[1]
output: str = sys.argv[2]
code: List[str] = open(codefile, "r").readlines()
line = 0

debug = False
if len(sys.argv) > 3:
    if sys.argv[3] == "debug":
        debug = True
        print("DEBUGGING!")

### urcl variables
urcl: list = []
urclfuncs: list = []
funcs: list[list[str]] = [[]]

### variables
nextvariableidentifier = 0
freepointers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
usedvariablepointers = []
usedvariablequicks = [0] # reg 0 is unusable
maxvariables = 16
maxregs = 16
usednames = ["num", "free", "quick", "//", "#"]

def getvariablefreepointer() -> int:
    global usedvariablepointers

    for i in freepointers:
        if i not in usedvariablepointers:
            usedvariablepointers.append(i)
            return i

    error("exceeded the maximum amount of variables. Optimize your program to use less variables")
    return -1

def getvariablequick() -> int:
    global usedvariablequicks
    for i in range(maxregs):
        if i not in usedvariablequicks:
            usedvariablequicks.append(i)
            return i

    error("exceeded the maximum amount of quicks. Optimize your program (even more) to use less quicks")
    return -1

def getvariableidentifier() -> int:
    global nextvariableidentifier

    nextvariableidentifier += 1
    return nextvariableidentifier

vars: dict = {}
class Var: # TODO variable types (byte int obj)
    def __init__(self, name: str, type: str): # is done to be better :sunglasses:
        global nextvariableidentifier

        self.name = name
        self.type = type
        self.identifier = getvariableidentifier()
        
        if type == "ram":
            self.pointer = getvariablefreepointer()
        elif type == "quick":
            self.quick = getvariablequick()
        else:
            error(f"unknown variable type {type} when constructing a variable")

    def print(self):
        if self.type == "ram":
            print(f"ram variable {self.name} at address {self.pointer} and identifier {self.identifier}")
        elif self.type == "quick":
            print(f"quick variable {self.name} at register {self.quick} and identifier {self.identifier}")
        else:
            error(f"variable {self.name} has type {self.type} which is not ram or quick")

tempvars: List[Var] = []

### functions
funcs: dict = {} # TODO functions

### errors
haderror: bool = False
errors = 0
def error(msg: str) -> None:
    global haderror, errors
    print(f"ERROR! -> {msg}")
    input()
    haderror = True; errors += 1

### general purpose variable functions
def invars(name: str) -> bool:
    if name in vars: return True
    return False

def toint(raw) -> int:
    if type(raw) == str:
        raw: str
        if raw.isnumeric():
            return int(raw)
        else:
            error("immediate value is not an int")
            return -1
    elif type(raw) == int:
        return raw

def addvar(name: str, type: str) -> Var:
    global vars

    if name not in usednames: # name is free
        if name.isnumeric(): error(f"variable name {name} is numeric. Variables must be alphanumeric or alphabetic, not numeric")
        else:
            var = Var(name, type)
            vars[var.name] = var

            return var
    else:
        error(f"attempting to create a variable with name {name} but its already used or reserved")
        return None

def handleoperand(raw: str, load: bool) -> tuple: # returns (str, int, Var) | str: allocation; int: register; Var: allocated variable
    if invars(raw): # variable exists
        operand: Var = vars[raw]

        if operand.type == "quick":
            return "", operand.quick, None

        elif operand.type == "ram":
            newquick = addvar(f"MY_COOL_TEMP_VARIABLE_{nextvariableidentifier*13}", "quick")
            #//tempvars.append(newquick)

            return (f"LOD R{newquick.quick}, M{operand.pointer}" if load else ""), newquick.quick, newquick
    else:
        error(f"variable {raw} does not exist when handling an operand")
        return "", -1, None

def free(x: Var):
    if x.type == "quick":
        usedvariablequicks.remove(x.quick)
    elif x.type == "ram":
        usedvariablepointers.remove(x.pointer)
    else:
        error(f"variable {x} has unknown type {x.type}")

    vars.pop(x.name)

operators = ["+", "-", "/", "*", "%", "|", "&", "^"]
optourcl: dict = {
    "+": "ADD",
    "-": "SUB",
    "/": "DIV",
    "*": "MLT",
    "%": "MOD",
    "|": "OR" ,
    "&": "AND",
    "^": "XOR"
}
conditionals = ["if", "while", "for", "else", "elif"]
vartypes = ["num"]

### urcl functions
def operation(operator: str, x: str, y: str, z: str) -> tuple:  # (str, Var[]) | str: result; Var[]: temp variables
    if operator not in operators:
        error(f"operator {operator} is not a valid operator")
        return "", []

    if invars(x):
        xvar: Var = vars[x]

        preparing = []
        a = ""
        yreg = 0
        zreg = 0
        ycontent = ""
        zcontent = ""
        quicky = None
        quickz = None

        if y.isnumeric():
            ycontent = y
        else:
            a, yreg, quicky = handleoperand(y, True)
            preparing.append(a);
            ycontent = f"R{yreg}"

        if z.isnumeric():
            zcontent = z
        else:
            a, zreg, quickz = handleoperand(z, True)
            preparing.append(a);
            zcontent = f"R{zreg}"

        if xvar.type != "ram" and xvar.type != "quick": error(f"unknown variable {xvar.name} type {xvar.type} when handling an operand")

        a, xreg, quickx = handleoperand(x, False)
        preparing.append(a)

        quicks = [quicky, quickz, quickx]
        newquicks = []
        for quick in quicks:
            if quick != None: newquicks.append(quick)
        quicks = newquicks

        newpreparing = []
        for preparation in preparing:
            if preparation != "": newpreparing.append(preparation)
        preparing = newpreparing

        return "\n".join(preparing) + ("\n" if preparing != [] else "") + f"{optourcl[operator]} R{xreg}, {ycontent}, {zcontent}" + (f"\nSTR M{xvar.pointer}, R{xreg}" if xvar.type == "ram" else "") + ("// operation end" if debug else ""), quicks

    else:
        error(f"variable {x} doesn't exist")
        return "", []

def set(x: str, y: str) -> tuple: # (str, Var[]) | str: result; Var[]: temp variables
    if invars(x):
        xvar: Var = vars[x]

        if not y.isnumeric(): # y is variable
            preparation, yreg, quick = handleoperand(y, True)

            if xvar.type == "ram":
                return preparation + ("\n" if preparation != "" else "") + f"STR M{xvar.pointer}, R{yreg}" + ("// set end" if debug else ""), quick
            elif xvar.type == "quick":
                return preparation + ("\n" if preparation != "" else "") + f"IMM R{xvar.quick}, R{yreg}" + ("// set end" if debug else ""), quick
            else:
                error(f"variable {x} has a type that is not ram or quick ({xvar.type})")
                return "", None

        else: # y is numeric
            if xvar.type == "ram":
                return f"STR M{xvar.pointer}, {y}" + ("// set end" if debug else ""), None
            elif xvar.type == "quick":
                return f"IMM R{xvar.quick}, {y}" + ("// set end" if debug else ""), None
            else:
                error(f"variable {x} has a type that is not ram or quick ({xvar.type})")
                return "", None
    else:
        error(f"variable {x} is not a variable")
        return "", None

### compilation functions
def clean():
    global code

    for i in range(len(code)):
        code[i] = code[i].replace("\n", "")

        split = code[i].split(" ")
        if len(split) == 0: continue

        new = []
        for element in split:
            if element != "//" and element != "#":
                new.append(element)
            else:
                break

        code[i] = " ".join(new)

    newcode = []

    for i in range(len(code)):
        if code[i] != "": newcode.append(code[i])

    code = newcode

tokens = []
def tokenize():
    global tokens

    for line in code:
        tokens += line.split(" ")

    newtokens = []
    for token in tokens:
        if token != "": newtokens.append(token)

    tokens = newtokens

    print(f"* tokens = {tokens}")

def compile(tokens: List[str]):
    blocks: List[List[str]] = [[]]
    blockindex = 0
    mytokens = tokens.copy()
    inside = False
    layer = 0

    while mytokens != []:
        current = mytokens[0]

        if (current == "func" or current in conditionals) and inside == False:
            blockindex += 1
            blocks.append([current])
        else:
            blocks[blockindex].append(current)
            if current == "{" and inside == False: # can get in
                inside = True
                layer = 0
            elif current == "{" and inside == True:
                layer += 1
            elif current == "}":
                if layer == 0: # get out
                    inside = False
                    blockindex += 1
                    blocks.append([])
                else: # layer
                    layer -= 1

        mytokens.pop(0)

    newblocks = []
    for block in blocks:
        if block != []: newblocks.append(block)
    blocks = newblocks

    print(f"* blocks = {blocks}")
    print("compiling blocks...")

    for block in blocks:
        compileblock(block) # YEAH!!!

def compileblock(block: List[str]):
    length = len(block)
    print("--- compiling block...")

    if block.count("{") <= 1: # raw block
        bricks: List[List[str]] = [[]]
        brickindex = 0
        myblock = block.copy()

        ### initial brickizing
        while myblock != []:
            if myblock[0] == ";" or myblock[0] == "{" or myblock[0] == "}":
                brickindex += 1

                if len(myblock) >= 1:
                    bricks.append([])

            else:
                bricks[brickindex].append(myblock[0])

            myblock.pop(0)

        ### clean bricks
        newbricks = []
        for brick in bricks:
            if brick != []: newbricks.append(brick)
        bricks = newbricks

        print(f"--- bricks = {bricks}")

        for brick in bricks:
            compilebrick(brick)

    elif  block.count("{") > 1: # it has subblocks
        print("--- calling recursive compilation")
        #//input("--- STOP MOMENT")
        print(f"--- new tokens to compile = {block[block.index('{') + 1:-1]}")
        compile(block[block.index("{") + 1:-1])

    else:
        error("block has no brackets defining scope? what")

def compilebrick(brick: List[str], func = False, funcidentifier = 0):
    global urcl, tempvars

    length = len(brick)
    print("--- --- compiling brick")
    print(f"--- --- brick = \"{' '.join(brick)}\"")

    if brick[0] in vartypes or brick[0] == "quick": # (num a = 0 / num a) (variable allocation)
        addvar(brick[1], ("ram" if brick[0] in vartypes else "quick"))

        if length > 2: # (num a = x / num a = x + y) (variable setting or variable setting by operation)
            compilebrick(brick[1:])
        elif length == 2:
            pass
        else:
            error(f"invalid syntax in brick {brick}")

    elif brick[1] == "=": # setting a var to some value
        if length == 3: # a = x
            result, quick = set(brick[0], brick[2])
            if not func:
                urcl.append(result)
            else:
                funcs[funcidentifier].append(result)

            if quick != None:
                free(quick)

        elif length == 5: # a = x + y
            result, quicks = operation(brick[3], brick[0], brick[2], brick[4])
            if not func:
                urcl.append(result)
            else:
                funcs[funcidentifier].append(result)

            for quick in quicks:
                free(quick)

        else:
            error(f"invalid syntax in brick {brick}")

    elif brick[0] == "free":
        if invars(brick[1]):
            free(vars[brick[1]])
        else:
            error(f"attempting to free variable {brick[1]} that doesnt exist")

### printing functions
def printcode():
    print("##### code to compile:")
    #//print("#####")
    for line in code: print(line)
    print("#####")

def printvariables():
    print("##### variables")
    #//print("#####")
    for varname in vars: vars[varname].print()
    print("#####")

def printresult():
    print("##### result of the compilation:")
    #//print("#####")
    for line in urcl: print(line)
    print("#####")

#//output = "output2.urcl"
def storeresult():
    with open(output, "w") as f: f.writelines("\n".join(urclfuncs) + "\n".join(urcl))

### main
def main():
    global urcl

    clean()

    print("TUKE COMPILER (c) 2021\nEnjoy your stay\n")
    printcode()
    print("\nstarting to compile...")

    tokenize()
    compile(tokens)
    urcl.append("HLT")

    print(f"\ndone compiling!\n{(f'encountered {errors} errors' if haderror else 'succesfully compiled wooo')}\n")
    printvariables()
    print("")
    printresult()

    storeresult()

    #//input("input moment")

main() # actually run the compiler :d
