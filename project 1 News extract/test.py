# coding=UTF-8
from gensim.models import Word2Vec,word2vec
from gensim import models
from pyltp import Segmentor, Postagger, Parser, SementicRoleLabeller, NamedEntityRecognizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import numpy as np
from scipy.linalg import norm
import gensim
import jieba
from typing import List
import re

#基于Word2Vec得出句子的余弦相似度
def build_sentence_vector(sentence, size, w2v_model):
    vec = np.zeros(size).reshape((1, size))
    count = 0
    for word in sentence:
        try:
            vec += w2v_model[word].reshape((1, size))
            count += 1
        except KeyError:
            continue
    if count != 0:
        vec /= count
    return vec
def cosine_similarity(vec1, vec2):
    a = np.array(vec1)
    b = np.array(vec2)
    cos1 = np.sum(a * b)
    cos21 = np.sqrt(np.sum(a**2))
    cos22 = np.sqrt(np.sum(b**2))
    cosine_value = cos1 / float(cos21 * cos22)
    return cosine_value
def compute_cosine_similarity(sent1, sent2):
    size = 100
    w2v_model = Word2Vec.load('news_corpus_8.13.model')
    vec1 = build_sentence_vector(sent1, size, w2v_model)
    vec2 = build_sentence_vector(sent2, size, w2v_model)
    similarity = cosine_similarity(vec1, vec2)
    return similarity

#TfIdf计算句子相似度
def tfidf_similarity(s1, s2):
    def add_space(s):
        return ' '.join(list(s))
    s1, s2 = add_space(s1), add_space(s2)
    cv = TfidfVectorizer(tokenizer=lambda s: s.split())
    corpus = [s1, s2]
    vectors = cv.fit_transform(corpus).toarray()
    return np.dot(vectors[0], vectors[1]) / (norm(vectors[0]) * norm(vectors[1]))

#基于Word2Vec的相似度匹配
# model_file = 'news_12g_baidubaike_20g_novel_90g_embedding_64_small.model'
model = Word2Vec.load('news_word2v-model.model')
def cut_word(sentence):
    segmentor = Segmentor()
    segmentor.load('/home/student/project/project-01/Four-Little-Frogs/ltp_data_v3.4.0/cws.model')
    words = list(segmentor.segment(sentence))
    segmentor.release()
    # cut_words = ("\t".join(words))
    return words
def vector_similarity(s1, s2):
    def sentence_vector(s):
        words = cut_word(s)
        v = np.zeros(100)
        for word in words:
            v += model[word]
        v /= len(words)
        return v
    v1, v2 = sentence_vector(s1), sentence_vector(s2)
    return np.dot(v1, v2) / (norm(v1) * norm(v2))

#word2vec词向量+tfidf
def list_dict(list_data):
    list_data=list(map(lambda x:{str(x[0]):x[1]},list_data))
    dict_data = {}
    for i in list_data:
        key, = i
        value, = i.values()
        dict_data[key] = value
    return dict_data
def word2vec_tfidf(corpus_tfidf, token2id, sentence_list, model, embedding_size):
    sentence_set = []
    for i in range(len(sentence_list)):
        sentence_vector = np.zeros(embedding_size)
        sentence = sentence_list[i]
        sentence_tfidf = corpus_tfidf[i]
        dict_tfidf = list_dict(sentence_tfidf)
        for word in sentence:
            tfidf_weight = dict_tfidf.get(str(token2id[word]))
            sentence_vector = np.add(sentence_vector, tfidf_weight * model[word])
        sentence_vector = np.divide(sentence_vector, len(sentence))
        sentence_set.append(sentence_vector)
    return sentence_set



def vector_similar(sentence1, sentence2):
    segmentor = Segmentor()
    segmentor.load('/home/student/project/project-01/Four-Little-Frogs/ltp_data_v3.4.0/cws.model')
    model = Word2Vec.load('news_word2v-model.model')
    def sentence_vector(s):
        words = list(segmentor.segment(s))
        v = np.zeros(100)
        for word in words:
            v += model[word]
        v /= len(words)
        return v
    v1, v2 = sentence_vector(sentence1), sentence_vector(sentence2)
    return np.dot(v1, v2) / (norm(v1) * norm(v2))

content = '而港股突然爆发大涨。也是因为这个。果然在晚间。今日晚发表电视公告。宣布正式撤回修订草案。'
def split_sents(content):
    return [sentence for sentence in re.split(r'[？?！!。；\n\r]', content) if sentence]
sentences = split_sents(content)
print(sentences)

expect = 0.7
i = len(sentences)
print(i)

new_sentences = []
while i>1:
    s1 = sentences.pop(0)
    print(sentences)
    s2 = sentences[0]
    print(vector_similarity(s1, s2))

    if vector_similarity(s1, s2) > 0.7:
        sentences[0] = s1 + ',' + s2
        print(sentences[0])
    else:
        new_sentences.append(s1)
        print(new_sentences)
    i -= 1
    if i == 1:
        new_sentences.append(s2)

print(new_sentences)

# print(compute_cosine_similarity(['你', '在', '干嘛', '呢'], ['你', '在', '干', '什么', '呢']))
# print(tfidf_similarity('你在干嘛呢', '你在干什么呢'))
# print(vector_similar('你在干嘛呢', '你在干什么呢'))

# def cut_word(sentence):
#     segmentor = Segmentor()
#     segmentor.load('/usr/local/python3/lib/python3.6/site-packages/cws.model')
#     words = list(segmentor.segment(sentence))
#     segmentor.release()
#     # cut_words = ("\t".join(words))
#     return words
#
# def wmd(sent1, sent2):
#     sent1 = cut_word(sent1)
#     sent2 = cut_word(sent2)
#     model = models.Word2Vec.load('news_corpus_8.13.model')
#     #如果不打算进一步训练模型，调用init_sims将使得模型的存储更加高效
#     # model.init_sims(replace=True)
#     distance = model.wmdistance(sent1, sent2)
#     return distance

# def get_top_n(document, query, num_best):
#     corups = [word_cut(i) for i in document]
#     model = models.Word2Vec.load('news_corpus_8.13.model')
#     instance = WmdSimilarity(corups, model, num_best)
#     query = word_cut(query)
#     sims = instance[query]
#     for i in range(num_best):
#         print(sims[i][1])
#         print(document[sims[i][1]])




