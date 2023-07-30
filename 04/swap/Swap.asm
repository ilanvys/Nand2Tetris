// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

//init i with array length
    @R15
    D=M
    @i
    M=D
    @curr_add
    M=0

// init max value and min value
    @R14
    A=M
    D=M
    @maxval
    M=D
    @minval
    M=D

//init max address and min address
    @R14
    D=M
    @maxadd
    M=D
    @minadd
    M=D

//iterate over every value of the array
(LOOP)
    @i
    M=M-1
    D=M
    @SWAP
    D;JEQ
    @R14
    D=M
    @i
    D=D+M
    @curr_add
    M=D

//check if the current value > maxval
    @maxval
    D=M
    @curr_add
    A=M
    D=D-M
    @SWAP_MAX
    D;JLT

//check if the current value < minval
    @minval
    D=M
    @curr_add
    A=M
    D=D-M
    @SWAP_MIN
    D;JGT

    @LOOP
    0;JMP

//swap the stored max value
(SWAP_MAX)
    @curr_add
    D=M
    @maxadd
    M=D
    @curr_add
    A=M
    D=M
    @maxval
    M=D
    @LOOP
    0;JMP

//swap the stored min value
(SWAP_MIN)
    @curr_add
    D=M
    @minadd
    M=D
    @curr_add
    A=M
    D=M
    @minval
    M=D
    @LOOP
    0;JMP

//swap the min and max values of the array
(SWAP)
    @minval
    D=M
    @maxadd
    A=M
    M=D
    @maxval
    D=M
    @minadd
    A=M
    M=D
    @END
    0;JMP

(END)
    0;JMP



