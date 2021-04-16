from typing import List
import sys
try: from rich import print # import rich if installed
except: pass

### code variables & init
codefile: str = "code.txt"
codefile: str = sys.argv[1]
output: str = "output.txt"
output: str = sys.argv[2]
code: List[str] = open(codefile, "r").readlines()
line = 0

### CONFIG (BETA)
AddDefaultFunctionReturn = True

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
freepointers: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
usedvariablepointers: list[int] = []
usedvariablequicks: list[int] = [0] # reg 0 is unusable
maxvariables = 16
maxregs = 16
usednames: list[str] = ["num", "free", "quick", "//", "#", "+", "-", "*", "/", "&", "|", "^", "func", "{", "}", ";", "pop", "push", "main"]

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
class Var: # TODO variable types (num array list obj)
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
funcidentifier = 0
funcnames = []

funcobjs: dict = {}
class Func:
    def __init__(self, name, args, returntype):
        global funcidentifier, funcnames

        self.name = name
        self.args = args
        self.returntype = returntype
        self.identifier = funcidentifier
        funcnames.append(name)

        funcidentifier += 1

    def print(self):
        print(f"function {self.name} with identifier {self.identifier} and return type {self.returntype}")

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
            preparing.append(a)
            ycontent = f"R{yreg}"

        if z.isnumeric():
            zcontent = z
        else:
            a, zreg, quickz = handleoperand(z, True)
            preparing.append(a)
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

        return (f"// --- --- {optourcl[operator].lower()} operation\n" if debug else "") + "\n".join(preparing) + ("\n" if preparing != [] else "") + f"{optourcl[operator]} R{xreg}, {ycontent}, {zcontent}" + (f"\nSTR M{xvar.pointer}, R{xreg}" if xvar.type == "ram" else ""), quicks

    else:
        error(f"variable {x} doesn't exist")
        return "", []

def set(x: str, y: str) -> tuple: # (str, Var[]) | str: result; Var[]: temp variables
    if invars(x):
        xvar: Var = vars[x]

        if not y.isnumeric(): # y is variable
            preparation, yreg, quick = handleoperand(y, True)

            if xvar.type == "ram":
                return ("// --- --- set\n" if debug else "") + preparation + ("\n" if preparation != "" else "") + f"STR M{xvar.pointer}, R{yreg}", quick
            elif xvar.type == "quick":
                return ("// --- --- set\n" if debug else "") + preparation + ("\n" if preparation != "" else "") + f"IMM R{xvar.quick}, R{yreg}", quick
            else:
                error(f"variable {x} has a type that is not ram or quick ({xvar.type})")
                return "", None

        else: # y is numeric
            if xvar.type == "ram":
                return ("// --- --- set immediate\n" if debug else "") + f"STR M{xvar.pointer}, {y}", None
            elif xvar.type == "quick":
                return ("// --- --- set immediate\n" if debug else "") + f"IMM R{xvar.quick}, {y}", None
            else:
                error(f"variable {x} has a type that is not ram or quick ({xvar.type})")
                return "", None
    else:
        error(f"variable {x} is not a variable")
        return "", None

def stack(type: str, var: Var) -> tuple: # (result, quick) (str, Var)
    if type == "push":
        preparation, reg, quick = handleoperand(var.name, True)

        return ("// --- --- stack push\n" if debug else "") + preparation + ("\n" if preparation != "" else "") + f"PSH R{reg}", quick
    elif type == "pop":
        if var.type == "ram":
            quick = addvar(f"MY_COOL_TEMP_VARIABLE_{nextvariableidentifier*13}", "quick")

            return ("// --- --- stack pop\n" if debug else "") + f"POP R{quick.quick}\nSTR M{var.pointer}, R{quick.quick}", quick
        elif var.type == "quick":
            return ("// --- --- stack pop\n" if debug else "") + f"POP R{var.quick}", None
        return "", None # default

def genfunc(bricks: list[list[str]]) -> Func:
    global funcs

    #* parse args
    args = [x.split(" ") for x in " ".join(bricks[0][3:]).split(",")]

    newargs = []
    for i in range(len(args)):
        arg = args[i]

        newarg = []

        for subarg in arg:
            if subarg != "":
                newarg.append(subarg)

        args[i] = newarg

        if args[i] != []:
            newargs.append(arg[i])
    args = newargs

    print(f"--- func {bricks[0][2]} args: {args}")

    #* generate object
    funcobj: Func = Func(bricks[0][2], [x[0] for x in args], bricks[0][1])

    #* pop args & create arg variables
    for arg in args:
        argVar = addvar(arg[0], "quick")
        result, quick = stack("pop", argVar)

        if quick != None:
            free(quick)

        funcs[funcidentifier - 1].append(result)

    return funcobj

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
    global funcidentifier

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

        #* compilation of the bricks
        if bricks[0][0] == "func":
            funcs[funcidentifier].append(f".func_{bricks[0][2]}")
            funcobjs[bricks[0][2]] = genfunc(bricks)

            for brick in bricks[1:]:
                compilebrick(brick, True, funcidentifier - 1)
        else:
            for brick in bricks:
                compilebrick(brick)

    elif block.count("{") > 1: # subblocks
        print("--- calling recursive compilation")
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
            compilebrick(brick[1:], func, funcidentifier)
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

    elif brick[0] == "return":
        if invars(brick[1]):
            xvar = vars[brick[1]]

            result, quick = stack("push", xvar)
            result += "\nRET"

            if quick != None:
                free(quick)

            if not func:
                urcl.append(result)
            else:
                funcs[funcidentifier].append(result)
        else:
            error(f"variable {brick[1]} doesn't exist")

    elif brick[0] in funcnames:
        args = "".join(brick[1:]).split(",")

        print(f"--- --- calling args: {args}")

        if debug:
            urcl.append("// --- --- func call")

        for arg in args:
            if invars(arg):
                argvar = vars[arg]

                stack("push", argvar)
            else:
                urcl.append(f"PSH {toint(arg)}")

        urcl.append(f"CAL .func_{brick[0]}")

        if funcobjs[brick[0]].returntype != "void":
            urcl.append(f"POP R0") # void the return

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

def printfunctions():
    print("##### functions")
    for function in funcobjs: funcobjs[function].print()
    for function in funcs:
        for line in function:
            print(line)
    print("#####")

def printresult():
    print("##### result of the compilation(code):")
    #//print("#####")
    for line in urcl: print(line)
    print("#####")

def printfunctionsresult():
    print("##### result of the compilation(functions):")
    #//print("#####")
    for line in urclfuncs: print(line)
    print("#####")

def storeresult():
    with open(output, "w") as f:
        funcstr = ""
        for function in funcs:
            funcstr += "// --- function\n" if debug else ""
            funcstr += "\n".join(function)
        #//f.writelines(("\n" + ("//function" if debug else "")).join(["\n".join(x) for x in funcs]))
        f.write(("// entry point\n" if debug else "") + "JMP .main\n")
        f.writelines(funcstr)
        f.write("\n// main\n" if debug else "")
        f.writelines("\n".join(urcl))

### main
def main():
    global urcl

    clean()

    print("TUKE COMPILER (c) 2021\nEnjoy your stay\n")
    printcode()
    print("\nstarting to compile...")

    tokenize()
    urcl.append(".main")
    compile(tokens)
    urcl.append(("// end of the program\n" if debug else "") + "HLT")

    print(f"\ndone compiling!\n{(f'encountered {errors} errors' if haderror else 'succesfully compiled wooo')}\n")
    printvariables()
    print("")
    printfunctions()
    print("")
    printfunctionsresult()
    print("")
    printresult()

    storeresult()

main() # actually run the compiler :d
