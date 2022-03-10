'''
example textfile form 
words/ukrainian/duolingo_raw.txt
'''
import csv


source_file = '/Users/kitanotoshiyuki/lingo-cast/demo/words/ukrainian/duolingo_raw.txt'
out_dir = '/Users/kitanotoshiyuki/lingo-cast/demo/words/ukrainian/duolingo/'
initial_name = 'Letters1'

with open(source_file) as f:
    s = f.read()
is_after_words = False
name = initial_name
words = []
for text in s.split('\n'):
    if 'Words:' in text:
        is_after_words = True
        words = text.replace('Words: ','').split(', ')
        with open(out_dir + name + '.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(words)
    elif is_after_words:
        name = text.replace(' [test]', '').replace(' ', '').replace('.','').replace('-', '_')
        
        is_after_words = False