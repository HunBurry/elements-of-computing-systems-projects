
from Tokenizer import *
import os
import sys
import glob

class Parser:

    def __init__(self, inp):
        self.toker = Tokenizer(inp)
        self.saved = []   # pushed-back tokens
        self.first = True
        self.currentFile = ""

    def parseClass(self):
        kwTok = self.nextToken()  # 'class'
        cnTok = self.nextToken()  # the classname
        opBrk = self.nextToken()  # '{'
        self.currentFile.write("<class>")
        self.currentFile.write(str(kwTok))
        self.currentFile.write(str(cnTok))
        self.currentFile.write(str(opBrk))

        nextTok = self.nextToken()   # maybe '}'
        while nextTok.val != '}':
            self.saveToken(nextTok)
            if nextTok.val in ['static', 'field']:
                self.parseClassVarDec()
            else:
                self.parseSubroutineDec()
            nextTok = self.nextToken()   # maybe '}'
        
        self.currentFile.write(str(nextTok))   # the '}'
        self.currentFile.write("</class>")


    def nextAndPrint(self):
        tok = self.nextToken()
        self.currentFile.write(str(tok))
        return tok

    def parseSubroutineCall(self):
        tokName = self.nextAndPrint()
        maybeDot = self.nextToken()
        if maybeDot.val == ".":
            self.currentFile.write(str(maybeDot))
            funcName = self.nextAndPrint()
            paren1 = self.nextAndPrint()
            self.parseExpressionList()
        else: 
            self.currentFile.write(str(maybeDot)); #is actually a parenetheses 
            self.parseExpressionList()
        self.nextAndPrint()


    def parseSubroutineDec(self):
        self.currentFile.write("<subroutineDec>")
        tok = self.nextToken(); 
        self.currentFile.write(str(tok))     #  'constructor'/'function'/'method'
        retType = self.nextAndPrint() 
        subName = self.nextAndPrint()
        opParen = self.nextAndPrint()
        self.parseParameterList()
        self.nextAndPrint()    # the ')'
        self.parseSubroutineBody()
        self.currentFile.write("</subroutineDec>")


    def parseParameterList(self):
        self.currentFile.write("<parameterList>")
        tok = self.nextToken()
        if tok.val != ')':
            typTok = tok
            self.currentFile.write(str(typTok))
            nameTok = self.nextAndPrint()
            tok = self.nextToken()
            while tok.val == ',':
                self.currentFile.write(str(tok))
                typTok = self.nextAndPrint()
                nameTok = self.nextAndPrint()
                tok = self.nextToken()
        self.saveToken(tok);
        self.currentFile.write("</parameterList>")


    def parseSubroutineBody(self):
        self.currentFile.write("<subroutineBody>")
        self.nextAndPrint()  ## '{'

        tok = self.nextToken()
        while tok.val != '}':
            self.saveToken(tok)
            if tok.val == 'var':
                self.parseVar()
            else:
                self.parseStatements()
            tok = self.nextToken()

        self.currentFile.write(str(tok))  ## '}'
        self.currentFile.write("</subroutineBody>")



    def parseVar(self):
        self.currentFile.write("<varDec>")
        self.nextAndPrint()   # the 'var'
        typetok = self.nextToken()   # the 'type' token
        self.currentFile.write(str(typetok))
        nametok = self.nextToken()   # the variable name
        self.currentFile.write(str(nametok))
        maybesemi = self.nextToken()
        while (maybesemi.val != ';'):
            self.currentFile.write(str(maybesemi))
            # means that maybesemi was actually a comma
            nextNameTok = self.nextToken();
            self.currentFile.write(str(nextNameTok))
            maybesemi = self.nextToken();
        self.currentFile.write(str(maybesemi))
        self.currentFile.write("</varDec>")



    def parseClassVarDec(self):
        self.currentFile.write("<classVarDec>")
        self.currentFile.write(str(self.nextToken()))   # the 'var'
        typetok = self.nextToken()
        self.currentFile.write(str(typetok))
        nametok = self.nextToken()   # the variable name
        self.currentFile.write(str(nametok))

        maybesemi = self.nextToken()
        while (maybesemi.val != ';'):
            self.currentFile.write(str(maybesemi))
            # means that maybesemi was actually a comma
            nextNameTok = self.nextToken();
            self.currentFile.write(str(nextNameTok))
            maybesemi = self.nextToken();
        self.currentFile.write(str(maybesemi))

        self.currentFile.write("</classVarDec>")

    def parseIf(self):
        self.currentFile.write("<ifStatement>")
        ifSta = self.nextAndPrint()
        paren1 = self.nextAndPrint()
        self.parseExpr()
        paren2 = self.nextAndPrint()
        brack1 = self.nextAndPrint()
        self.parseStatements()
        brack2 = self.nextAndPrint()
        maybeElse = self.nextToken()
        if maybeElse.val == "else":
            self.currentFile.write(str(maybeElse))
            brack3 = self.nextAndPrint()
            self.parseStatements();
            brack4 = self.nextAndPrint()
        else:
            self.saveToken(maybeElse)
        self.currentFile.write("</ifStatement>")
    
    def parseWhile(self):
        self.currentFile.write("<whileStatement>")
        whiSt = self.nextAndPrint()
        paren1 = self.nextAndPrint()
        self.parseExpr() # should i add a while here keep evaulating expressions while the symbol is not a ')'
        paren2 = self.nextAndPrint()
        brack1 = self.nextAndPrint()
        self.parseStatements()
        brack2 = self.nextAndPrint()
        self.currentFile.write("</whileStatement>")

    def parseStatements(self):
        self.currentFile.write("<statements>") 
        tok = self.nextToken()
        self.saveToken(tok)

        while tok.val in [ "let" , "do", "if", "while", "return" ]:
            if tok.val == "let": 
                self.parseLet()
            elif tok.val == "do": 
                self.parseDo()
            elif tok.val == "if": 
                self.parseIf()
            elif tok.val == "return": 
                self.parseReturn()
            elif tok.val == "while": 
                self.parseWhile()

            tok = self.nextToken()       
            self.saveToken(tok)
        
        self.currentFile.write("</statements>")


    def parseReturn(self):
        self.currentFile.write("<returnStatement>")
        returnStatement = self.nextAndPrint()
        maybeSemi = self.nextToken()

        while maybeSemi.val != ";":
            self.saveToken(maybeSemi)
            self.parseExpr()
            maybeSemi = self.nextToken()

        self.currentFile.write(str(maybeSemi))
        self.currentFile.write("</returnStatement>")

    def parseDo(self):
        self.currentFile.write("<doStatement>")
        tok = self.nextAndPrint() #self.currentFile.write do 
        self.parseSubroutineCall()
        self.nextAndPrint() # self.currentFile.write semi
        self.currentFile.write("</doStatement>")
        

    def parseLet(self):
        self.currentFile.write("<letStatement>")
        tok = self.nextAndPrint()
        varName = self.nextAndPrint()

        #### i need to do something here so that it can detect the fact that anywhere in the entire statement can have a bracket
        tok = self.nextToken()  # maybe a '['
        if tok.val == '[':
            self.currentFile.write(str(tok))
            self.parseExpr()
            self.nextAndPrint()  # the ']'
            self.nextAndPrint()   # the '='
        else:
            self.currentFile.write(str(tok))  # the '='

        nextTok = self.nextToken(); #identifer
        nextTok2 = self.nextToken();
        if nextTok2.val == ".":
            self.saveToken(nextTok);
            self.saveToken(nextTok2);
            self.parseSubroutineCall();
        else:
            self.saveToken(nextTok);
            self.saveToken(nextTok2);
        self.parseExpr()
        self.nextAndPrint()   # the ';'
        self.currentFile.write("</letStatement>")


    def parseExpressionList(self):
        self.currentFile.write("<expressionList>")
        #rungame()
        #do rungame(game1)
        #rungame(game1, game2, game3)
        tok = self.nextToken()
        if tok.val != ")":
            self.saveToken(tok)
            self.parseExpr()
            tok = self.nextToken()
            while tok.val == ",":
                self.currentFile.write(str(tok))
                self.parseExpr()
                tok = self.nextToken()
            self.saveToken(tok)
        else:
            self.saveToken(tok)
        self.currentFile.write("</expressionList>")
    
    def parseLet(self):
        self.currentFile.write("<letStatement>")
        tok = self.nextAndPrint()
        varName = self.nextAndPrint()

        tok = self.nextToken()  # maybe a '['
        if tok.val == '[':
            self.currentFile.write(str(tok))
            self.parseExpr()
            self.nextAndPrint()  # the ']'
            self.nextAndPrint()   # the '='
        else:
            self.currentFile.write(str(tok))  # the '='

        self.parseExpr()
        self.nextAndPrint()   # the ';'
        self.currentFile.write("</letStatement>")

    
    def parseExpr(self):
        self.currentFile.write("<expression>")
        self.parseTerm()
        
        tok = self.nextToken();
        while tok.val in "+-*/&|<>=":
            self.currentFile.write(str(tok))
            self.parseTerm()
            tok = self.nextToken()

        self.saveToken(tok);
        self.currentFile.write("</expression>")
        


    def parseTerm(self):
        self.currentFile.write("<term>")
        tok = self.nextToken()
        if tok.val == "(":
            self.currentFile.write(str(tok))
            self.parseExpr()
            self.nextAndPrint()  # the ')'
        elif tok.val in ["-", "~"]:
            self.currentFile.write(str(tok))
            self.parseTerm()
        elif tok.type == TokType.KEYWORD:
            self.currentFile.write(str(tok))
        elif tok.type == TokType.NUMBER:
            self.currentFile.write(str(tok))
        elif tok.type == TokType.STRING:
            self.currentFile.write(str(tok))
        else:
            tok2 = self.nextToken()
            if tok2.val == "[":   # array access
                self.currentFile.write(str(tok))
                self.currentFile.write(str(tok2))
                self.parseExpr()
                self.nextAndPrint()  # ']'
            elif tok2.val in [".", "("]:   # subroutineCall
                self.saveToken(tok2)
                self.saveToken(tok)
                self.parseSubroutineCall()
            else:
                self.saveToken(tok2)
                self.currentFile.write(str(tok))
        self.currentFile.write("</term>")


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
    os.chdir(sys.argv[1])
    for file in glob.glob("*.jack"):
        p = Parser(io.FileIO(file))
        h = file.split(".");
        name = h[0] + ".txt"
        p.currentFile = open(name, "w")
        p.parseClass()
    #t = Parser(io.BytesIO(b"let j = j / (-2); }"))
    #t.parseLet()
    # p = Parser(io.FileIO("Main.jack"))
    # p.parseClass()
    # c = Parser(io.BytesIO(b"""class Test {  
    #                                 field int x, y; static boolean z, test; 
    #                                 constructor Test new(int x, boolean y) {
    #                                     var String s, t, u;
    #                                     var int a, b;

    #                                     let x = 5;
    #                                     if(5 = 5) {
    #                                         do run.game(1, 2, 3);
    #                                     }
    #                                     else {
    #                                         let x = 2;
    #                                         do run.game(1, 2);
    #                                         if(2 = 2) {
    #                                             let x = 2;
    #                                         }
    #                                     }
    #                                  }
    #                         }"""))

if __name__ == "__main__":
    main()
