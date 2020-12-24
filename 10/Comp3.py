
from simpletok import *


# BSL grammar
#
#     prog        := ( def-or-expr )*
#     def-or-expr := def   |   expr
#     def         := '(' 'define' '(' ident ident (ident)* ')' expr ')'
#     expr        := ident
#                  | literal string "...."
#                  | literal integer ####
#                  | '(' ident expr (expr)* ')'
#                  | '(' 'cond' ( '(' expr expr ')' )* ')'
#                  | '(' 'cond' ( '(' expr expr ')' )* '(' 'else' expr ')' ')'




## ---------------------------------------------------------
class Parser:

    def __init__(self, inp):
        self.toker = Tokenizer(inp)
        self.saved = []   # pushed-back tokens

    def parseProgram(self):
        print("<prog>")
        tok = self.nextToken() # see if there even is a next token
        while tok:
            self.saveToken(tok)
            self.parseDefOrExpr()
            tok = self.nextToken() # see if there are more tokens
        print("</prog>")

    def parseDefOrExpr(self):
        # here, need to read potentially 2 tokens ahead to figure out if a 'def'
        fstTok = self.nextToken()
        isDef = False
        if fstTok.val == '(':
            sndTok = self.nextToken()
            if sndTok.val == 'define':
                isDef = True
            self.saveToken(sndTok)
        self.saveToken(fstTok)

        if isDef: self.parseDef()
        else: self.parseExpr()

    def parseDo(self):
        print("<doStatement>")
        tok = self.nextToken()
        while tok.val != ";":
            if tok.type == TokType.IDENT:
                print("<identifer>")
                print(tok.val)
                print("</identifer>")
            elif tok.type == TokType.SYMBOL:
                print("<symbol>")
                print(tok.val)
                print("</symbol>")
            #smething else here 
            tok = self.nextToken()
        print("</doStatement>")

    def parseDef(self):
        print("<def>")
        tok = self.nextToken()
        if not tok.val == '(': raise Exception("syntax error: expected ( got ", tok.val)
        tok = self.nextToken()
        if not tok.val == 'define': raise Expection("syntax error: expected define got ", tok.val)
        tok = self.nextToken()
        if not tok.val == '(': raise Exception("syntax error: expected ( got ", tok.val)

        funcName = self.nextToken()
        print(funcName)
        firstParam = self.nextToken()
        print(firstParam)

        nextTok = self.nextToken()
        while nextTok.type == TokType.IDENT:
            print(nextTok)
            nextTok = self.nextToken()
        if not nextTok.val == ')': raise Exception("syntax error: expected ) got ", tok.val)
        self.parseExpr()
        tok = self.nextToken()
        if not tok.val == ')': raise Exception("syntax error: expected ) got ", tok.val)
        print("</def>")

    def parseExpr(self):
        print("<expr>")
        fstTok = self.nextToken()
        if fstTok.type == TokType.IDENT or \
           fstTok.type == TokType.NUMBER or \
           fstTok.type == TokType.STRING:
                print(fstTok)
        else:  # the fstTok should be a '('
            sndTok = self.nextToken()
            if sndTok.type == TokType.IDENT:
                print(sndTok)
                self.parseExpr()
                nextTok = self.nextToken()
                while not nextTok.val == ')':
                    self.saveToken(nextTok)
                    self.parseExpr()
                    nextTok = self.nextToken()
            else:  # sndTok should be a 'cond'
                print("<cond>")
                nextTok = self.nextToken()
                while not nextTok.val == ')':
                    # nextTok should be '('
                    print("<cond-clause>")
                    qTok = self.nextToken()
                    if qTok.val == 'else':
                        self.parseExpr()
                        self.nextToken()   # should be ')'
                        self.nextToken()   # shoudl be ')'
                        print("</cond-clause>")
                        break
                    else:
                        self.saveToken(qTok)
                        self.parseExpr()
                        self.parseExpr();
                        self.nextToken()   # should be ')'
                        print("</cond-clause>")
                    nextTok = self.nextToken()
                print("</cond>")
        print("</expr>")



    # token access methods
    def nextToken(self):
        if not self.saved:
            return self.toker.nextToken()
        else:
            tok = self.saved[0]
            self.saved = self.saved[1:]
            return tok

    def saveToken(self, tok):
        self.saved = [tok] + self.saved




def main():
    p = Parser(io.FileIO("barometer-dir.txt"))
    p.parseProgram()


if __name__ == "__main__":
    main()