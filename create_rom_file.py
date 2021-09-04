import pandas as pd
import numpy as np
from tqdm import tqdm

#Opening spreadsheet containing instruction codes and control words
df = pd.read_excel('16bit_set.xlsx', dtype=str)
n_instructions = len(df)

#Creating multiples for handling flag signals
df = pd.concat([df]*32, ignore_index=True)

#List of all possibilities for the 5 flag bits
flags_list = [bin(i)[2:].zfill(5) for i in range(pow(2, 5))]
flags_df = pd.DataFrame(np.repeat(flags_list, n_instructions, axis=0), columns=['Flags'])

#Check if flag at given position is set
def check_flag(string, index):
    return string[-(index + 1)] == '1'

#Combining instruction dataframe with flags and organizing columns
df = pd.concat([df, flags_df], axis=1)
cols = df.columns.tolist()
cols = cols[:3] + cols[-1:] + cols[3:-1]
df = df[cols]

#Getting ROM addresses in decimal to create Logisim memory file
data = {}
converted_addr = []
for index, row in df[['Code', 'Step', 'Flags']].iterrows():
    dec_addr = int(str(row['Code']) + str(row['Step']) + str(row['Flags']), base=2)
    data[dec_addr] = 0
    converted_addr.append(dec_addr)

df['Code'] = converted_addr

#Setting microcode for conditional jumps
for i in tqdm(range(len(df))):
    if df.loc[i, ['Instruction']]['Instruction'] == 'JEQ' and check_flag(df.loc[i, ['Flags']]['Flags'], 2) and df.loc[i, ['Step']]['Step'] == '011':
        df.loc[i, ['RO']] = 1
        df.loc[i, ['J']] = 1
    elif df.loc[i, ['Instruction']]['Instruction'] == 'JG' and check_flag(df.loc[i, ['Flags']]['Flags'], 3) and df.loc[i, ['Step']]['Step'] == '011':
        df.loc[i, ['RO']] = 1
        df.loc[i, ['J']] = 1
    elif df.loc[i, ['Instruction']]['Instruction'] == 'JL' and check_flag(df.loc[i, ['Flags']]['Flags'], 4) and df.loc[i, ['Step']]['Step'] == '011':
        df.loc[i, ['RO']] = 1
        df.loc[i, ['J']] = 1
    elif df.loc[i, ['Instruction']]['Instruction'] == 'JC' and check_flag(df.loc[i, ['Flags']]['Flags'], 0) and df.loc[i, ['Step']]['Step'] == '011':
        df.loc[i, ['RO']] = 1
        df.loc[i, ['J']] = 1

#Generating microcode from columns and saving to data dict
for index, row in df.iterrows():
    binary_str = ""
    for col in df.columns[4:]:
        binary_str += str(row[col])

    data[row['Code']] = hex(int(binary_str, base=2))

#Converting data to array and save to text file
arr = np.full((1,pow(2, 16)), '0', dtype=np.dtype('U100'))
for key, value in data.items():
    arr[0,key] = value.split('x')[1]
arr = arr.reshape(4096,16)
np.savetxt('instructions_rom16.txt', arr, delimiter=' ', fmt='%s')

#Adding Logisim memory header
with open('instructions_rom16.txt', 'r+') as f:
    line = 'v2.0 raw'
    content = f.read()
    f.seek(0, 0)
    f.write(line.rstrip('\r\n') + '\n' + content)