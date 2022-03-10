import string
import json

from nltk.lm        import Vocabulary
from nltk.lm.models import MLE
from nltk.util      import ngrams
from nltk.lm.preprocessing import pad_sequence

from nltk_languagecode import get_nltk_tokenizer_language_code, is_nltk_tokenizer_supported_language

EXCLUDE_STR = string.punctuation + '<s></s>«»、「」（）『』・'

# TODO consider the appropriate number
MAX_PROCESS_SENTENCE_NUM = 100

class NgramLanguageModel():
    
    def __init__(self, sentences_tokenized) -> None:        
        self.sentences_tokenized = sentences_tokenized[:MAX_PROCESS_SENTENCE_NUM]
        sentences_padded = self.padding_sentences(sentences_tokenized)
        trigrams_forward = self.get_ngram(N=3, sentences_padded=sentences_padded)
        trigrams_backward = self.get_ngram(N=3, sentences_padded=sentences_padded, backward=True)
        vocabulary = self.get_vocab(sentences_padded)
        self.trigram_forward_model = self.create_language_model(trigrams_forward, N=3,vocabulary=vocabulary)
        self.trigram_backward_model = self.create_language_model(trigrams_backward, N=3, vocabulary=vocabulary)
    
    def create_language_model(self, ngrams, N, vocabulary): # N-gram言語モデルの作成
        ngram_language_model = MLE(order=N, vocabulary=vocabulary)
        ngram_language_model.fit(ngrams, vocabulary)
        return ngram_language_model
    
    # TODO? 
    def padding_sentences(self, sentences_tokenized):
        sents = []
        for sent in sentences_tokenized:
            sent_padded = list(pad_sequence([word for word in sent],pad_left=True, left_pad_symbol="<s>",pad_right=True, right_pad_symbol="</s>", n=3))
            sents.append(sent_padded)
            # sents.append(list(pad_sequence([word for word in sent], n=3)))
        return sents
        

    def get_vocab(self,sentences_padded):
        vocab = Vocabulary([word for sent in sentences_padded for word in sent], unk_cutoff=1)
        return vocab
        
    def get_ngram(self,N, sentences_padded, backward=False):
        if backward:
            word_ngrams = [ngrams(sent[::-1], N) for sent in sentences_padded]
        else:
            word_ngrams = [ngrams(sent, N) for sent in sentences_padded]
        return word_ngrams
    
    # Maximum Likelihood Estimator
    # P(new_word|context)
    def get_mle_word(self,model, context):
        word_prob_list = []
        ngram_words = model.context_counts(model.vocab.lookup(context))
        # model doesnt have context
        if len(ngram_words) == 0:
            return '', 0
        for word in ngram_words:
            word_prob_list.append((word, model.score(word, context)))
        word_prob_list.sort(key=lambda x: x[1], reverse=True) # 出現確率順

        for word, prob in word_prob_list:
            if not self.is_word_in_exclude_str(word):
                return word, prob
        return '', 0

    def is_word_in_exclude_str(self, word):
        return word in EXCLUDE_STR

    def count_word_by_relative_position(self, word, relative_position):
        word_counter = {}
        for sent in self.sentences_tokenized:
            word_position = sent.index(word)
            try:
                new_word = sent[word_position + relative_position]
                if new_word not in word_counter:
                    word_counter[new_word] = 1
                else:
                    word_counter[new_word] += 1
            except IndexError:
                continue
        return word_counter
        
    def sort_word_counter(self, word_counter, isDescending=True):
        return {k: v for k, v in sorted(word_counter.items(), key=lambda item: item[1], reverse=isDescending)}

    def get_most_common_word_in_word_counter(self, word_counter):
        word_counter = self.sort_word_counter(word_counter)
        for w,c in word_counter.items():
            if w not in EXCLUDE_STR:
                return w, c
        return '', 0
                
    #TODO clean
    def create_example_sentence(self,word, min_length=4, max_length=6):
        # count both side of source-word for 2 gram
        prev_word_counter = self.count_word_by_relative_position(word, -1)
        next_word_counter = self.count_word_by_relative_position(word, +1)
        most_common_prev_word, prev_count = self.get_most_common_word_in_word_counter(prev_word_counter)
        most_common_next_word, next_count = self.get_most_common_word_in_word_counter(next_word_counter)
        if prev_count > next_count:
            words = [most_common_prev_word, word]
        else:
            words = [word, most_common_next_word]
        example_sentence = ' '.join(words)
        score_sum = 0
        score_mean = 0
        while(len(words)) < max_length:
            prev_context = tuple(words[:2][::-1])
            prev_word, prev_score = self.get_mle_word(self.trigram_backward_model, prev_context)
            next_context = tuple(words[-2:])
            next_word, next_score = self.get_mle_word(self.trigram_forward_model, next_context)

            if prev_score == 0 and next_score == 0:
                return example_sentence
            elif prev_score > next_score:
                score_sum += prev_score
                score_mean_old = score_mean
                score_mean = score_sum / (len(words))
                if score_mean_old > score_mean and len(words) >= min_length:
                    return example_sentence
                else:
                    words = [prev_word] + words
            else:
                score_sum += next_score
                score_mean_old = score_mean
                score_mean = score_sum / (len(words))
                if score_mean_old > score_mean and len(words) >= min_length:
                    return example_sentence
                else:
                    words = words + [next_word]
            example_sentence = ' '.join(words)

            
        return example_sentence
            



