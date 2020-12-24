import sys
import re

nextRamPos = 16

#Handles all the instructions starting with the "@" symbol
def atInstruction(symbol):
	global nextRamPos
	if(symbol.isdigit()):
		binToStr(symbol);
	else:
		li = list(allVals.keys())
		if(symbol not in li):
			allVals[symbol] = nextRamPos
			nextRamPos = nextRamPos + 1
		binToStr(str(allVals[symbol]))
        
def binToStr(string):
	b = bin(int(string))
	b = b.split("b")
	b = b[1]
	while len(b) < 16:
		b = "0" + b
	print(b)

#Dictionary of mnemonic to binary for the jump bits
jmpDict = {
	"null" : "000",
	"JGT" : "001",
	"JEQ" : "010",
	"JGE" : "011",
	"JLT" : "100",
	"JNE" : "101",
	"JLE" : "110",
	"JMP" : "111"
}

allVals = {	
	"R0"  :0,
	"R1"  :1,
	"R2"  :2,
	"R3"  :3,
	"R4"  :4,
	"R5"  :5,
	"R6"  :6,
	"R7"  :7,
	"R8"  :8,
	"R9"  :9,
	"R10" :10,
	"R11" :11,
	"R12" :12,
	"R13" :13,
	"R14" :14,
	"R15" :15,
	"KBD" :24576,
	"SCREEN":16384,
	"SP"  :0,
	"LCL" :1,
	"ARG" :2,
	"THIS":3, 
	"THAT":4
}

#dictionary of the mnemonic to binary for the dest bits
destDict = {
	"null" : "000",
	"M" : "001",
	"D" : "010",
	"MD" : "011",
	"A" : "100",
	"AM" : "101",
	"AD" : "110",
	"AMD" : "111"
}

#dictionary of the mnemonic to binary for the comp bits, as well as the A bit for added simplicity.
compDict = {
	"0"   : "0101010",
	"1"   : "0111111",
	"-1"  : "0111010",
	"D"   : "0001100",
	"A"   : "0110000",
	"!D"  : "0001101",
	"!A"  : "0110001",
	"-D"  : "0001111",
	"-A"  : "0110011",
	"D+1" : "0011111",
	"A+1" : "0110111",
	"D-1" : "0001110",
	"A-1" : "0110010",
	"D+A" : "0000010",
	"D-A" : "0010011",
	"A-D" : "0000111",
	"D&A" : "0000000",
	"D|A" : "0010101",
	"M"   : "1110000",
	"!M"  : "1110001",
	"M+1" : "1110111",
	"M-1" : "1110010",
	"D+M" : "1000010",
	"D-M" : "1010011",
	"M-D" : "1000111",
	"D&M" : "1000000",
	"D|M" : "1010101"
}

#Handles all of the instructions that do not have @ at the start of them. 
def computeInstruction(symbol):
	jmp = "000"
	dest = "000"
	comp = "0000000" #I am wrapping the A bit in with the compute just for simplicity in the LUT
	
	instruction = symbol.split(";")
	if(len(instruction) > 1):
		jmp = jmpDict[instruction[1]]
		instruction = instruction[0] #Chop off the semicolon bit

	instruction = instruction[0].split("=")
	if(len(instruction) > 1):
		dest = destDict[instruction[0]]
		comp = compDict[instruction[1]]
	else:
		comp = compDict[instruction[0]]

	print("111" + comp + dest + jmp)



#Reading the file that was input via the command line, enters each line into the list text_file
text_file = open(sys.argv[1], "r")
lines = text_file.readlines()
text_file.close()

newLineCounter = 0; #Will be counting the lines that are not empty that will be put into the new list.
tempLines = [] #Will hold the new 

#Removes the comments in each of the lines
for x in range(0, len(lines)):
	lines[x] = re.sub("//.*", "", lines[x]) #Removes all comments
	lines[x] = re.sub("\s*", "", lines[x]) #Removes all whitespace
	if(lines[x] != ""): #Removes all blank lines. 
		tempLines.append(lines[x]) 

lines = tempLines #Sets our no blank lines list to the actual list. 

counter = 0;

for line in lines:
	if(line[0] == "("):
		val = len(line) - 1
		t = line[1:val]
		allVals[t] = counter
		#counter = counter - 1
	else:
		counter = counter + 1

for line in lines: #Loops through and assigns instructions
	if(line[0] == "@"): #If the instruction starts with @, do those
		atInstruction(line[1:])
	elif(line[0] == "("):
		pass
	else: #... else do the compute instructions that start with 111
		computeInstruction(line)