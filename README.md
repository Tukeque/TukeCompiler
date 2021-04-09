### tuke compiler
a compiler from a custom language, tuke compiler, to URCL.

## usage
from the command line, run:
```
py compiler_1.0.py code.txt output.urcl
```
this will compile code.txt, wich is a code file written in tuke language to urcl and store it in output.urcl
if you use another version, replace "compiler_1.0.py" with "compiler_1.1.py" for example if the version was 1.1
if you want debug comments, run:
```
py compiler_1.0.py code.txt output.urcl debug
```

## tuke language
tuke language is a language i designed specifically for this compiler

note: tokens must always be separated by a space or it does not work lol

variables:
to create a variable, you do:
```
num x ;
```

you can operate on variables like this:
```
x = y + 50 ;
```

quick variables:
WARNING: big brain, dont use if you dont need efficiency (because this is for efficiency)
quick variables are variables that are stored in the registers instead of ram like normal variables. they are used to make a program faster
create a quick variable:
```
quick quickVariable = 3 ; 
```
quickVariable is stored in a register
quick variables work the same way as normal variables, they are just stored in registers, so you can operate on them like this:
```
quickVariable = x + 45 ;
```

comments:
you can do a comment by # or //. i added both because theyre both cool
example
```
x = 4500 ; # comment!
num z = 69 ; // comment 2 !
```

note: the comment tokens have to be separated from the normal text to work
this wont work:
```
num y ; #bad comment
```
nor this:
```
num w = 40 ;# also bad comment 
```

TODO functions
TODO libraries
TODO linked lists
TODO objects

TODO keep updating this
