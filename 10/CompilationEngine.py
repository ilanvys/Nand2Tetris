"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer


class CompilationEngine:
    """Gets input from a Jackt and emits its parsed structure into an
    output stream.
    """
    op_set = { '+', '-', '*' ,'/' ,'&amp;', '|' ,'&gt;' ,'&lt;' ,'=' ,'^' ,'#'}
    
    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.output = output_stream
        self.tokenizer = input_stream
        self.tokenizer.advance()
        self.compile_class()
    
    def write_symbol(self) -> None:
        self.write_tags(self.tokenizer.symbol(), "symbol")
    
    def write_identifier(self) -> None:
        self.write_tags(self.tokenizer.identifier(), "identifier")

    def write_keyword(self) -> None:
        self.write_tags(self.tokenizer.keyword(), "keyword")

    def write_int_val(self) -> None:
        self.write_tags(self.tokenizer.int_val(), "integerConstant")

    def write_string_val(self) -> None:
        self.write_tags(self.tokenizer.string_val(), "stringConstant")

    def write_tags(self, token: str, token_type: str) -> None:
        self.output.write("<" + token_type + "> " + \
                            str(token) + \
                            " </" + token_type + ">\n")
        
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def open_tag(self, name: str) -> None:
        self.output.write("<" + name + ">\n")

    def close_tag(self, name: str) -> None:
        self.output.write("</" + name + ">\n")

    def write_brackets(self) -> None:
        if self.tokenizer.symbol() == "{":
            self.write_symbol()
            self.compile_statements()
        else:
            self.write_symbol()
            self.compile_expression()

        self.write_symbol()
        
    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.open_tag("class")
        self.write_keyword()
        self.write_identifier()
        self.write_symbol()
        
        while self.tokenizer.token_type() == "keyword" and self.tokenizer.keyword() in ["static", "field"]:
            self.compile_class_var_dec()
        while self.tokenizer.token_type() == "keyword" and self.tokenizer.keyword() in ["constructor", "function", "method"]:
            self.compile_subroutine()
        
        self.write_symbol()
        self.close_tag("class")
        
    def compile_type(self) -> None:
        if self.tokenizer.token_type() == "keyword":
            self.write_keyword()
        else:
            self.write_identifier()

    def compile_class_var_dec(self) -> None:
        self.open_tag("classVarDec")
        self.write_keyword()
        self.compile_type()
        self.write_identifier()
        while self.tokenizer.symbol() == ",":
            self.write_symbol()
            self.write_identifier()

        self.write_symbol()
        self.close_tag("classVarDec")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.open_tag("subroutineDec")
        
        # subroutine declaration
        self.write_keyword()
        self.compile_type()
        self.write_identifier()
        self.write_symbol()

        # subroutine parameters
        self.compile_parameter_list()
        self.write_symbol()

        # subroutine body
        self.compile_subroutine_body()
        self.close_tag("subroutineDec")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.open_tag("parameterList")
        if self.tokenizer.symbol() != ")":
            self.compile_type()
            self.write_identifier()
        
        # add more parameters
        while self.tokenizer.symbol() != ")":
            self.write_symbol()
            self.compile_type()
            self.write_identifier()
            
        self.close_tag("parameterList")

    def compile_subroutine_body(self) -> None:
        self.open_tag("subroutineBody")
        
        self.write_symbol()
        while self.tokenizer.keyword() == "var":
            self.compile_var_dec()
        
        self.compile_statements()
        self.write_symbol()
        self.close_tag("subroutineBody")
    
    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.open_tag("varDec")
        self.write_keyword()
        self.compile_type()
        self.write_identifier()
        while self.tokenizer.symbol() == ",":
            self.write_symbol()
            self.write_identifier()
        
        self.write_symbol()
        self.close_tag("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.open_tag("statements")
        while self.tokenizer.token_type() == "keyword" and self.tokenizer.keyword() in ["let", "if", "while", "do", "return"]:
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
        
        self.close_tag("statements")

    def output_subroutine_call(self) -> None:
        if self.tokenizer.symbol() == ".":
            self.write_symbol()
            self.write_identifier() 
        
        self.write_symbol()
        self.compile_expression_list()   
        self.write_symbol()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.open_tag("doStatement")
        self.write_keyword()
        self.write_identifier()
        self.output_subroutine_call()
        self.write_symbol()
        self.close_tag("doStatement")
    
    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.open_tag("letStatement")
        self.write_keyword()
        self.write_identifier()
        if self.tokenizer.symbol() == "[":
            self.write_brackets() # [expression]

        self.write_symbol()
        self.compile_expression()
        self.write_symbol()
        self.close_tag("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.open_tag("whileStatement")
        self.write_keyword()
        self.write_brackets() # (expression)
        self.write_brackets() # {statements}
        self.close_tag("whileStatement")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.open_tag("returnStatement")
        self.write_keyword()
        if self.tokenizer.token_type() == "symbol" and self.tokenizer.symbol() == ";":
            self.write_symbol()
        else:
            self.compile_expression()
            self.write_symbol()

        self.close_tag("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.open_tag("ifStatement")
        self.write_keyword()
        self.write_brackets() # (expression)
        self.write_brackets() # {statements}
        if self.tokenizer.token_type() == "keyword" and self.tokenizer.keyword() == "else":
            self.write_keyword()
            self.write_brackets() # {statements}

        self.close_tag("ifStatement")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.open_tag("expression")
        self.compile_term()
        while self.tokenizer.symbol() in self.op_set:
            self.write_symbol()
            self.compile_term()

        self.close_tag("expression")
        
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
        self.open_tag("term")
        if self.tokenizer.token_type() == "integerConstant":
            self.write_int_val()
        
        elif self.tokenizer.token_type() == "stringConstant":
            self.write_string_val()
        
        elif self.tokenizer.token_type() == "keyword":
            self.write_keyword()
        
        elif self.tokenizer.token_type() == "symbol":
            if self.tokenizer.symbol() == "(":
                self.write_brackets() # (expression)
            else:
                self.write_symbol()
                self.compile_term()
        else:
            self.write_identifier()
            if self.tokenizer.symbol() == "[":
                self.write_brackets() # [expression]
            elif self.tokenizer.symbol() in ["(", "."]:
                self.output_subroutine_call()

        self.close_tag("term")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.open_tag("expressionList")
        if self.tokenizer.symbol() != ")":
            self.compile_expression()
            while self.tokenizer.symbol() != ")":
                self.write_symbol()
                self.compile_expression()

        self.close_tag("expressionList")
