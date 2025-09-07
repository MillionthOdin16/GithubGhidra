# Ghidra Analysis Export Script
# @category Analysis
# @author MCP Server
# @description Export analysis results to JSON

import json
import os
from ghidra.program.model.symbol import SymbolType
from ghidra.program.model.listing import Function

def get_functions():
    """Get all functions in the program"""
    functions = []
    function_manager = currentProgram.getFunctionManager()
    
    for function in function_manager.getFunctions(True):
        func_data = {
            "name": function.getName(),
            "entry_point": str(function.getEntryPoint()),
            "signature": str(function.getSignature()),
            "parameter_count": function.getParameterCount(),
            "local_variable_count": function.getLocalVariables().length if function.getLocalVariables() else 0,
            "body_size": function.getBody().getNumAddresses() if function.getBody() else 0
        }
        functions.append(func_data)
    
    return functions

def get_symbols():
    """Get all symbols in the program"""
    symbols = []
    symbol_table = currentProgram.getSymbolTable()
    
    for symbol in symbol_table.getAllSymbols(True):
        if symbol.getSymbolType() in [SymbolType.FUNCTION, SymbolType.LABEL, SymbolType.GLOBAL_VAR]:
            sym_data = {
                "name": symbol.getName(),
                "address": str(symbol.getAddress()),
                "type": str(symbol.getSymbolType()),
                "source": str(symbol.getSource())
            }
            symbols.append(sym_data)
    
    return symbols

def get_strings():
    """Get defined strings in the program"""
    strings = []
    listing = currentProgram.getListing()
    
    data_iterator = listing.getDefinedData(True)
    for data in data_iterator:
        if data.hasStringValue():
            string_data = {
                "address": str(data.getAddress()),
                "value": str(data.getValue()),
                "length": data.getLength()
            }
            strings.append(string_data)
    
    return strings

def get_program_info():
    """Get basic program information"""
    return {
        "name": currentProgram.getName(),
        "executable_path": str(currentProgram.getExecutablePath()),
        "image_base": str(currentProgram.getImageBase()),
        "min_address": str(currentProgram.getMinAddress()),
        "max_address": str(currentProgram.getMaxAddress()),
        "language": str(currentProgram.getLanguage()),
        "compiler_spec": str(currentProgram.getCompilerSpec()),
        "creation_date": str(currentProgram.getCreationDate())
    }

def main():
    """Main export function"""
    try:
        # Collect analysis data
        analysis_results = {
            "program_info": get_program_info(),
            "functions": get_functions(),
            "symbols": get_symbols(),
            "strings": get_strings(),
            "analysis_timestamp": str(java.util.Date())
        }
        
        # Write results to JSON file
        project_dir = os.path.dirname(currentProgram.getDomainFile().getPathname())
        output_file = os.path.join(project_dir, "analysis_results.json")
        
        with open(output_file, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        print("Analysis results exported to: " + output_file)
        
    except Exception as e:
        print("Error exporting analysis: " + str(e))

if __name__ == "__main__":
    main()