"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing

from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # initialization
    address_counter = 16
    symbol_table = SymbolTable()
    code = Code()
    p = Parser(input_file)

    # first pass
    command_counter = 0
    while p.has_more_commands():
        if p.command_type() == "L_COMMAND":
            symbol_table.add_entry(p.symbol(), command_counter)
        else:
            command_counter += 1
        
        p.advance()
    
    # second pass
    p.reset()
    binary_line = ''
    while p.has_more_commands():       
        if p.command_type() == "C_COMMAND":
            # add support for shift
            if '<<' in p.comp() or '>>' in p.comp():
                binary_line = '101' 
            else:
                binary_line = '111'
           
            binary_line += code.comp(p.comp()) + \
                    code.dest(p.dest()) + code.jump(p.jump())
                
        if p.command_type() == "L_COMMAND":
            p.advance()
            continue
        
        if p.command_type() == "A_COMMAND":
            if (p.symbol()).isdigit():
                binary_line = '0' + code.to_binary(p.symbol())
            else:
                if not symbol_table.contains(p.symbol()):
                    symbol_table.add_entry(p.symbol(), address_counter)
                    address_counter += 1

                address = symbol_table.get_address(p.symbol())
                binary_line = '0' + code.to_binary(str(address))
        
        output_file.write(binary_line + '\n')
        p.advance()

if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
