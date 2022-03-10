import MeCab
import ipadic

# TODO inherit
# TODO implement superclass

AVOID_START_JAPANESE_POS_LIST = ['接続詞', '助詞']
AVOID_END_JAPANESE_POS_LIST = ['接続詞', '助詞', '名詞']

class JapaneseUtils():
    
    def __init__(self) -> None:
        self.spacer = MeCab.Tagger('-Owakati ' + ipadic.MECAB_ARGS)
        self.tagger = MeCab.Tagger(ipadic.MECAB_ARGS)
        # self.spacer = MeCab.Tagger('-Owakati -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
        # self.tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    def split_to_sentences(self, text) -> list:
        return text.split('。')

    def spacing_sentence(self, sentence) -> str:
        return self.spacer.parse(sentence)
    
    def separate_sentence(self, sentence) -> list:
        return self.spacer.parse(sentence).split()
    
    def get_pos_japanese(self, word):
        p = self.tagger.parse(word)
        pos = p.split("\n")[0].split()[1].split(',')[0]
        return pos
    
    # def check_both_ends(self, sentence):
    #     sentence = self.separate_sentence(sentence)

    #     if self.get_pos_japanese(sentence[0]) in  AVOID_START_JAPANESE_POS_LIST:
    #         sentence = sentence[i:]
    #     if self.get_pos_japanese(sentence[-1]) in AVOID_END_JAPANESE_POS_LIST:
    #         sentence = sentence[:-1]
    #     return ''.join(sentence)
