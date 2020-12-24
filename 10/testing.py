
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


# Some constant tags for token types
class TokType:
    KEYWORD, SYMBOL, IDENT, NUMBER, STRING = range(5)

def tokType(n):
    return ["keyword", "symbol", "ident", "number", "string"][n]

class Token:
    def __init__(self, typ, val):
        self.type = typ
        self.val = val

    def __str__(self):
        return "<%s>%s</%s>" % (tokType(self.type), self.val,  tokType(self.type))

## A Token is one of:
##    Token( TokType.KEYWORD , KwType )
##    Token( TokType.SYMBOL , String )
##    Token( TokType.IDENT , String )
##    Token( TokType.NUMBER , Number )
##    Token( TokType.STRING , String )


# Tokenizer states
class TState:
    START, LINE_COMMENT, INTCONST, STRCONST, KW_OR_IDENT, IDENT, SYMBOL,  \
        DONE_SYMBOL, DONE_INTCONST, DONE_STRCONST, DONE_KEYWORD, DONE_IDENT, COMMENT, MULTI_COMMENT \
        = range(14)

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

        while (True):
            c = self.nextChar()
            #  NOTE: c will be '' (empty string) if no more input

            if self.st == TState.START:
                if c:  self.fromStart(c)
                else:  return False
            elif self.st == TState.LINE_COMMENT: 
                self.fromLineComment(c)
            elif self.st == TState.COMMENT:
                self.fromComment(c)
            elif self.st == TState.MULTI_COMMENT:
                self.fromMultiComment(c)
            elif self.st == TState.INTCONST:     
                self.fromNumber(c)
            elif self.st == TState.STRCONST:     
                self.fromString(c)
            elif self.st == TState.IDENT:        
                self.fromIdent(c)
            elif self.st == TState.DONE_SYMBOL:
                self.pushBack(c)
                return self.processSymbol()
            elif self.st == TState.DONE_INTCONST:
                self.pushBack(c)
                return self.processNumber()
            elif self.st == TState.DONE_STRCONST:
                self.pushBack(c)
                return self.processString()
            elif self.st == TState.DONE_IDENT:
                self.pushBack(c)
                #here
                return self.processIdent()

    def fromStart(self, c):
        if isDigit(c): 
            self.collectGoto(c, TState.INTCONST)
        elif isComBegin(c):
            self.gotoState(TState.COMMENT)
        elif isQuote(c): 
            self.gotoState(TState.STRCONST)
        elif isLetter(c): 
            self.collectGoto(c, TState.IDENT)
        elif isWhitespace(c): 
            self.gotoState(TState.START)
        elif isSymbol(c): 
            self.collectGoto(c, TState.DONE_SYMBOL)
        else:
            print("Unexpected character: %s" % c)
        #print(" ===> %d /%s/" % (self.st, self.acc))

    def fromComment(self, c):
        if not c: 
            self.resetState()
        elif c == "/":
            self.collectGoto(c, TState.LINE_COMMENT)
        elif c == "*":
            self.collectGoto(c, TState.MULTI_COMMENT)
        elif isWhitespace(c):
            self.pushBack("/")
            self.gotoState(TState.DONE_SYMBOL)
        else:
            print("error")

    def fromMultiComment(self, c):
        if not c:
            self.resetState()
        elif "*/" in self.acc:
            self.resetState()
        else:
            self.collectGoto(c, TState.MULTI_COMMENT)

    def fromLineComment(self, c):
        if not c: 
            self.resetState()
        elif isNewline(c): 
            self.resetState()
        else: 
            self.collectGoto(c, TState.LINE_COMMENT)

    def fromNumber(self, c):
        if not c: 
            self.gotoState(TState.DONE_INTCONST)
        elif isDigit(c): 
            self.collectGoto(c, TState.INTCONST)
        else: 
            self.pushBackGoto(c, TState.DONE_INTCONST)

    def fromString(self, c):
        if not c: 
            print("Unexpected end of input in string literal")
        elif isNewline(c): 
            print("Unexpected new line in string literal")
        elif isQuote(c): 
            self.gotoState(TState.DONE_STRCONST)
        else: 
            elf.collectGoto(c, TState.STRCONST)

    def fromIdent(self, c):
        if not c: 
            self.gotoState(TState.DONE_IDENT)
        elif isWhitespace(c): 
            #self.pushBackGoto(c, TState.DONE_IDENT)
            #here
            self.gotoState(TState.DONE_IDENT)
        elif isSymbol(c):
            self.pushBackGoto(c, TState.DONE_IDENT)
        else: 
            self.collectGoto(c, TState.IDENT)

    def processSymbol(self):
        tok = self.acc
        self.resetState()
        return Token(TokType.SYMBOL, tok)

    def proccessLet(self, c):
        if c.isLetter(c):
            self.collectGoto(c, TState.IDENT)
        elif c.isSymbol(c):
            self.gotoState(TState.LET)
            self.processSymbol()
        elif c.isWhitespace(c):
            self.gotoState(TState.LET)

    def proccessDo(self, c):
        if c.isLetter(c):
            self.collectGoto(c, TState.IDENT)
        elif c.isSymbol(c):
            self.gotoState(TState.LET)
            self.processSymbol()
        elif c.isWhitespace(c):
            self.gotoState(TState.LET)

    def processNumber(self):
        tok = self.acc
        self.resetState()
        return Token(TokType.NUMBER, int(tok))

    def processString(self):
        tok = self.acc
        self.resetState()
        return Token(TokType.STRING, tok)

    def processIdent(self):
        tok = self.acc
        self.resetState()
        if self.isKeyword(tok):
            return Token(TokType.KEYWORD, tok)
        elif isSymbol(tok):
            self.processSymbol()
        else:
            return Token(TokType.IDENT, tok)

    def isKeyword(self, tok):
        return tok in ["void", "static", "this", "constructor", "boolean", "class", "while", "function", "var", "let", "do", "return", "null", "int", "if", "else", "true", "false"]


    ##------------------------
    # transition functionality
    # : 1str TState -> void
    def collectGoto(self, c, newst):
        self.acc = self.acc + c
        self.st = newst

    def pushBackGoto(self, c, newst):
        self.ahead = c + self.ahead
        self.st = newst

    def gotoState(self, newst):
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
            return str(self.inp.read(1), 'utf-8')

    # : 1str -> void
    def pushBack(self, c):
        self.ahead = c + self.ahead


## ---------- character predicates -----------------
def isDigit(c):
    return c.isdigit()

def isParen(c):
    return c in ["(", ")"]

def isSemicolon(c):
    return c == ";"

def isNewline(c):
    return c == "\n"

def isQuote(c):
    return c == "\""

def isLetter(c):
    return c.isalpha()

def isWhitespace(c):
    return c.isspace()

def isSymbol(c):
    return c.isprintable() and not c.isalnum() and not c.isspace()

def isComBegin(c):
    return c == "/"
