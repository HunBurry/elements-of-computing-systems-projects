// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(READ)
	@KBD           	//Jump to keyboard
	D=M 			//Put keyboard value into D
	@BLACK 			
	D;JNE			//If anything is in the keyboard, jump to black color
	@WHITE
	0;JMP 			//Else go to white color
(BLACK)
	D=-1 			//Put color in D register
	@color
	M=D 			//Store color in @color address
	@LOOPSTART
	0;JMP
(WHITE)
	D=0 			//Put color in D register
	@color
	M=D  			//Store color in @color address
	@LOOPSTART
	0;JMP
(LOOPSTART)
	@SCREEN	 		//Starts out the loop at the first location in 
	D=A
	@pointer 
	M=D
(LOOP)
	@color
	D=M
	@pointer
	A=M
	M=D 			//Puts color in memory at pixel location
	D=A+1 			//Sets the current location to the D register
	@pointer 		//Go to the @pointer variable
	M=D 			//Sets the address+1 in memory
	@KBD
	D=D-A			//Checks to see if the upcoming address is out of bounds
	@READ
	D;JEQ			//If the upcoming address is out of bounds read the keyboard
	@color
	D=M 			//Load the color into memory
	@pointer
	A=M 			//Sets the address to the next point
	@LOOP
	0;JMP 			//Go back to the start of the loop



