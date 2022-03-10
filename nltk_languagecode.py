import json

def is_nltk_tokenizer_supported_language(language_code) -> bool:
    with open('wiki40b_code_to_nltk_tokenizer_code.json') as f:
        d = json.load(f)
        return language_code in d

def get_nltk_tokenizer_language_code(language_code) -> str:
    with open('wiki40b_code_to_nltk_tokenizer_code.json') as f:
        d = json.load(f)
        return d[language_code]    