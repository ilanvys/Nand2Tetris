"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.__output = output_stream
        self.__label_counter = 0
        self.__filename = ''

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.__filename = filename
    
    def write_basic_push(self) -> None:
        self.__output.write("D=M\n" + 
                            "@SP\n" + 
                            "A=M\n" + 
                            "M=D\n" + 
                            "@SP\n" +
                            "M=M+1\n")
        
    def write_constant_push(self, index: int) -> None:
        self.__output.write("@" + str(index) + "\n" + 
                            "D=A\n" + 
                            "@SP\n" + 
                            "A=M\n" + 
                            "M=D\n" + 
                            "@SP\n" + 
                            "M=M+1\n")
    
    def write_basic_pop(self) -> None:
        self.__output.write("D=A\n" +
                            "@R13\n" +
                            "M=D\n" +
                            "@SP\n" +
                            "M=M-1\n" +
                            "A=M\n" +
                            "D=M\n" +
                            "@R13\n" +
                            "A=M\n" +
                            "M=D\n")
        
    def write_static_pop(self, index: int) -> None:
        self.__output.write("@SP\n" + 
                            "M=M-1\n" + 
                            "A=M\n" + 
                            "D=M\n" + 
                            "@" + self.__filename + "." + str(index) + "\n" + 
                            "M=D\n")
    
    def write_segment_index(self, index: int) -> None:
        self.__output.write("D=A\n" +
                            "@" + str(index) + "\n" +
                            "A=A+D\n")

    def write_add_sub(self, operator: str) -> None:
        self.__output.write("@SP \n" +
                            "A=M\n" +
                            "A=A-1\n" +
                            "D=M\n" +
                            "A=A-1\n" +
                            "M=M" + operator + "D\n" +
                            "@SP\n" +
                            "M=M-1\n")

    def write_cmp(self, jump_comm: str) -> None:
        if jump_comm == "JGT":
            jump_val = ["-1", "0"]
        elif jump_comm == "JLT":
            jump_val = ["0", "-1"]
        else:
            jump_val = ["0", "0"]

        unique_label = str(self.__label_counter) + "." + self.__filename
        self.__output.write("@SP\n" +
                            "A=M\n" +
                            "A=A-1\n" +
                            "D=M\n" +
                            "@R14\n" +
                            "M=D\n" +
                            "@SP\n" +
                            "A=M\n" +
                            "A=A-1\n" +
                            "A=A-1\n" +
                            "D=M\n" +
                            "@R13\n" +
                            "M=D\n" +
                            "@X_POS" +  unique_label + "\n" +
                            "D;JGE\n" +
                            "@X_NEG" +  unique_label + "\n" +
                            "0;JMP\n")
        self.__output.write("(X_POS" + unique_label + ")\n" +
                            "@R14\n" +
                            "D=M\n" +
                            "@EQ_SIGN" + unique_label + "\n" +
                            "D;JGE\n" +
                            "@X_POS_Y_NEG" + unique_label + "\n" +
                            "0;JMP\n")
        self.__output.write("(X_NEG" + unique_label + ")\n" +
                            "@R14\n" +
                            "D=M\n" +
                            "@X_NEG_Y_POS" + unique_label + "\n" +
                            "D;JGE\n" +
                            "@EQ_SIGN" + unique_label + "\n" +
                            "0;JMP\n")
        self.__output.write("(X_POS_Y_NEG" + unique_label + ")\n" + 
                            "@SP\n" +
                            "M=M-1\n" +
                            "A=M\n" +
                            "A=A-1\n" + 
                            "M=" + jump_val[0] + "\n" +  
                            "@ENDCMP" + unique_label + "\n" + 
                            "0;JMP\n")
        self.__output.write("(X_NEG_Y_POS" + unique_label + ")\n" + 
                            "@SP\n" +
                            "M=M-1\n" +
                            "A=M\n" +
                            "A=A-1\n" + 
                            "M=" + jump_val[1] + "\n" +  
                            "@ENDCMP" + unique_label + "\n" + 
                            "0;JMP\n")
        self.__output.write("(EQ_SIGN" + unique_label + ")\n" +
                            "@R14\n" +
                            "D=M\n" +
                            "@R13\n" +
                            "D=M-D\n" +
                            "@TRUE" + unique_label + "\n" +
                            "D;" + jump_comm + "\n" +
                            "@SP\n" +
                            "M=M-1\n" +
                            "A=M\n" +
                            "A=A-1\n" + 
                            "M=0\n" + 
                            "@ENDCMP" + unique_label + "\n" +
                            "0;JMP\n" +
                            "(TRUE" + unique_label + ")\n" +
                            "@SP\n" +
                            "M=M-1\n" +
                            "A=M\n" +
                            "A=A-1\n" + 
                            "M=-1\n" + 
                            "(ENDCMP" + unique_label + ")\n")
        self.__label_counter += 1

    def write_and_or(self, operator: str) -> None:
        self.__output.write("@SP\n" +
                            "A=M\n" +
                            "A=A-1\n" +
                            "D=M\n" +
                            "A=A-1\n" +
                            "M=D" + operator + "M\n" +
                            "@SP\n" +
                            "M=M-1\n")

    def write_neg_not(self, operator: str) -> None:
        self.__output.write("@SP\n" +
                            "A=M\n" + 
                            "A=A-1\n" + 
                            "M=" + operator + "M\n")

    def write_shift(self, operator: str) -> None:
        self.__output.write("@SP\n" + 
                            "A=M\n" + 
                            "A=A-1\n" + 
                            "M=" + "M" + operator + "\n")
    
    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        if command == "add":
             self.write_add_sub("+")
        elif command == "sub":
            self.write_add_sub("-")
        elif command == "eq":
            self.write_cmp("JEQ")
        elif command == "gt":
            self.write_cmp("JGT")
        elif command == "lt":
            self.write_cmp("JLT")
        elif command == "and":
            self.write_and_or("&")
        elif command == "or":
            self.write_and_or("|")
        elif command == "neg":
            self.write_neg_not("-")
        elif command == "not":
            self.write_neg_not("!")
        elif command == "shiftleft":
            self.write_shift("<<")
        elif command == "shiftright":
            self.write_shift(">>")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        seg_dict = {"local": "LCL", "argument": "ARG", "this": "THIS",
                    "that": "THAT", "temp": "5", "pointer": "3"}
        
        if segment in ["local", "argument", "this", "that", "temp", "pointer"]:
            self.__output.write("@" + seg_dict[segment] + "\n")
            
            if segment not in ["temp", "pointer"]:
                self.__output.write("A=M\n")
            
            self.write_segment_index(index)
            if command == "C_PUSH":
                self.write_basic_push()
            else:
                self.write_basic_pop()
                
        elif segment == "constant":
            self.write_constant_push(index)
        
        elif segment == "static":
            if command == "C_PUSH":
                self.__output.write("@" + self.__filename + "." + str(index) + "\n")
                self.write_basic_push()
            else:
                self.write_static_pop(index)

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass
    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        pass
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass
