import argparse
import json
import os
from decode_input_file import decode_input_file
from decode_wiki40b import DecodeWiki40b
from ngram_language_model import NgramLanguageModel


def main():
    parser = argparse.ArgumentParser()
    
    # TODO? guess soruce language form words file
    parser.add_argument("-l","--language_code", help="wiki40b language code: https://research.google/pubs/pub49029/?hl=ja")
    parser.add_argument("-d", "--words_files_dir")
    parser.add_argument("-o", "--output_files_dir", default='outputs/')
    parser.add_argument("-min","--min_example_sentence_length", type=int, default=3)
    parser.add_argument("-max","--max_example_sentence_length", type=int, default=5)
    parser.add_argument("-r","--remove_stopwords", type=bool, default=True)

    args = parser.parse_args()
    wiki40b = DecodeWiki40b(args.language_code)
    
    # TODO error check
    file_names = os.listdir(args.words_files_dir)

    for i, file_name in enumerate(file_names):
        print(i+1,'/',len(file_names))
        file_path = args.words_files_dir + file_name
        output_json_name = file_name.split('.')[0] + '.json'
        
        source_words = decode_input_file(file_path)
        source_words = [w.lower() for w in source_words]

        word_with_example_sentences = []
        for source_word in source_words:
            sentences_contained_word = wiki40b.get_tokenized_sentences_contain_word(source_word)
            model = NgramLanguageModel(sentences_contained_word)
            word_with_example_sentence = {}
            word_with_example_sentence['word'] = source_word
            example_sentence = model.create_example_sentence(source_word)
            word_with_example_sentence['example'] = example_sentence
            word_with_example_sentences.append(word_with_example_sentence)

        with open(args.output_files_dir + output_json_name, 'w',encoding='utf8') as f:
            json.dump(word_with_example_sentences, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
