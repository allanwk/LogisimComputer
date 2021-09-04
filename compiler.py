import pandas as pd
import numpy as np
import sys

#Get instruction codes from spreadsheet
df = pd.read_excel('16bit_set.xlsx', dtype=str)
df = df.set_index(df['Instruction'])
instructions = pd.unique(df['Instruction'])

codes = {}
for instruction in instructions[1:]:
    codes[instruction] = df.loc[instruction, ['Code']].iloc[0]['Code']

def compile(filename):
    """
    Compiles a simple language containing labels, jumps (gotos) and constants,
    generating a text file with hex values for the computer RAM.
    """

    with open(filename, 'r') as file:
        lines = file.read().splitlines()
    var_address = 192
    constants = {}
    memory = {}
    labels = {}
    instruction_address_counter = 0

    #Extract constants and commands
    const = [line.split('//')[0].strip() for line in lines if line != '' and '=' in line]
    commands = [line.split('//')[0].strip() for line in lines if line != '' and '=' not in line]
    
    #Map constants to memory
    for c in const:
        name, value = c.replace(" ", "").split("=")
        constants[name] = var_address
        memory[var_address] = hex(int(value))[2:].zfill(4)
        var_address += 1

    #Map labels to memory
    for index, line in enumerate(commands):
        if ':' in line:
            label = line[:line.index(':')]
            labels[label] = var_address
            memory[var_address] = hex(int(index))[2:].zfill(4)
            var_address += 1
            commands[index] = commands[index].split(':')[1].strip()
    
    """For each line, create a binary string containing 8 instruction bits
    and 8 address bits. Convert this string to hex and save to memory dict.
    The mrmory dict is used to generate a numpy array, which is saved as
    the RAM.txt file.
    """
    for line in commands:
        l = line.split(" ")
        hex_str = ""

        if len(l) == 2:
            instruction, operand = l
            binary_str = codes[instruction]
            if operand in labels:
                binary_str += bin(int(labels[operand]))[2:].zfill(8)
            elif operand in constants:
                binary_str += bin(int(constants[operand]))[2:].zfill(8)
            else:
                memory[var_address] = hex(int(operand))[2:].zfill(4)
                constants[operand] = var_address
                var_address += 1
                binary_str += bin(int(constants[operand]))[2:].zfill(8)
            
            hex_str = hex(int(binary_str, 2))[2:].zfill(4)
                

        else:
            instruction = l[0]
            binary_str = codes[instruction] + "0"*8
            hex_str = hex(int(binary_str, 2))[2:].zfill(4)
        
        memory[instruction_address_counter] = hex_str
        instruction_address_counter += 1

    arr = np.full((1,256), '0', dtype=np.dtype('U100'))
    for key, value in memory.items():
        arr[0,key] = value
    arr = arr.reshape(16,16)

    np.savetxt('RAM.txt', arr, delimiter=' ', fmt='%s')

    with open('RAM.txt', 'r+') as f:
        line = 'v2.0 raw'
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

    print("Compiled to RAM.txt")   

if __name__ == '__main__':
    compile(sys.argv[1])