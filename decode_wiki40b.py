import time

import tensorflow_datasets as tfds
from nltk import sent_tokenize, word_tokenize

from nltk_languagecode import get_nltk_tokenizer_language_code, is_nltk_tokenizer_supported_language
from japanese import JapaneseUtils


# TODO parse japanese and chinese sentence
REQUIRED_WORD_SEPARATION_LANGUAGES = [
    'ja', 'zh-cn', 'zh-tw', 'th', 
]

class DecodeWiki40b():

    def __init__(self, language_code) -> None:
        self.language_code = language_code
        if language_code == 'ja':
            self.ja_text_separator = JapaneseUtils().split_to_sentences
            self.ja_sentence_sepatator = JapaneseUtils().separate_sentence
        self.is_nltk_tokenizer_supported_language = is_nltk_tokenizer_supported_language(self.language_code)
        if self.is_nltk_tokenizer_supported_language:
            self.nltk_languarge_code = get_nltk_tokenizer_language_code(self.language_code)
        texts = self.decode_wiki40b()
        texts = [t.lower() for t in texts]
        sentences = [sentence for t in texts for sentence in self.split_to_sentences(t)]
        self.sentences_tokenized = [self.split_to_words(s) for s in sentences]
        self.word_index_dict = self.get_dict(self.sentences_tokenized)
    
    def decode_wiki40b(self, max_paragraph_num = 100000) -> list:
        # test : val : train = 5 : 5 : 90
        ds = tfds.load('wiki40b/' + self.language_code, split='test')
        start_paragraph = False
        texts = []
        for wiki in ds.as_numpy_iterator():
            for text in wiki['text'].decode().split('\n'):
                if start_paragraph:
                    text = text.replace('_NEWLINE_', '')
                    texts.append(text)
                    # sentences += self.split_to_sentences(text)
                    start_paragraph = False
                if text == '_START_PARAGRAPH_':
                    start_paragraph = True
            if len(texts) > max_paragraph_num:
                break
        
        return texts


    def split_to_sentences(self, text) -> list:
        if self.is_nltk_tokenizer_supported_language:
            return sent_tokenize(text, self.nltk_languarge_code)
        elif self.language_code == 'ja':
            return self.ja_text_separator(text)
        else:
            raise ValueError('not supported language-code: {language_code}')
    
    # def split_to_words(self, sentences):
    def split_to_words(self, sentence):
        if self.is_nltk_tokenizer_supported_language:
            # return [word_tokenize(s, self.nltk_languarge_code) for s in sentences]
            return word_tokenize(sentence, self.nltk_languarge_code)
        elif self.language_code == 'ja':
            # return [japanese_utils.separate_sentence(s) for s in sentences]
            return self.ja_sentence_sepatator(sentence)
        else:
            raise ValueError('not supported language-code: {language_code}')
    
    # TODO clean    
    # def replace_num(self, text, replace_chalacter = 'X'):
        
    #     one_replace_chalacter = ' ' + replace_chalacter * 1 + ' '
    #     text = re.sub(' \d{1} ', one_replace_chalacter, text)
    #     two_replace_chalacter = ' ' + replace_chalacter * 2 + ' '
    #     text = re.sub(' \d{2} ', two_replace_chalacter, text)
    #     three_replace_chalacter = ' ' + replace_chalacter * 3 + ' '
    #     text = re.sub(' \d{3} ', three_replace_chalacter, text)
    #     four_replace_chalacter = ' ' + replace_chalacter * 4 + ' '
    #     text = re.sub(' \d{4} ', four_replace_chalacter, text)
    #     return text

    def get_dict(self, sentences_tokenized):
        word_index_dict = {}
        for i, sent in enumerate(sentences_tokenized):
            for word in sent:
                if word not in word_index_dict:
                    word_index_dict[word] = [i]
                else:
                    word_index_dict[word].append(i)
        return word_index_dict

    def get_tokenized_sentences_contain_word(self, word) -> list:
        try:
            indices = self.word_index_dict[word]
            return [self.sentences_tokenized[i] for i in indices]
        # word does not exist in wiki40b
        except KeyError:
            return []

    def get_word_num_in_sentences(self, word) -> int:
        try:
            indices = self._word_index_dict[word]
            word_num = len(indices)
            return word_num
        except KeyError:
            return 0

        