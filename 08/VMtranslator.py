import sys
import re
import glob
import os

myFiles = []

newLineCounter = 0; #Counts the lines so that the 
functionCounter = 0;

#helper function for incrementations for the add/sub of the stack ponter
def addOrSub(string):
	if(string == "add"):
		file.write("@0\nM=M+1\n");
	elif(string == "sub"):
		file.write("@0\nM=M-1\n");
	
def push(segment, index):#Put a number onto the stack 
	file.write("//push" + " " + str(segment) + " " + str(index) + "\n")
	if(segment == "constant"): #Push a constant to the stack and increment the SP
		file.write("@"+ str(index) + "\nD=A\n@0\nA=M\nM=D\n")
		addOrSub("add")
	elif(segment in segments.keys() or segment in segments2.keys()):
		mySeg = ""
		hold = ""
		if(segment in segments.keys()):
			mySeg = segments[segment]
			hold = "A=M+D"
		else:
			mySeg = segments2[segment]
			hold ="A=A+D"
		file.write("@"+ str(index) + "\nD=A\n");
		file.write("@" + str(mySeg) + "\n")
		file.write(hold + "\n")	
		file.write("D=M\n@0\nA=M\nM=D\n");
		addOrSub("add")
	elif(segment == "static"):
		file.write("@" + re.sub("/", "_", myFiles[inc-1]) + "_" + index + "\nD=M\n@0\nA=M\nM=D\n");
		addOrSub("add")

def pop(segment, index):
	file.write("//pop" + str(segment) + " " + str(index) + "\n")
	if(segment == "constant"):
		pass;
	if(segment == "static"):
		file.write("@0\nAM=M-1\n")
		file.write("D=M\n@" + re.sub("/", "_", myFiles[inc-1]) + "_" + str(index) +"\nM=D\n")
	elif(segment in segments.keys() or segment in segments2.keys()):
		mySeg = ""
		holdStr = ""
		if(segment in segments.keys()):
			mySeg = segments[segment]
			holdStr = "D=D+M"
		else:
			mySeg = segments2[segment]
			holdStr = "D=D+A"
		file.write("@" + str(index) + "\nD=A\n@" + str(mySeg) + "\n")
		file.write(holdStr + "\n");
		file.write("@R15\nM=D\n@0\nAM=M-1\nD=M\n@R15\nA=M\nM=D\n")
	

def makeFunction(functionName, numOfParams):
	file.write("(" + functionName + ")\n")
	for x in range(int(numOfParams)):
		file.write("@0\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

def makeCall(functionName, numOfParams):
	global functionCounter
	file.write("@" + functionName + '_RETURN' +  str(functionCounter) + "\n")
	file.write("D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
	for param in possibleTypes:
		file.write("@" + param + "\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n");
	file.write("@SP\nD=M\n@LCL\nM=D\n");
	hold = str(int(numOfParams) + 5)
	file.write("@" + hold + "\nD=D-A\n@ARG\nM=D\n")
	file.write("@" + functionName + "\n0;JMP\n")
	file.write("(" + functionName + "_RETURN" + str(functionCounter) + ")\n")
	functionCounter = functionCounter + 1;
	

def makeReturn():
	file.write("@LCL\nD=M\n@R14\nM=D\n@5\nA=D-A\nD=M\n@R15\nM=D\n")
	file.write("@ARG\nD=M\n@0\nD=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n")
	file.write("@13\nA=M\nM=D\n@ARG\nD=M\n@SP\nM=D+1\n")
	for x in possibleTypes:
		file.write("@R14\nD=M\nA=D\nD=M-1\nD=M\n@" + x + "\nM=D\n")
	file.write("@R15\nA=M\n0;JMP\n")
	
segments = {
	"this" : "3",
	"that" : "4",
	"argument" : "2",
	"local" : "1",
}

segments2 = {
	"pointer" : "3", 
	"temp" : "5"
}

possibleTypes = ["THIS", "THAT", "LCL", "ARG"]

allCalls = {}


def add(): #Add the top 2 items of the stack and decrement the SP
	#file.write("@0\nAM=M-1\nD=M\nA=A-1\nM=M+D\n@0\nM=M-1\n")
	#file.write("@0\nAM=M-1\nD=M\n@SP\nAM=M-1\nM=D+M\n");
	#addOrSub("add")
	file.write("@0\nA=M-1\nD=M\nA=A-1\nM=M+D\n@0\nM=M-1\n")

def sub():#Subtracts the top number from the number below it.
	#file.write("@0\nAM=M-1\nD=M\n@SP\nAM=M-1\nM=M-D\n")
	#addOrSub("add")
	file.write("@0\nA=M-1\nD=M\nA=A-1\nM=M-D\n@0\nM=M-1\n")

def neg():#Negates the top number
	file.write("@0\nA=M-1\nM=-M\n")

def eq():#pops off the top two numbers, then pushes true on the stack if the top two numbers are equal or false if not equal.
	nlc = str(newLineCounter)
	file.write("@0\nA=M-1\nD=M\nA=A-1\nD=M-D\n@" + nlc + "true\nD;JEQ\n@0\nA=M-1\nA=A-1\nM=0\n@" + nlc + "end\n0;JMP\n(" + nlc + "true)\n@0\nA=M-1\nA=A-1\nM=-1\n(" + nlc + "end)\n")
	addOrSub("sub")

def gt():#pops off the top two numbers, then pushes true on the stack if the second number is greater than the top. Otherwise false.
	nlc = str(newLineCounter)
	file.write("@0\nA=M-1\nD=M\nA=A-1\nD=M-D\n@" + nlc + "true\nD;JGT\n@0\nA=M-1\nA=A-1\nM=0\n@" + nlc + "end\n0;JMP\n(" + nlc + "true)\n@0\nA=M-1\nA=A-1\nM=-1\n(" + nlc + "end)\n")
	addOrSub("sub")

def lt():#pops off the top two numbers, then pushes true on the stack if the second number is less than the top. Otherwise false.
	nlc = str(newLineCounter)
	file.write("@0\nA=M-1\nD=M\nA=A-1\nD=M-D\n@" + nlc + "true\nD;JLT\n@0\nA=M-1\nA=A-1\nM=0\n@" + nlc + "end\n0;JMP\n(" + nlc + "true)\n@0\nA=M-1\nA=A-1\nM=-1\n(" + nlc + "end)\n")
	addOrSub("sub")

def andfunc(): #Pops the top two numbers off and pushes a bitwise and of them.
	file.write("@0\nA=M-1\nD=M\nA=A-1\nM=D&M\n")
	addOrSub("sub")

def orfunc(): #Pops the top two numbers off and pushes a bitwise or of them.
	file.write("@0\nA=M-1\nD=M\nA=A-1\nM=D|M\n")
	addOrSub("sub")

def notfunc(): #Performs a bitwise not on the top number. 
	file.write("@0\nA=M-1\nM=!M\n")

def labelfunc(mylabel):
	file.write("(" + mylabel + ")\n");

def gotofunc(mylabel): 
	file.write("@" + mylabel + "\n0;JMP\n")

def ifgotofunc(mylabel): 
	file.write("@SP\nM=M-1\nA=M\nD=M\n@" + mylabel + "\nD;JNE\n");


#still need to add functionality for the actual functions and the return values in them 

#Reading the file that was input via the command line, enters each line into the list text_file
inc = 1

#things to do within these statements:
	#add functions/loops
	#if goto



if(os.path.isfile(sys.argv[1])):
	text_file = open(sys.argv[1], "r")
	lines = text_file.readlines()
	text_file.close()
	myFiles.append(sys.argv[1])
	tempLines = [] #Will hold the new 

	for x in range(0, len(lines)):
			lines[x] = re.sub("//.*", "", lines[x]) #Removes all comments
			lines[x] = re.sub("\n", "", lines[x])
			if(lines[x] != ""): #Removes all blank lines. 
				tempLines.append(lines[x]) 

	lines = tempLines #Sets our no blank lines list to the actual list. 

	file = open(sys.argv[2], "w") 

	file.write("@256\nD=A\n@0\nM=D\n") #Initialize the SP to 256
	makeCall("Sys.init", 0)

	for line in lines:
		newLineCounter += 1
		#MEMORY ACCESS COMMANDS
		if(line[0:4] == "push"): #Go to the push instruction with the segment and index
			s = line.split(" ")
			push(s[1], s[2])
		if(line[0:3] == "pop"): #Go to the push instruction with the segment and index
			s = line.split(" ")
			pop(s[1], s[2])
		#ARITHMETIC AND LOGICAL COMMANDS
		if(line[0:3] =="add"): #Execute the add
			add()
		if(line[0:3] =="sub"): #Execute the add
			sub()
		if(line[0:3] =="neg"): #Execute the add
			neg()
		if(line[0:2] =="eq"): #Execute the add
			eq()
		if(line[0:2] =="gt"): #Execute the add
			gt()
		if(line[0:2] =="lt"): #Execute the add
			lt()
		if(line[0:3] =="and"): #Execute the add
			andfunc()
		if(line[0:2] =="or"): #Execute the add
			orfunc()
		if(line[0:3] =="not"): #Execute the add
			notfunc()
		if(line[0:5] == "label"):
			t = len(line) 
			labelfunc(line[6:t])
		if(line[0:4] == "goto"):
			t = len(line)
			gotofunc(line[5:t])
		if(line[0:7] == "if-goto"):
			t = len(line)
			ifgotofunc(line[8:t])
		if(line[0:8] == "function"):
			t = line.split(" ")
			makeFunction(t[1], t[2])
		if(line[0:6] == "return"):
			t = line.split(" ")
			makeReturn()
		if(line[0:4] == "call"):
			t = line.split(" ")
			makeCall(t[1], t[2])
##else statement
else:
	os.chdir(sys.argv[1])
	file = open(sys.argv[2], 'w')
	file = open(sys.argv[2], 'a') 
	for file2 in glob.glob("*.vm"):
		print(file2)
		myFiles.append(file2)

#for fileName in range(1, (len(sys.argv)-1)):
		text_file = open(file2, "r+")
		lines = text_file.readlines()
		text_file.close()

		tempLines = [] #Will hold the new 

	#Removes the comments in each of the lines

		for x in range(0, len(lines)):
			lines[x] = re.sub("//.*", "", lines[x]) #Removes all comments
			lines[x] = re.sub("\n", "", lines[x])
			if(lines[x] != ""): #Removes all blank lines. 
				tempLines.append(lines[x]) 

		lines = tempLines #Sets our no blank lines list to the actual list. 

		file.write("@256\nD=A\n@0\nM=D\n") #Initialize the SP to 256
		makeCall("Sys.init", 0)
		for line in lines:
			newLineCounter += 1
			#MEMORY ACCESS COMMANDS
			if(line[0:4] == "push"): #Go to the push instruction with the segment and index
				s = line.split(" ")
				push(s[1], s[2])
			if(line[0:3] == "pop"): #Go to the push instruction with the segment and index
				s = line.split(" ")
				pop(s[1], s[2])
			#ARITHMETIC AND LOGICAL COMMANDS
			if(line[0:3] =="add"): #Execute the add
				add()
			if(line[0:3] =="sub"): #Execute the add
				sub()
			if(line[0:3] =="neg"): #Execute the add
				neg()
			if(line[0:2] =="eq"): #Execute the add
				eq()
			if(line[0:2] =="gt"): #Execute the add
				gt()
			if(line[0:2] =="lt"): #Execute the add
				lt()
			if(line[0:3] =="and"): #Execute the add
				andfunc()
			if(line[0:2] =="or"): #Execute the add
				orfunc()
			if(line[0:3] =="not"): #Execute the add
				notfunc()
			if(line[0:5] == "label"):
				t = len(line) 
				labelfunc(line[6:t])
			if(line[0:4] == "goto"):
				t = len(line)
				gotofunc(line[5:t])
			if(line[0:7] == "if-goto"):
				t = len(line)
				ifgotofunc(line[8:t])
			if(line[0:8] == "function"):
				t = line.split(" ")
				makeFunction(t[1], t[2])
			if(line[0:6] == "return"):
				t = line.split(" ")
				makeReturn()
			if(line[0:4] == "call"):
				t = line.split(" ")
				makeCall(t[1], t[2])
			

		inc = inc + 1;

file.write("(END)\n@END\n0;JMP\n") #At the end, do the infinite loop end bit.
file.close();



