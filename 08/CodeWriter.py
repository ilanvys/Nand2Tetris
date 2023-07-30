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
        self.__func_counter = 0
        self.__filename = ''
        self.__curr_func = ''

    def boot_write(self) -> None:
        self.__output.write("@256\n" + 
                            "D=A\n" + 
                            "@SP\n" + 
                            "M=D\n")
        self.write_call("Sys.init", 0)

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
        symbol_to_write = self.__filename + "." + self.__curr_func + "$" + label
        self.__output.write("(" + symbol_to_write + ")\n")
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        symbol_to_write = self.__filename + "." + self.__curr_func + "$" + label
        self.__output.write("@" + 
                            symbol_to_write + 
                            "\n" + 
                            "0;JMP\n")
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        symbol_to_write = self.__filename + "." + self.__curr_func + "$" + label
        self.__output.write("@SP\n" + 
                            "M=M-1\n" + 
                            "A=M\n" + 
                            "D=M\n" + 
                            "@" + 
                            symbol_to_write + 
                            "\n" + 
                            "D;JNE\n")

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
        self.__curr_func = function_name
        self.__output.write("(" + self.__curr_func + ")\n")
        for i in range(n_vars):
            self.write_push_pop("C_PUSH", "constant", 0)

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
        self.__func_counter += 1
        label = self.__filename + "." + function_name + "$" + "returnAddress." + str(self.__func_counter)

        # generates a label and pushes it to the stack
        self.__output.write("@" + 
                            label + 
                            "\n" + 
                            "D=A\n" + 
                            "@SP\n" + 
                            "A=M\n" + 
                            "M=D\n" + 
                            "@SP\n" + 
                            "M=M+1\n")

        # saves LCL, ARG, THIS, THAT of the caller
        for seg in ["@LCL", "@ARG", "@THIS", "@THAT"]:
            self.__output.write(seg + 
                                "\n" + 
                                "D=M\n" + 
                                "@SP\n" + 
                                "A=M\n" + 
                                "M=D\n" + 
                                "@SP\n" + 
                                "M=M+1\n")

        # repositions ARG
        self.__output.write("@SP\n" + 
                            "D=M\n" + 
                            "@" + 
                            str(n_args+5) + 
                            "\n" + 
                            "D=D-A\n" + 
                            "@ARG\n" + 
                            "M=D\n")

        # repositions LCL
        self.__output.write("@SP\n" + 
                            "D=M\n" + 
                            "@LCL\n" + 
                            "M=D\n")

        # transfers control to the callee
        self.__output.write("@" + 
                            function_name + 
                            "\n" + 
                            "0;JMP\n")

        # injects the return address label into the code
        self.__output.write("(" + label + ")\n")
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        
        # sets the end frame
        self.__output.write("@LCL\n" + 
                            "D=M\n" + 
                            "@R13\n" + 
                            "M=D\n")

        # puts the return address in a temp var
        self.__output.write("@R13\n" + 
                            "D=M\n" + 
                            "@5\n" + 
                            "D=D-A\n" + 
                            "A=D\n" + 
                            "D=M\n" + 
                            "@R14\n" + 
                            "M=D\n")

        # repositions the return value for the caller
        self.__output.write("@SP\n" + 
                            "M=M-1\n" + 
                            "A=M\n" + 
                            "D=M\n" + 
                            "@ARG\n" + 
                            "A=M\n" + 
                            "M=D\n")
       
        # repositions SP for the caller
        self.__output.write("@ARG\n" + 
                            "D=M\n" + 
                            "D=D+1\n" + 
                            "@SP\n" + 
                            "M=D\n")
        
        # restores THAT, THIS, ARG, LCL for the caller
        for seg in ["@THAT", "@THIS", "@ARG", "@LCL"]:
            self.__output.write("@R13\n" + 
                                "M=M-1\n" + 
                                "A=M\n" + 
                                "D=M\n" + 
                                seg + 
                                "\n" + 
                                "M=D\n")
        
        # go to the return address
        self.__output.write("@R14\n" + 
                            "A=M\n" + 
                            "0;JMP\n")
        