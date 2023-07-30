"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer
import SymbolTable
import VMWriter

class CompilationEngine:

    """Gets input from a Jackt and emits its parsed structure into an
    output stream.
    """
    un_op_dict = {'-':'neg', '~':'not'}
    bin_op_dict = { '+':'add', '-':'sub', '*': 'Math.multiply','/':'Math.divide' ,'&amp;':'and', '|':'or' 
    ,'&gt;':'gt' ,'&lt;':'lt' ,'=':'eq' ,'^':'leftshift' ,'#':'rightshift'}
    
    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.output = output_stream
        self.tokenizer = input_stream
        self.class_name = ""
        self.label_counter = 0
        self.sym_table = SymbolTable.SymbolTable()
        self.vm_writer = VMWriter.VMWriter(output_stream)

        self.tokenizer.advance() 
        self.compile_class()
        
    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.tokenizer.advance() #class
        self.class_name = self.tokenizer.identifier()
        self.tokenizer.advance() #className
        self.tokenizer.advance() #{
        
        while self.tokenizer.token_type() == "keyword" and \
                self.tokenizer.keyword() in ["static", "field"]:
            self.compile_class_var_dec()
        
        while self.tokenizer.token_type() == "keyword" and \
                self.tokenizer.keyword() in ["constructor", "function", "method"]:
            self.compile_subroutine() 
              
    def compile_type(self) -> str:
        if self.tokenizer.token_type() == "keyword":
            return self.tokenizer.keyword()
        else:
            return self.tokenizer.identifier()

    def compile_class_var_dec(self) -> None:
        curr_kind = self.tokenizer.keyword()
        self.tokenizer.advance() #static|field
        curr_type = self.compile_type()
        self.tokenizer.advance() #type
        self.sym_table.define(self.tokenizer.identifier(), curr_type, curr_kind)
        self.tokenizer.advance() #varName

        while self.tokenizer.symbol() == ",":
            self.tokenizer.advance() #,
            self.sym_table.define(self.tokenizer.identifier(), curr_type, curr_kind)
            self.tokenizer.advance() #varName

        self.tokenizer.advance() #;

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # subroutine declaration
        curr_sub_type = self.tokenizer.keyword() 
        self.sym_table.start_subroutine()
        if curr_sub_type == "method":
            self.sym_table.define("this", self.class_name, "argument")    
        
        self.tokenizer.advance() #function|constructor|method
        self.tokenizer.advance() #void|type
        curr_func_name = self.tokenizer.identifier()
        self.tokenizer.advance() #subroutineName
        self.tokenizer.advance() #(

        # subroutine parameters
        self.compile_parameter_list()
        self.tokenizer.advance() #)

        # subroutine body
        self.compile_subroutine_body(curr_sub_type, curr_func_name)

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        if self.tokenizer.symbol() != ")":
            curr_type = self.compile_type()
            self.tokenizer.advance() #type
            self.sym_table.define(self.tokenizer.identifier(), curr_type, "argument")
            self.tokenizer.advance() #varName
        
        # add more parameters
        while self.tokenizer.symbol() != ")":
            self.tokenizer.advance() #,
            self.curr_type = self.compile_type()
            self.tokenizer.advance() #type
            self.sym_table.define(self.tokenizer.identifier(), curr_type, "argument")
            self.tokenizer.advance() #varName

    def compile_subroutine_body(self, sub_type: str, func_name: str) -> None:
        self.tokenizer.advance() #{
        while self.tokenizer.keyword() == "var":
            self.compile_var_dec()
        
        self.vm_writer.write_function(self.class_name + "." + func_name, self.sym_table.var_count("var"))
        if sub_type == "method":
            self.sym_table.define("this", self.class_name, "argument")
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)
        
        elif sub_type == "constructor":
            self.vm_writer.write_push("constant", self.sym_table.var_count("field"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
        
        self.compile_statements()
        self.tokenizer.advance() #}
    
    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.tokenizer.advance() #var
        curr_type = self.compile_type()
        self.tokenizer.advance() #type
        self.sym_table.define(self.tokenizer.identifier(), curr_type, "var")
        self.tokenizer.advance() #varName
        while self.tokenizer.symbol() == ",":
            self.tokenizer.advance() #,
            self.sym_table.define(self.tokenizer.identifier(), curr_type, "var")
            self.tokenizer.advance() #varName
        
        self.tokenizer.advance() #;

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.tokenizer.token_type() == "keyword" and \
                self.tokenizer.keyword() in ["let", "if", "while", "do", "return"]:
            if self.tokenizer.keyword() == "let":
                self.compile_let()
            elif self.tokenizer.keyword() == "if":
                self.compile_if()
            elif self.tokenizer.keyword() == "while":
                self.compile_while()
            elif self.tokenizer.keyword() == "do":
                self.compile_do()
            else:
                self.compile_return()
        
    def compile_subroutine_call(self) -> None:
        add_arg = 0
        curr_sub_name = ""
        if self.tokenizer.peek() == ".":
            if self.sym_table.kind_of(self.tokenizer.identifier()) in ["local", "this"]:
                self.vm_writer.write_push(self.sym_table.kind_of(self.tokenizer.identifier()), 
                                            self.sym_table.index_of(self.tokenizer.identifier()))
                curr_sub_name = self.sym_table.type_of(self.tokenizer.identifier())
                add_arg += 1
            else:
                curr_sub_name = self.tokenizer.identifier()

            self.tokenizer.advance() #className|varName
            curr_sub_name += "."
            self.tokenizer.advance() #.
            curr_sub_name += self.tokenizer.identifier()
        
        else:
            self.vm_writer.write_push("pointer", 0)
            curr_sub_name = self.class_name + "." + self.tokenizer.identifier()
            add_arg += 1

        self.tokenizer.advance() #subroutineName
        self.tokenizer.advance() #(
        arg_num = self.compile_expression_list() + add_arg   
        self.tokenizer.advance() #)
        self.vm_writer.write_call(curr_sub_name, arg_num)
        
    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.tokenizer.advance() #do
        self.compile_subroutine_call()
        self.vm_writer.write_pop("temp", 0)
        self.tokenizer.advance() #;
    
    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.tokenizer.advance() #let
        curr_var_name = self.tokenizer.identifier()
        var_kind = self.sym_table.kind_of(curr_var_name)
        var_index = self.sym_table.index_of(curr_var_name)
        self.tokenizer.advance() #varName
        if self.tokenizer.symbol() == "[":
            self.tokenizer.advance() #[
            self.compile_expression()
            self.tokenizer.advance() #]
            self.vm_writer.write_push(var_kind, var_index)
            self.vm_writer.write_arithmetic("add")
            self.tokenizer.advance() #=
            self.compile_expression()
            self.tokenizer.advance() #;
            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)

        else:
            self.tokenizer.advance() #=
            self.compile_expression()
            self.tokenizer.advance() #;
            self.vm_writer.write_pop(var_kind, var_index)

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.tokenizer.advance() #while
        self.tokenizer.advance() #(
        curr_label_counter = self.label_counter
        self.label_counter += 1
        self.vm_writer.write_label("WHILE_EXP" + str(curr_label_counter))
        self.compile_expression()
        self.tokenizer.advance() #)
        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if("WHILE_END" + str(curr_label_counter))
        self.tokenizer.advance() #{
        self.compile_statements()
        self.tokenizer.advance() #}
        self.vm_writer.write_goto("WHILE_EXP" + str(curr_label_counter))
        self.vm_writer.write_label("WHILE_END" + str(curr_label_counter))
               
    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.tokenizer.advance() #return
        if self.tokenizer.token_type() == "symbol" and self.tokenizer.symbol() == ";":
            self.vm_writer.write_push("constant", 0)
        else:
            self.compile_expression()
        
        self.vm_writer.write_return()
        self.tokenizer.advance() #;

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        curr_label_counter = self.label_counter
        self.label_counter += 1
        self.tokenizer.advance() #if
        self.tokenizer.advance() #(
        self.compile_expression()
        self.tokenizer.advance() #)
        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if("IF_FALSE" + str(curr_label_counter))
        self.tokenizer.advance() #{
        self.compile_statements()
        self.tokenizer.advance() #}
        self.vm_writer.write_goto("IF_TRUE" + str(curr_label_counter))
        self.vm_writer.write_label("IF_FALSE" + str(curr_label_counter))
        if self.tokenizer.token_type() == "keyword" and self.tokenizer.keyword() == "else":
            self.tokenizer.advance() #else
            self.tokenizer.advance() #{
            self.compile_statements()
            self.tokenizer.advance() #}
        
        self.vm_writer.write_label("IF_TRUE" + str(curr_label_counter))

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self.tokenizer.symbol() in self.bin_op_dict:
            op = self.tokenizer.symbol()
            self.tokenizer.advance() #operator
            self.compile_term()
            if op == "*" or op == "/":
                self.vm_writer.write_call(self.bin_op_dict[op], 2)
            else:
                self.vm_writer.write_arithmetic(self.bin_op_dict[op])
        
    def compile_term(self) -> None:
        """Compiles a term. 
        
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        if self.tokenizer.token_type() == "integerConstant":
            self.vm_writer.write_push("constant", self.tokenizer.int_val())
            self.tokenizer.advance() #integerConstant    
        
        elif self.tokenizer.token_type() == "stringConstant":
            str_len = len(self.tokenizer.string_val())
            self.vm_writer.write_push("constant", str_len)
            self.vm_writer.write_call("String.new", 1)
            for i in range(str_len):
                self.vm_writer.write_push("constant", ord(self.tokenizer.string_val()[i]))
                self.vm_writer.write_call("String.appendChar", 2)
            
            self.tokenizer.advance() #stringConstant
        
        elif self.tokenizer.token_type() == "keyword":
            if self.tokenizer.keyword() in ["true", "false"]:
                self.vm_writer.write_bool(self.tokenizer.keyword())
            elif self.tokenizer.keyword() == "this":
                self.vm_writer.write_push("pointer", 0)
            elif self.tokenizer.keyword() == "null":
                self.vm_writer.write_push("constant", 0)
           
            self.tokenizer.advance() #keyword
        
        elif self.tokenizer.token_type() == "symbol":
            if self.tokenizer.symbol() == "(":
                self.tokenizer.advance() #(
                self.compile_expression()
                self.tokenizer.advance() #)
            else:
                op = self.tokenizer.symbol()
                self.tokenizer.advance() #operator
                self.compile_term()
                self.vm_writer.write_arithmetic(self.un_op_dict[op])

        else:
            if self.tokenizer.peek() in ["(", "."]:
                self.compile_subroutine_call()
            else:
                self.vm_writer.write_push(self.sym_table.kind_of(self.tokenizer.identifier()), 
                                            self.sym_table.index_of(self.tokenizer.identifier()))
                self.tokenizer.advance() #varName

                if self.tokenizer.symbol() == "[":
                    self.compile_array()

    def compile_array(self) -> None:
        self.tokenizer.advance() #[
        self.compile_expression()
        self.tokenizer.advance() #]
        self.vm_writer.write_arithmetic("add")
        self.vm_writer.write_pop("pointer", 1)
        self.vm_writer.write_push("that", 0)

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        arg_num = 0
        if self.tokenizer.symbol() != ")":
            arg_num += 1
            self.compile_expression()
            while self.tokenizer.symbol() != ")":
                arg_num += 1
                self.tokenizer.advance() #,
                self.compile_expression()
        
        return arg_num
