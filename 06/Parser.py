"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from re import T
import re
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:`
            input_file (typing.TextIO): input file.
        """
        self.program_lines = []

        # remove spaces and comments 
        for line in input_file.read().splitlines():
            n_line = line.replace(' ', '').split('//', 1)[0]
            if n_line != '':
                self.program_lines.append(n_line)

        self.num_of_lines = len(self.program_lines)
        self.line_counter = 0
        self.current_line = self.program_lines[self.line_counter]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.line_counter < self.num_of_lines

    def advance(self) -> None:
        """Reads the next command from the input and makes it the
        current command. Should be called only if has_more_commands() is true.
        """
        self.line_counter += 1
        if self.line_counter < self.num_of_lines:
            self.current_line = self.program_lines[self.line_counter]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or
            a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx)
            where Xxx is a symbol
        """
        if self.current_line.startswith('@'):
            return "A_COMMAND"
        if self.current_line.startswith('('):
            return "L_COMMAND"
        return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == "A_COMMAND":
            return self.current_line[1:]
        if self.command_type() == "L_COMMAND":
            return self.current_line[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if '=' in self.current_line:
            return self.current_line.split('=', 1)[0]
        return 'null'

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.dest() != 'null':
            tmp_dest = self.current_line.split('=', 1)[1]
            return tmp_dest.split(';', 1)[0]

        else:
            tmp_dest = self.current_line.split(';', 1)[0]
            if tmp_dest == '':
                return 'null'
            return tmp_dest

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if ';' in self.current_line:
            return self.current_line.split(';', 1)[1]
        return 'null'

    def reset(self) -> None:
        """Resets the line_counter of the program
        """
        self.line_counter = -1
        self.advance()
