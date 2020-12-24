import sys
import re
import glob
import os

#TODO: file I/O, parsing original file string to tokens, classifying those tokens
#      Writing those classified tokens out, (the entire freaking parser)

funcs = {}; #list of current functions and where they are in the array of toks 

symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']

os.chdir(sys.argv[1])
for file in glob.glob("*.jack"):
    initialText = "" #Contains the big string of everything from the source file.
    tokens = [] #contains the tokens before being classified
    text_file = open(file, "r+")
    lines = text_file.readlines()
    text_file.close()
    tempLines = []

    for x in range(0, len(lines)):
        lines[x] = re.sub("//.*", "", lines[x]) #Removes all single line comments
        lines[x] = re.sub("/\*.*\*/", "", lines[x]) # removes all block comments
        lines[x] = re.sub("\n", "", lines[x])
        if(lines[x] != ""): #Removes all blank lines. 
            tempLines.append(lines[x]) 

    lines = tempLines

    for line in lines:
        initialText = initialText + line + "\n"

    currTok = "" #holds the current token that is being worked on
    toks = [] #holds all the tokens before being parsed
    inString = False #keeps track of if the parser is in a string. 

    for c in initialText: #Chop up string by spaces and symbols. ALso strings get pushed together. 
        currTok = currTok + c;

        if currTok == " " or currTok == "\n" or currTok == "\t": #Leading spaces are bad. 
            currTok = ""
        if (c == " " or c == "\n" or c == "\t") and currTok != "" and not inString:
            toks.append(currTok)
            currTok = "" 
        if not c.isspace() and not c.isalnum() and c != "\"" and not inString: #Basically only symbols
            toks.append(currTok[0:-1])
            toks.append(c)
            currTok = ""

        if currTok == "\"": #Found a string
            inString = True
        elif c == "\"":
            toks.append(currTok)
            currTok = ""
            inString = False
    
    currXML = "<tokens>\n" #holds a string that is all the XML
    curCounter = 1
    first = False
    ifInProgress = False
    doInProgress = False
    letInProgress = False

    for tok in toks:
        finishedParsing = False
        if (tok == "{") and first and ifInProgress: 
            first = False;
            finishedParsing = True
        elif (tok.value == "{") and (first == False) and ifInProgress:
            curCounter = curCounter + 1
            finishedParsing = True
        elif (tok.value == "}") and ifInProgress:
            curCounter = curCounter - 1;
            finishedParsing = True
        elif tok == ";" and doInProgess:
            doInProgess = False;
            currXML = currXML + "<symbol> " + tok + " </symbol>\n"
            currXML = currXML + "</doStatement>\n"
            finishedParsing = True
        elif tok == ";" and letInProgress:
            letInProgress = False;
            currXML = currXML + "<symbol> " + tok + " </symbol>\n"
            currXML = currXML + "</letStatement>\n"
            finishedParsing = True
        
        elif tok in symbols:
            currXML = currXML + "<symbol> " + tok + " </symbol>\n"
            finishedParsing = True

        elif tok == "if":
            currXML = currXML + "<ifStatement>\n <keyword> if </keyword>\n"
                if not ifInProgress:
                    first = True
                ifInProgress = True
            finishedParsing = True

        elif tok == "do":
            currXML = currXML + "<doStatement>\n"
                doInProgress = True;
            
        elif tok == "let":
            currXML = currXML + "<letStatement>\n"
                letInProgress = True;
        
        elif tok in keywords:
            currXML = currXML + "<keyword> " + tok + " </keyword>\n"
            finishedParsing = True

        
        if(finishedParsing):
            if curCounter == 0:
                ifInProgress = False
                currXML = currXML + "</ifStatement>\n"
            continue
        
        if tok[0:1] == "\"":
            currXML = currXML + "<stringConstant> " + tok[1:-1] + " </stringConstant>\n"
            continue

        if tok.isnumeric():
            currXML = currXML + "<integerConstant> " + tok + " </integerConstant>\n"
            continue

        if not finishedParsing and tok != "":
            currXML = currXML + "<identifier> " + tok + " </identifier>\n"


    currXML = currXML + "</tokens>\n"

    xmlname = file.split(".")[0]
    xmlFile = open(file + "T.xml", "w")
    xmlFile.write(currXML)





#ways to splice. ['(', ')', ',', ' ',]