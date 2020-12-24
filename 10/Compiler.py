
import io

##
##    Tokenizer for the following lexical specification
##
##    keyword:     define | cond | else
##    symbol:	     (    |    )
##    intConstant: one or more digits
##    stringConst: " any sequence of chars besides double quote or newline "
##    identifier:  any other sequence of non-whitespace characters starting with a letter
##    comment:     ;  ...  till newline character
##


## simple unit test function
def check(func, exp):
    if (func != exp):
        raise Exception("FAIL! {0} should be {1}.".format(func, exp))


## ---------------------------------------------------------
## DATA DEFINITION FOR TOKENS

# Some constant tags for keyword types
class Keyword:
    DEFINE, COND, ELSE = range(3)
    STRS = [ "define", "cond", "else" ]

# Some constant tags for token types
class TokType:
    KEYWORD, SYMBOL, IDENT, NUMBER, STRING = range(5)

class Token:
    def __init__(self, typ, val):
        self.type = typ
        self.val = val
        
## A Token is one of:
##    Token( TokType.KEYWORD , KwType )
##    Token( TokType.SYMBOL , String )
##    Token( TokType.IDENT , String )
##    Token( TokType.NUMBER , Number )
##    Token( TokType.STRING , String )


# Tokenizer states
class TState:
    START, LINE_COMMENT, INTCONST, STRCONST, KW_OR_IDENT, IDENT,  \
        DONE_SYMBOL, DONE_INTCONST, DONE_STRCONST, DONE_KEYWORD, DONE_IDENT  \
        = range(11)

## A 1str is a one-character string

## ---------------------------------------------------------
class Tokenizer:

    def __init__(self, inp):
        self.inp = inp    # input (file) port
        self.st = TState.START   # current state
        self.acc = ""     # accumulated token
        self.ahead = ""   # pushback buffer
        self.eof = False  # has end-of-file input already happened?

    ##------------------------
    ## nextToken : -> Token or False
    def nextToken(self):
        if self.eof: return False

        while (true):
            c = self.nextChar()
            #  NOTE: c will be '' (empty string) if no more input
            



    ##------------------------
    # transition functionality
    # : 1str TState -> void
    def collectGoto(self, c, newst):
        self.acc = self.acc + c
        self.st = newst

    def pushBackGoto(self, c, newst):
        self.ahead = c + self.ahead
        self.st = newst

    def gotoState(self, c, newst):
        # c is ignored
        self.st = newst

    # reset to START state, clear accumulated token string
    def resetState(self):
        self.st = TState.START
        self.acc = ""

    def tokerError(self, msg):
        raise Exception(msg)

    ##-------------------------------------
    # low-level character reading functions
    # : -> 1str or ''
    def nextChar(self):
        if (self.eof): return ''
        elif (self.ahead):
            c = self.ahead[0]
            self.ahead = self.ahead[1:]
            return c
        else:
            return self.inp.read(1)

    # : 1str -> void
    def pushBack(self, c):
        self.ahead = c + self.ahead

    


## TESTS

def test():
    # nextChar / pushBack
    t = Tokenizer(io.StringIO("hello world"));
    check(t.nextChar(), 'h')
    t.nextChar()
    t.nextChar()
    t.pushBack('l')
    t.pushBack('e')
    check(t.nextChar(), 'e')
    

test()