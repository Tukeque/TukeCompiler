# tuke compiler
a compiler from a custom language, tuke language, to URCL.

## usage
from the command line, run:
```
py compiler_1.0.py code.txt output.urcl
```
this will compile code.txt, wich is a code file written in tuke language to urcl and store it in output.urcl\
if you use another version, replace "compiler_1.0.py" with "compiler_1.1.py" for example if the version was 1.1\
if you want debug comments, run:
```
py compiler_1.0.py code.txt output.urcl debug
```

## tuke language
tuke language is a language i designed specifically for this compiler\
\
note: tokens must always be separated by a space or it does not work lol\

### variables
to create a variable, you do:
```
num x ;
```
\
you can operate on variables like this:
```
x = y + 50 ;
```

### quick variables
WARNING!: big brain, dont use if you dont need efficiency (because this is for efficiency)\
quick variables are variables that are stored in the registers instead of ram like normal variables. they are used to make a program faster\
create a quick variable:
```
quick quickVariable = 3 ; 
```
quickVariable is stored in a register\
quick variables work the same way as normal variables, they are just stored in registers, so you can operate on them like this:
```
quickVariable = x + 45 ;
```

### comments
you can do a comment by # or //. i added both because theyre both cool\
example
```
x = 4500 ; # comment!
num z = 69 ; // comment 2 !
```

note: the comment tokens have to be separated from the normal text to work\
this wont work:
```
num y ; #bad comment
```
nor this:
```
num w = 40 ;# also bad comment 
```

### functions
this is an example of defining a function:
```
func num addTwoValues x : num , y : num {
    num result = x + y ;
    return result ;
}
```
the first line is the function's features: func {return type} {name} [arguments] ...\
if the return type is "void", it means the function doesn't return anything\
the arguments are variables local to the function(they only exist in the function) that are defined separated by commas and with a semicolon to tell their type\
a function can have as many arguments as you want but it must only return 1 variable\
the code of the function is placed between the parentheses\
\
calling a function:
```
addTwoValues 6 , x ;
```
in this case, you're calling the function "addTwoValues" that was previously defined. It takes 2 arguments, so you call it with 6 and "x". Variables can be used when calling a function and immediate values too\
\
right now, setting a variable to the return of a function isn't implemented, but its planned and is coming soon

TODO libraries\
TODO linked lists\
TODO objects\
\
TODO keep updating this
