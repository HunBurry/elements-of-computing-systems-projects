
from testing import *

#do works if (), does not work if (param) or (param, param2)
#return does work
#let does work
#while works if while(true), does not work if while ((true) | (false))
#if 


## ---------------------------------------------------------
class Parser:

    def __init__(self, inp):
        self.toker = Tokenizer(inp)
        self.saved = []   # pushed-back tokens
        self.first = True


    def parseClass(self):
        kwTok = self.nextToken()  # 'class'
        cnTok = self.nextToken()  # the classname
        opBrk = self.nextToken()  # '{'
        print("<class>")
        print(kwTok)
        print(cnTok)
        print(opBrk)

        nextTok = self.nextToken()   # maybe '}'
        while nextTok.val != '}':
            self.saveToken(nextTok)
            if nextTok.val in ['static', 'field']:
                self.parseClassVarDec()
            else:
                self.parseSubroutineDec()
            nextTok = self.nextToken()   # maybe '}'
        
        print(nextTok)    # the '}'
        print("</class>")


    def nextAndPrint(self):
        tok = self.nextToken()
        print(tok)
        return tok


    def parseSubroutineDec(self):
        print("<subroutineDec>")
        tok = self.nextToken(); print(tok)     #  'constructor'/'function'/'method'
        retType = self.nextAndPrint() 
        subName = self.nextAndPrint()
        opParen = self.nextAndPrint()
        self.parseParameterList()
        self.nextAndPrint()    # the ')'
        self.parseSubroutineBody()
        print("</subroutineDec>")


    def parseParameterList(self):
        print("<parameterList>")
        tok = self.nextToken()
        if tok.val != ')':
            typTok = tok
            print(typTok)
            nameTok = self.nextAndPrint()
            tok = self.nextToken()
            while tok.val == ',':
                print(tok)
                typTok = self.nextAndPrint()
                nameTok = self.nextAndPrint()
                tok = self.nextToken()
        self.saveToken(tok);
        print("</parameterList>")


    def parseSubroutineBody(self):
        print("<subroutineBody>")
        self.nextAndPrint()  ## '{'

        tok = self.nextToken()
        while tok.val != '}':
            self.saveToken(tok)
            if tok.val == 'var':
                self.parseVar()
            else:
                self.parseStatements()
            tok = self.nextToken()

        print(tok)  ## '}'
        print("</subroutineBody>")



    def parseVar(self):
        print("<varDec>")
        self.nextAndPrint()   # the 'var'
        typetok = self.nextToken()   # the 'type' token
        print(typetok)
        nametok = self.nextToken()   # the variable name
        print(nametok)
        maybesemi = self.nextToken()
        while (maybesemi.val != ';'):
            print(maybesemi)
            # means that maybesemi was actually a comma
            nextNameTok = self.nextToken();
            print(nextNameTok)
            maybesemi = self.nextToken();
        print(maybesemi)
        print("</varDec>")



    def parseClassVarDec(self):
        print("<classVarDec>")
        print(self.nextToken())   # the 'var'
        typetok = self.nextToken()
        print(typetok)
        nametok = self.nextToken()   # the variable name
        print(nametok)

        maybesemi = self.nextToken()
        while (maybesemi.val != ';'):
            print(maybesemi)
            # means that maybesemi was actually a comma
            nextNameTok = self.nextToken();
            print(nextNameTok)
            maybesemi = self.nextToken();
        print(maybesemi)

        print("</classVarDec>")

    def parseIf(self):
        print("<ifStatement>")
        ifSta = self.nextAndPrint()
        paren1 = self.nextAndPrint()
        self.parseExpr()
        # should i add a while here keep evaulating expressions while the symbol is not a ')'
        paren1 = self.nextAndPrint()
        brack1 = self.nextAndPrint()
        self.parseStatements()
        brack2 = self.nextAndPrint()
        maybeElse = self.nextToken()
        if maybeElse.val == "else":
            print(maybeElse)
            brack3 = self.nextAndPrint()
            self.parseStatements();
            brack4 = self.nextAndPrint()
        else:
            self.saveToken(maybeElse)
        print("</ifStatement>")

        """curCounter = 1
        first = True
        while (curCounter >= 1):
            tok = self.nextToken()
            if (tok.val == "{") and first: 
                self.saveToken(tok)
                self.parseSymbol()
                first = False;
            elif (tok.val == "{") and (first == False):
                self.saveToken(tok)
                self.parseSymbol()
                curCounter = curCounter + 1
            elif (tok.val == "}"):
                self.saveToken(tok)
                self.parseSymbol()
                curCounter = curCounter - 1;
            elif (tok.val == "(") and first:
                print("<symbol> ( </symbol>\n")
                self.parseTerm(")")
            else: 
                self.saveToken(tok)
                self.myParser()"""

    
    def parseWhile(self):
        print("<whileStatement>")
        whiSt = self.nextAndPrint()
        paren1 = self.nextAndPrint()
        self.parseExpr() # should i add a while here keep evaulating expressions while the symbol is not a ')'
        paren2 = self.nextAndPrint()
        brack1 = self.nextAndPrint()
        self.parseStatements()
        brack2 = self.nextAndPrint()
        print("</whileStatement>")
        """curCounter = 1
        first = True
        while (curCounter >= 1):
            tok = self.nextToken()
            if (tok.val == "{") and first: 
                self.saveToken(tok)
                self.parseSymbol()
                first = False;
            elif (tok.val == "{") and (first == False):
                self.saveToken(tok)
                self.parseSymbol()
                curCounter = curCounter + 1
            elif (tok.val == "}"):
                self.saveToken(tok)
                self.parseSymbol()
                curCounter = curCounter - 1;
            else: 
                self.saveToken(tok)
                self.myParser()"""

    def parseFor(self):
        print("<forStatement>")
        curCounter = 1
        first = True
        while (curCounter >= 1):
            tok = self.nextToken()
            if (tok.val == "{") and first: 
                first = False;
            elif (tok.val == "{") and (first == False):
                curCounter = curCounter + 1
            elif (tok.val == "}"):
                curCounter = curCounter - 1;
            else: 
                self.myParser()
        print("</forStatement>")




    def parseStatements(self):
        print("<statements>") 
        tok = self.nextToken()
        self.saveToken(tok)

        while tok.val in [ "let" , "do", "if", "while", "return" ]:
            if tok.val == "let": self.parseLet()
            elif tok.val == "do": self.parseDo()
            elif tok.val == "if": self.parseIf()
            elif tok.val == "return": self.parseReturn()
            elif tok.val == "while": self.parseWhile()

            tok = self.nextToken()       
            self.saveToken(tok)
        
        print("</statements>")


    def parseReturn(self):
        print("<returnStatement>")
        returnStatement = self.nextAndPrint()
        maybeSemi = self.nextToken()

        while maybeSemi.val != ";":
            self.saveToken(maybeSemi)
            self.parseExpr()
            maybeSemi = self.nextToken()

        print(maybeSemi)
        print("</returnStatement>")

    def parseDo(self):
        print("<doStatement>")
        tok = self.nextAndPrint() #print do 
        varName = self.nextAndPrint() #print name
        maybeDot = self.nextToken()
        if maybeDot.val == ".":
            print(maybeDot)
            funcName = self.nextAndPrint()
            paren1 = self.nextAndPrint()
            self.parseExpressionList()
        else: 
            print(maybeDot);
            self.parseExpressionList()
        self.nextAndPrint()
        print("</doStatement>")


    def parseExpressionList(self):
        print("<expressionList>")
        #rungame()
        #do rungame(game1)
        #rungame(game1, game2, game3)
        tok = self.nextToken()
        if tok.val != ")":
            self.saveToken(tok)
            self.parseExpr()
            tok = self.nextToken()
        else:
            self.saveToken(tok)
        print("</expressionList>")
        self.nextAndPrint()


        


        """
        tok = self.nextToken()  # maybe a '['
        if tok.val == ';':
            print(tok)
            self.parseExpr()
            self.nextAndPrint()  # the ']'
            self.nextAndPrint()   # the '='
        else:
            print(tok)  # the '='

        self.parseExpr()
        self.nextAndPrint()   # the ';'
        """

    
    def parseLet(self):
        print("<letStatement>")
        tok = self.nextAndPrint()
        varName = self.nextAndPrint()

        tok = self.nextToken()  # maybe a '['
        if tok.val == '[':
            print(tok)
            self.parseExpr()
            self.nextAndPrint()  # the ']'
            self.nextAndPrint()   # the '='
        else:
            print(tok)  # the '='

        self.parseExpr()
        self.nextAndPrint()   # the ';'
        print("</letStatement>")

    
    def parseExpr(self):
        print("<expression>")
        self.parseTerm()
        
        tok = self.nextToken();
        while tok.val in "+-*/&|<>=":
            print(tok)
            self.parseTerm()
            tok = self.nextToken()
        
        self.saveToken(tok);
        print("</expression>")
        if tok.val == ",":
            self.nextAndPrint()
        


    def parseTerm(self):
        print("<term>")
        tok = self.nextAndPrint()
        print("</term>")


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
    #p = Parser(io.FileIO("Main.jack"))
    p = Parser(io.BytesIO(b"""class Test {  
                                    field int x, y; static boolean z, test; 
                                    constructor Test new(int x, boolean y) {
                                        var String s, t, u;
                                        var int a, b;

                                        let x = 5;
                                        if(5 = 5) {
                                            return 5 + 9;
                                        }
                                        else {
                                            return this;
                                        }
                                     }
                            }"""))
    p.parseClass()


if __name__ == "__main__":
    main()