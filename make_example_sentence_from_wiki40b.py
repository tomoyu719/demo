import os
import re

import tensorflow_datasets as tfds
from utility.russian.russian_word_morph import RussianWordMorph


#  TODO 日本語、中国語などは文をparseする


class MakeExampleSentenceFromWiki40b():
    SA = '_START_ARTICLE_'
    SS = '_START_SECTION_'
    SP = '_START_PARAGRAPH_'
    NL = '_NEWLINE_'
    META_TAGS = [SA, SS, SP, NL]

    def __init__(self, wiki40b_language_code, exclude_pos_list=[], is_including_other_word_form=False) -> None:
        self.wiki40b_sentences, self.word_index_dict = self._decode_wiki40b(
            wiki40b_language_code)
        self.morph = RussianWordMorph()
        self.exclude_pos_list = exclude_pos_list
        self.is_including_other_word_form = is_including_other_word_form
        

    # TODO 数字等を置換する？　1994 -> XX    
    def _decode_wiki40b(self, wiki40b_language_code):
        # test : val : train = 5 : 5 : 90
        ds = tfds.load('wiki40b/' + wiki40b_language_code, split='test')

        start_paragraph = False
        sentences = []
        for wiki in ds.as_numpy_iterator():
            for text in wiki['text'].decode().split('\n'):
                if start_paragraph:
                    text = text.replace('_NEWLINE_', '').lower()
                    sentences += text.split('.')
                    start_paragraph = False
                if text == '_START_PARAGRAPH_':
                    start_paragraph = True

        word_index_dict = {}
        for i, s in enumerate(sentences):
            for word in s.split():
                if word not in word_index_dict:
                    word_index_dict[word] = [i]
                else:
                    word_index_dict[word].append(i)
        return sentences, word_index_dict

    
    #Wiki40bから、 前+word+後,を返す
    def _get_around_words(self, word) -> list:
        try:
            indices = self.word_index_dict[word]
        except KeyError:
            return []
        short_sentences = []
        # sentences = list(filter(lambda s: word in s, self.wiki40b_sentences))
        sentences = [self.wiki40b_sentences[i] for i in indices]
        for s in sentences:
            split = s.split()
            if word in split:
                index = split.index(word)
                try:
                    prev = split[index - 1]
                except IndexError:
                    prev = ''
                try:
                    next = split[index + 1]
                except IndexError:
                    next = ''
                prev_pos = self.morph.get_word_pos(prev)
                next_pos = self.morph.get_word_pos(next)
                # avoid end up with PREP(前置詞)
                if next_pos == 'PREP':
                    try:
                        next += ' ' + split[index + 2]
                    except IndexError:
                        next = next
                    
                if prev_pos not in self.exclude_pos_list and next_pos not in self.exclude_pos_list and prev != '' and next != '':
                    s = prev + ' ' + word + ' ' + next
                    s = s.lower()
                    short_sentences.append(s)
                else:
                    if prev_pos not in self.exclude_pos_list and prev != '':
                        s = prev + ' ' + word
                        s = s.lower()
                        short_sentences.append(s)
                    if next_pos not in self.exclude_pos_list and next != '':
                        s = word + ' ' + next
                        s = s.lower()
                        short_sentences.append(s)


        return short_sentences

        
    def is_idiom_russian(self, word):
        s = re.split('[-_ ]', word)
        
        if len(s) > 1:
            return True
        return False

    # def is_word_contain_exclude_pos(self, word):

    #     pos = self.morph.get_word_pos(word)
    #     if pos in self.exclude_pos_list:
    #         return True
    #     return False        

    def make_example_sentence(self, word) -> str:
        word = word.lower()
        if self.is_idiom_russian(word):
            return word
        example_sentences = []
        if self.is_including_other_word_form:
            all_word_forms = self.morph.get_inflected_forms(word)
            for word in all_word_forms:
                example_sentences += self._get_around_words(word)
        else:
            example_sentences = self._get_around_words(word)
        # # exclude sentence including specific pos
        # example_sentences = [s for s in example_sentences if self.is_contain_exclude_pos(s) != True ]
                
        # sentence not exist in wiki40b
        if len(example_sentences) == 0:
            return word        

        # count same sentence
        sentence_frequency_conter = {}
        for s in example_sentences:
            if s not in sentence_frequency_conter:
                sentence_frequency_conter[s] = 1
            else:
                sentence_frequency_conter[s] += 1
        
        most_frequent_sentence = max(sentence_frequency_conter, key=sentence_frequency_conter.get)
        
        return most_frequent_sentence