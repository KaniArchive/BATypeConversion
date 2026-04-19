import ctypes
import os
import json

import re

def parse_protocol_enum(filepath="TypeConversion.c"):
    protocols = []
    with open(filepath, 'r') as f:
        content = f.read()
        
    match = re.search(r'typedef enum Protocol__Enum \{(.*?)\}\s+Protocol__Enum;', content, re.DOTALL)
    if not match:
        raise ValueError("Could not find Protocol__Enum in " + filepath)
        
    enum_body = match.group(1)
    
    for line in enum_body.split('\n'):
        line = line.split('//')[0].strip()
        if not line: continue
        if line.endswith(','):
            line = line[:-1].strip()
            
        if '=' in line:
            name, val = line.split('=', 1)
            protocols.append((name.strip(), int(val.strip())))
            
    return protocols

if __name__ == "__main__":
    lib_name = "TypeConversion.dll" if os.name == 'nt' else "TypeConversion.so"
    typeConvert = ctypes.CDLL(os.path.abspath(lib_name))
    typeConvert.TypeConversion.argtypes = [ctypes.c_uint32, ctypes.c_int]
    typeConvert.TypeConversion.restype = ctypes.c_int32
    
    results = []
    protocol_list = parse_protocol_enum("TypeConversion.c")

    for crc in range(0, 99):
        for protocol_name, protocol_value in protocol_list:
            converted_value = typeConvert.TypeConversion(crc, protocol_value)

            results.append({
                "Crc": crc,
                "Protocol": protocol_value,
                "ProtocolName": protocol_name.replace("Protocol__Enum_", ""),
                "Converted_Value": converted_value
            })
    
    with open("ProtocolConversionData.json", 'w') as json_file:
        json.dump(results, json_file, indent=4)

    
    