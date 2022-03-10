import re

def decode_input_file(file_path) -> list:
    with open(file_path) as f:
        s = f.read()
        s = re.sub('\s','',s)
        words = s.split(',')        
        # remove space
        words = [w for w in words if w != '']
        return words
