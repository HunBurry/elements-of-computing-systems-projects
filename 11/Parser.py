
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
        self.currentSymTable = {}
        self.localCounter = 0
        self.className = ""
        self.classTable = {}
        self.ifCounter = 0
        self.elseCounter = 0
        self.whileCounter = 0
        self.fieldCounter = 0
        self.staticCounter = 0

    def parseClass(self):
        kwTok = self.nextToken()  # 'class'
        cnTok = self.nextToken()  # the classname
        self.className = cnTok.val
        opBrk = self.nextToken()  # '{'

        nextTok = self.nextToken()   # maybe '}'
        while nextTok.val != '}':
            self.saveToken(nextTok)
            if nextTok.val in ['static', 'field']:
                self.parseClassVarDec()
            else:
                self.parseSubroutineDec()
            nextTok = self.nextToken()   # maybe '}'



    def nextAndPrint(self):
        tok = self.nextToken()
        self.currentFile.write(tok)
        return tok

    def parseSubroutineCall(self):
        tokName = self.nextToken()
        maybeDot = self.nextToken()
        if maybeDot.val == ".":
            funcName = self.nextToken()
            #then do a self.currentFile.write in parseExpressionList to get the number of parameters 
            paren1 = self.nextToken()
            if tokName.val in self.currentSymTable.keys():
                self.currentFile.write("push " + self.currentSymTable[tokName.val]["jType"] + " " + str(self.currentSymTable[tokName.val]["position"]) + "\n")
            elif tokName.val in self.classTable.keys():
                self.currentFile.write("push " + self.classTable[tokName.val]["jType"] + " " + str(self.classTable[tokName.val]["position"]) + "\n")
            myInt = self.parseExpressionList()
            if tokName.val in self.currentSymTable.keys():
                self.currentFile.write("call " + self.currentSymTable[tokName.val]["pType"] + "." + funcName.val + " " + str(myInt + 1) + "\n")
            elif tokName.val in self.classTable.keys():
                self.currentFile.write("call " + self.classTable[tokName.val]["pType"] + "." + funcName.val + " " + str(myInt + 1) + "\n")  
            else:
                self.currentFile.write("call " + tokName.val + "." + funcName.val + " " + str(myInt) + "\n") 
        else: 
          #  self.currentFile.write(str(maybeDot)); #is actually a parenetheses 
            self.currentFile.write("push pointer 0\n")
            myInt = self.parseExpressionList()
            self.currentFile.write("call " + self.className + "." + tokName.val + " " + str(myInt + 1) + "\n")
        self.nextToken()


    def parseSubroutineDec(self):
        self.currentSymTable = {}
       # self.currentFile.write("<subroutineDec>")
        tok = self.nextToken(); 
        holding = tok.val
       # self.currentFile.write(str(tok))     #  'constructor'/'function'/'method'
        
        retType = self.nextToken() 
        subName = self.nextToken()
        opParen = self.nextToken()
        if holding == "method":
            self.parseParameterList(1);
        else:
            self.parseParameterList(0);
        count = 0;
        self.nextToken()    # the ')'
        self.nextToken()  ## '{'
        self.localCounter = 0
        tok = self.nextToken()
        while tok.val != '}':
            self.saveToken(tok)
            if tok.val == 'var':
                self.parseVar()
            else:
                anotherCount = 0
                for key in self.currentSymTable.keys():
                    if self.currentSymTable[key]["jType"] == "local":
                        anotherCount = anotherCount + 1
                self.currentFile.write("function " + self.className + "." + subName.val + " " + str(anotherCount) + "\n")
                if holding == "constructor":
                    for key in self.classTable.keys():
                        if self.classTable[key]["jType"] == "this":
                            count = count + 1
                    self.currentFile.write("push constant " + str(count) + "\ncall Memory.alloc 1\npop pointer 0\n")
                elif holding == "method":
                    self.currentFile.write("push argument 0\npop pointer 0\n")
                self.parseStatements()
            tok = self.nextToken()
        # if retType == "void":
        #     self.currentFile.write("push constant 0\nreturn")
        # elif tok.val == "constructor":
        #     self.currentFile.write("push pointer 0\nreturn")
        # else:
        #     self.currentFile.write("something")
       # self.currentFile.write("</subroutineDec>")
       
        


    def parseParameterList(self, myNum):
        tok = self.nextToken()
        argumentCounter = myNum;
        if tok.val != ')':
            typetok = tok
            nameTok = self.nextToken()
            self.currentSymTable[nameTok.val] = {
                "jType": "argument",
                "pType": typetok.val,
                "position": argumentCounter
            }
            argumentCounter = argumentCounter + 1
            tok = self.nextToken()
            while tok.val == ',':
                typTok = self.nextToken()
                nameTok = self.nextToken()
                self.currentSymTable[nameTok.val] = {
                    "jType": "argument",
                    "pType": typetok.val,
                    "position": argumentCounter
                }
                argumentCounter = argumentCounter + 1
                tok = self.nextToken()
        self.saveToken(tok);


    def parseSubroutineBody(self):
        self.nextToken()  ## '{'
        self.localCounter = 0
        tok = self.nextToken()
        while tok.val != '}':
            self.saveToken(tok)
            if tok.val == 'var':
                self.parseVar()
            else:
                self.parseStatements()
            tok = self.nextToken()


    def parseVar(self):
        ##need to be able to add class names
        #do something there about arrays maybe idk
        localCounter = self.localCounter;
        t = self.nextToken()   # the 'var'
        typetok = self.nextToken()   # the 'type' token
        nametok = self.nextToken()   # the variable name
        self.currentSymTable[nametok.val] = {
            "jType": "local",
            "pType": typetok.val,
            "position": localCounter
        }
        localCounter = localCounter + 1
        maybesemi = self.nextToken()
        while (maybesemi.val != ';'):
            nextNameTok = self.nextToken();
            self.currentSymTable[nextNameTok.val] = {
                "jType": "local",
                "pType": typetok.val,
                "position": localCounter
            }   
            localCounter = localCounter + 1
            maybesemi = self.nextToken();
        self.localCounter = localCounter



    def parseClassVarDec(self):

        ###change the fields in here to this 
        fieldCounter = self.fieldCounter;
        staticCounter = self.staticCounter;
        fieldOrStat = self.nextToken()
        typetok = self.nextToken()
        nametok = self.nextToken() 
        #self.currentFile.write("<classVarDec>")
        if fieldOrStat.val == "field":
            self.classTable[nametok.val] = {
                "jType": "this",
                "pType": typetok.val,
                "position": fieldCounter
            }
            fieldCounter = fieldCounter + 1
        else :
            self.classTable[nametok.val] = {
                "jType": "static",
                "pType": typetok.val,
                "position": staticCounter
            }
            staticCounter = staticCounter + 1
        
        maybesemi = self.nextToken()
        while (maybesemi.val != ';'):
            nextNameTok = self.nextToken();
            if fieldOrStat.val == "field":
                self.classTable[nextNameTok.val] = {
                    "jType": "this",
                    "pType": typetok.val,
                    "position": fieldCounter
                }
                fieldCounter = fieldCounter + 1
            else :
                self.classTable[nextNameTok.val] = {
                    "jType": "static",
                    "pType": typetok.val,
                    "position": staticCounter
                }
                staticCounter = staticCounter + 1
            maybesemi = self.nextToken();
        self.staticCounter = staticCounter;
        self.fieldCounter = fieldCounter;

    def parseIf(self):
        #self.currentFile.write("<ifStatement>")
        ifSta = self.nextToken()
        paren1 = self.nextToken()
        self.parseExpr()
        paren2 = self.nextToken()
        brack1 = self.nextToken()
        curCounter = self.ifCounter
        self.currentFile.write("if-goto IF_TRUE" + str(curCounter) + "\n")
        self.ifCounter = self.ifCounter + 1
        self.currentFile.write("goto IF_FALSE" + str(curCounter) + "\n")
        self.currentFile.write("label IF_TRUE" + str(curCounter) + "\n")
        self.parseStatements()
        brack2 = self.nextToken()
        maybeElse = self.nextToken()
        if maybeElse.val == "else":
            self.currentFile.write("goto IF_END" + str(curCounter) + "\n")
            self.currentFile.write("label IF_FALSE" + str(curCounter) + "\n")
           # self.currentFile.write(str(maybeElse))
            brack3 = self.nextToken()
            self.parseStatements();
            brack4 = self.nextToken()
            self.currentFile.write("label IF_END" + str(curCounter) + "\n")
        else:
            self.currentFile.write("label IF_FALSE" + str(curCounter) + "\n")
            self.saveToken(maybeElse)
        
       # self.currentFile.write("</ifStatement>")
    
    def parseWhile(self):
       # self.currentFile.write("<whileStatement>")
        whiSt = self.nextToken()
        paren1 = self.nextToken()
        counter = self.whileCounter
        self.whileCounter = self.whileCounter + 1
        self.currentFile.write("label WHILE_EXP" + str(counter) + "\n") 
        self.parseExpr() # should i add a while here keep evaulating expressions while the symbol is not a ')'
        self.currentFile.write("not\n")
        self.currentFile.write("if-goto WHILE_END" + str(counter) + "\n")
        paren2 = self.nextToken()
        brack1 = self.nextToken()
        self.parseStatements()
        brack2 = self.nextToken()
        self.currentFile.write("goto WHILE_EXP" + str(counter) + "\n")
        self.currentFile.write("label WHILE_END" + str(counter) + "\n")
        #self.currentFile.write("</whileStatement>")

    def parseStatements(self):
       # self.currentFile.write("<statements>") 
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
        
       # self.currentFile.write("</statements>")


    def parseReturn(self):
        #self.currentFile.write("<returnStatement>")
        returnStatement = self.nextToken()
        maybeSemi = self.nextToken()

        if maybeSemi.val ==  ";":
            #i think we need to determine if its consutrcotr, void, etc.
            self.currentFile.write("push constant 0\n")

        while maybeSemi.val != ";":
            self.saveToken(maybeSemi)
            self.parseExpr()
            maybeSemi = self.nextToken()
        
        self.currentFile.write("return\n")
        self.ifCounter = 0
        self.whileCounter = 0
        self.elseCounter = 0

       # self.currentFile.write(str(maybeSemi))
       # self.currentFile.write("</returnStatement>")

    def parseDo(self):
        tok = self.nextToken() #self.currentFile.write do 
        self.parseSubroutineCall()
        self.currentFile.write("pop temp 0\n");
        self.nextToken() # self.currentFile.write semi

    def parseExpressionList(self):
        #self.currentFile.write("<expressionList>")
        #rungame()
        #do rungame(game1)
        #rungame(game1, game2, game3)
        counter = 0
        tok = self.nextToken()
        if tok.val != ")":
            self.saveToken(tok)
            self.parseExpr()
            tok = self.nextToken()
            counter = counter + 1
            while tok.val == ",":
               # self.currentFile.write(str(tok))
                self.parseExpr()
                tok = self.nextToken()
                counter = counter + 1
            self.saveToken(tok)
        else:
            self.saveToken(tok)
        #self.currentFile.write("</expressionList>")
        return counter
    
    def parseLet(self):
        didAccess = False
       # self.currentFile.write("<letStatement>")
        tok = self.nextToken()
        varName = self.nextToken()
        pos = ""
        val = ""
        if (varName.val in self.currentSymTable.keys()):
            val = self.currentSymTable[varName.val]["jType"]
            pos = self.currentSymTable[varName.val]["position"]
        else:
            val = self.classTable[varName.val]["jType"]
            pos = self.classTable[varName.val]["position"]
        tok = self.nextToken()  # maybe a '['
        if tok.val == '[':
           # self.currentFile.write(str(tok))
            self.parseExpr()
            self.currentFile.write("push " + str(val) + " " + str(pos) + "\n")
            self.currentFile.write("add\n")
            self.nextToken()  # the ']'
            self.nextToken()   # the '='
            didAccess = True
        # else:
        #     another = self.nextToken()
        #     another2 =self.nextToken()
        #     self.currentFile.write(another)
        #     self.currentFile.write(another2)
        #     if another.type == TokType.IDENTIFIER and ((another2.val == "(") or (another2.val == ".")):
        #         self.saveToken(another2)
        #         self.saveToken(another)
        #         self.parseSubroutineCall()
        #     else:
        #         self.saveToken(another2)
        #         self.saveToken(another)
        self.parseExpr()
        self.nextToken()   # the ';'
        if didAccess:
            self.currentFile.write("pop temp 0\npop pointer 1\npush temp 0\npop that 0\n")
        else:
            self.currentFile.write("pop " + str(val) + " " + str(pos) + "\n")
       # self.currentFile.write("</letStatement>")

    
    def parseExpr(self):
      #  self.currentFile.write("<expression>")
        self.parseTerm()
        hold = ""
        
        tok = self.nextToken();
        while tok.val in "+-*/&|<>=":
            if tok.val == "+": 
                hold = "add"
            elif tok.val == "-":
                hold = "sub"
            elif tok.val == "/":
                hold = "call Math.divide 2"
            elif tok.val == "*":
                hold = "call Math.multiply 2"
            elif tok.val == "<":
                hold = "lt"
            elif tok.val == ">":
                hold = "gt"
            elif tok.val == "&":
                hold = "and"
            elif tok.val == "|":
                hold = "or"
            elif tok.val  == "=":
                hold = "eq"
          #  self.currentFile.write(str(tok))
            self.parseTerm()
            tok = self.nextToken()
        self.currentFile.write(hold + "\n")
        self.saveToken(tok);
        #self.currentFile.write("</expression>")
        


    def parseTerm(self):
       # self.currentFile.write("<term>")
        tok = self.nextToken()
        if tok.val == "(":
         #   self.currentFile.write(str(tok))
            self.parseExpr()
            self.nextToken()  # the ')'
        elif tok.val in ["-", "~"]:
          #  self.currentFile.write(str(tok))
          # this should push a "neg" function
          #but it should do it after pushing the constant 
            self.parseTerm()
            if tok.val == "-":
                self.currentFile.write("neg\n")
            else:
                self.currentFile.write("not\n")
        elif tok.type == TokType.KEYWORD:
            if tok.val == "this":
                self.currentFile.write("push pointer 0\n");
            elif tok.val == "false" or tok.val == "null":
                self.currentFile.write("push constant 0\n")
            elif tok.val == "true":
                self.currentFile.write("push constant 0\n")
                self.currentFile.write("not\n")
            else:
                self.currentFile.write(tok.val + "\n")
         #   self.currentFile.write(str(tok))
        elif tok.type == TokType.NUMBER:
            self.currentFile.write("push constant " + str(tok.val) + "\n")
          #  self.currentFile.write(str(tok))
        elif tok.type == TokType.STRING:
            self.saveToken(tok)
            self.makeString()
        else:
            ##this should be the identifer section
            tok2 = self.nextToken()
            if tok2.val == "[":   # array access
              #  self.currentFile.write(str(tok))
              #  self.currentFile.write(str(tok2))
                self.parseExpr()
                self.nextToken()  # ']'
                val = ""
                pos = ""
                if (tok.val in self.currentSymTable.keys()):
                    val = self.currentSymTable[tok.val]["jType"]
                    pos = self.currentSymTable[tok.val]["position"]
                else:
                    val = self.classTable[tok.val]["jType"]
                    pos = self.classTable[tok.val]["position"]
                self.currentFile.write("push " + str(val) + " " + str(pos) + "\n")
                self.currentFile.write("add\n")
                self.currentFile.write("pop pointer 1\npush that 0\n")
            elif tok2.val in [".", "("]:   # subroutineCall
                self.saveToken(tok2)
                self.saveToken(tok)
                self.parseSubroutineCall()
            else:
                self.saveToken(tok2)
                val = ""
                pos = ""
                ##i think i need something to see if its a this
                if (tok.val in self.currentSymTable.keys()):
                    val = self.currentSymTable[tok.val]["jType"]
                    pos = self.currentSymTable[tok.val]["position"]
                else:
                    val = self.classTable[tok.val]["jType"]
                    pos = self.classTable[tok.val]["position"]
                self.currentFile.write("push " + str(val) + " " + str(pos) + "\n")
               # self.currentFile.write(str(tok))
      #  self.currentFile.write("</term>")


    def makeString(self):
        myString = self.nextToken().val;
        self.currentFile.write("push constant " + str(len(myString)) + "\n");
        self.currentFile.write("call String.new 1\n");
        for char in myString:
            self.currentFile.write("push constant " + str(ord(char)) + "\n") #self.currentFile.writes a 'push constant 76' for a constant
            self.currentFile.write("call String.appendChar 2\n");


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
        name = h[0] + ".vm"
        p.currentFile = open(name, "w")
        p.parseClass()
            # p = Parser(io.FileIO("Pong/Ball.jack"))
    # p.currentFile = open("idk.txt", "w")
    # p.parseClass()

if __name__ == "__main__":
    main()
