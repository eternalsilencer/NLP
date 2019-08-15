
import os.path
import sys
import multiprocessing
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence


line_setences_path = '.\jieba_cut\wiki_seg.txt'
model_path ='.\process\wiki.model'
sentences = LineSentence(line_setences_path)
program = os.path.basename(sys.argv[0])
model = Word2Vec(sentences, size=400, window=5, min_count=5, workers=multiprocessing.cpu_count())
model.save(model_path)

