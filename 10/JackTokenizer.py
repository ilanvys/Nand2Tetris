"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    keywords_set = {'class', 'constructor', 'function', 'method', 'field', 
                    'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                    'false', 'null', 'this', 'let', 'do', 'if', 'else', 
                    'while', 'return'}

    symbol_set = {'{' ,'}', '(', ')', '[', ']', '.', ',', ';', '+', 
                  '-', '*' ,'/' ,'&', '|', '<' ,'>' ,'=' ,'~' ,'^' ,'#'}

    skip_set = {" ", "\t", "\r", "\n"}
    
    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.program_lines = []


        for line in input_stream.read().splitlines():
            n_line = line.strip()
            if n_line != '':
                self.program_lines.append(n_line)
        self.program_str = "\n ".join(self.program_lines)

        # attributes to help parsing the program
        self.char_index = 0
        self.program_str_len = len(self.program_str)
        self.curr_token = ""
        self.curr_token_type = ""
        
        # skip spaces and comments
        self.skip_redundant()

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.char_index >= self.program_str_len:
            return False
        return True

    def skip_redundant(self) -> None:
        """Skips all the comments and spaces that begin from the current
        char_index forward, until finding the begining of a token
        """
        found = True
        while self.has_more_tokens() and found == True:
            if self.program_str[self.char_index] == "/" and self.program_str[self.char_index + 1] == "*":
                # advance until end of comment
                while (self.program_str[self.char_index] + self.program_str[self.char_index + 1]) != "*/":
                    self.char_index += 1
                self.char_index += 2
                found = True
                continue

            if self.program_str[self.char_index] == "/" and self.program_str[self.char_index + 1] == "/":
                # advance until end of line
                while self.char_index < self.program_str_len and self.program_str[self.char_index] != "\n":
                    self.char_index += 1
                self.char_index += 1
                found = True
                continue
                
            if self.program_str[self.char_index] in self.skip_set:
                self.char_index += 1
                found = True
                continue
            
            found = False
    
    def is_sequence_end(self) -> bool:
        if self.program_str[self.char_index] in self.symbol_set or \
                    self.program_str[self.char_index] in self.skip_set or \
                    self.program_str_len <= self.char_index:
            return True
        return False
    
    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        token = ""
        # handle stringConstant
        if self.program_str[self.char_index] == '"':
            self.char_index += 1
            while self.program_str[self.char_index] != '"':
                token += self.program_str[self.char_index]
                self.char_index += 1 
            
            self.curr_token_type = "stringConstant"
            self.char_index += 1

        # handle integerConstant
        elif (self.program_str[self.char_index]).isdigit():
            while (self.program_str[self.char_index]).isdigit():
                token += self.program_str[self.char_index]
                self.char_index += 1 
            self.curr_token_type = "integerConstant"

        # handle symbol
        elif self.program_str[self.char_index] in self.symbol_set:
            token += self.program_str[self.char_index]
            self.char_index += 1
            self.curr_token_type = "symbol"

        # handle identifier or keyword
        else:
            token_found = False
            while not token_found:
                if self.is_sequence_end():
                    token_found = True
                    self.curr_token_type = "identifier"
                else:
                    token += self.program_str[self.char_index]
                    self.char_index += 1
                    if token in self.keywords_set and self.is_sequence_end():
                        token_found = True
                        self.curr_token_type = "keyword"

        self.curr_token = token
        self.skip_redundant()
        
    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        return self.curr_token_type
        
    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.curr_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if self.curr_token == '&':
            return '&amp;'
        elif self.curr_token == '<':
            return '&lt;'
        elif self.curr_token == '>':
            return '&gt;'
        return self.curr_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.curr_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.curr_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.curr_token
