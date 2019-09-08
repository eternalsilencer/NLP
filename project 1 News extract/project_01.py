from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller
import re
import gensim
import numpy as np
from gensim.models import Word2Vec,word2vec

say_words = ['诊断', '交代', '说', '说道', '指出','报道','报道说','称', '警告',
           '所说', '告诉', '声称', '表示', '时说', '地说', '却说', '问道', '写道',
           '答道', '感叹', '谈到', '说出', '认为', '提到', '强调', '宣称', '表明',
           '明确指出', '所言', '所述', '所称', '所指', '常说', '断言', '名言', '告知',
           '询问', '知道', '得知', '质问', '问', '告诫', '坚称', '辩称', '否认', '还称',
           '指责', '透露', '坦言', '表达', '中说', '中称', '他称', '地问', '地称', '地用',
           '地指', '脱口而出', '一脸', '直说', '说好', '反问', '责怪', '放过', '慨叹', '问起',
           '喊道', '写到', '如是说', '何况', '答', '叹道', '岂能', '感慨', '叹', '赞叹', '叹息',
           '自叹', '自言', '谈及', '谈起', '谈论', '特别强调', '提及', '坦白', '相信', '看来',
           '觉得', '并不认为', '确信', '提过', '引用', '详细描述', '详述', '重申', '阐述', '阐释',
           '承认', '说明', '证实', '揭示', '自述', '直言', '深信', '断定', '获知', '知悉', '得悉',
           '透漏', '追问', '明白', '知晓', '发觉', '察觉到', '察觉', '怒斥', '斥责', '痛斥', '指摘',
           '回答', '请问', '坚信', '一再强调', '矢口否认', '反指', '坦承', '指证', '供称', '驳斥',
           '反驳', '指控', '澄清', '谴责', '批评', '抨击', '严厉批评', '诋毁', '责难', '忍不住',
           '大骂', '痛骂', '问及', '阐明']

class Ltp_parser:
    def __init__(self):
        self.segmentor = Segmentor()
        self.segmentor.load('/home/student/project/project-01/Four-Little-Frogs/ltp_data_v3.4.0/cws.model')
        self.postagger = Postagger()
        self.postagger.load('/home/student/project/project-01/Four-Little-Frogs/ltp_data_v3.4.0/pos.model')
        self.parser = Parser()
        self.parser.load('/home/student/project/project-01/Four-Little-Frogs/ltp_data_v3.4.0/parser.model')
        self.recognizer = NamedEntityRecognizer()
        self.recognizer.load('/home/student/project/project-01/Four-Little-Frogs/ltp_data_v3.4.0/ner.model')
        self.labeller = SementicRoleLabeller()
        self.labeller.load('/home/student/project/project-01/Four-Little-Frogs/ltp_data_v3.4.0/pisrl.model')

    '''依存句法分析'''
    def get_parser(self, words, postags):
        arcs = self.parser.parse(words, postags)
        # arcs = ' '.join("%d:%s" % (arc.head, arc.relation) for arc in arcs)
        return arcs

    '''命名实体识别'''
    def get_name_entity(self, words, postags):
        netags = self.recognizer.recognize(words, postags)
        netags = list(netags)
        return netags

    '''ltp模型释放'''
    def ltp_release(self):
        self.segmentor.release()
        self.postagger.release()
        self.parser.release()
        self.recognizer.release()

    '''LTP主函数'''
    def parser_main(self, sentence):
        words = list(self.segmentor.segment(sentence))
        postags = list(self.postagger.postag(words))
        arcs = self.get_parser(words, postags)
        netags = self.get_name_entity(words, postags)
        return words, postags, arcs, netags

class Extractor:
    def __init__(self):
        self.ltp = Ltp_parser()

    '''文章分句处理, 切分长句，冒号，分号，感叹号等做切分标识'''
    def split_sents(self, content):
        return [sentence for sentence in re.split(r'[？?！!。；\n\r]', content) if sentence]

    '''获取主语部分'''
    def get_name(self, name, predic, words, property, ne):
        index = words.index(name)
        cut_property = property[index+1:]
        pre = words[:index]
        pos = words[index+1:]
        while pre:
            w = pre.pop(-1)
            w_index = words.index(w)
            if property[w_index] == 'ADV': continue
            if property[w_index] in ['WP', 'ATT', 'SVB'] and (w not in ['，','。','、','）','（']):
                name = w + name
            else:
                pre = False
        while pos:
            w = pos.pop(0)
            p = cut_property.pop(0)
            if p in ['WP', 'LAD', 'COO', 'RAD'] and w != predic and (w not in ['，', '。', '、', '）', '（']):
                name = name + w
            else:
                return name
        return name

    '''获取言论信息'''
    def get_saying(self, sentence, proper, heads, pos):
        # word = sentence.pop(0) #谓语
        if '：' in sentence:
            return ''.join(sentence[sentence.index('：') + 1:])
        while pos < len(sentence):
            w = sentence[pos]
            p = proper[pos]
            h = heads[pos]
            # 谓语尚未结束
            if p in ['DBL', 'CMP', 'RAD']:
                pos += 1
                continue
            # 定语
            if p == 'ATT' and proper[h - 1] != 'SBV':
                pos = h
                continue
            # 宾语
            if p == 'VOB':
                pos += 1
                continue
            # if p in ['ATT', 'VOB', 'DBL', 'CMP']:  # 遇到此性质代表谓语未结束，continue
            #    continue
            else:
                if w == '，':
                    return ''.join(sentence[pos + 1:])
                else:
                    return ''.join(sentence[pos:])

    '''获取信息主函数'''
    def main_parse_sentence(self, content):
        sentences = self.split_sents(content)
        names = []
        sayings = []
        for sentence in sentences:
            cut_words, postags, arcs, netags = self.ltp.parser_main(sentence)
            choose_word = [word for word in cut_words if word in say_words]
            # if not cut_words:
            #     return False
            arcs_relation = [arc.relation for arc in arcs]
            stack = []
            for k, v in enumerate(arcs):
                if postags[k] in ['ni', 'nh']:
                    stack.append(cut_words[k])
                if v.relation == 'SBV' and (cut_words[v.head-1] in choose_word):
                    name = self.get_name(cut_words[k], arcs_relation[v.head-1], cut_words, arcs_relation, netags)
                    saying = self.get_saying(cut_words, arcs_relation, [i.head for i in arcs], v.head)
                    if not saying:
                        quotations = re.findall(r'“(.+?)”', sentence)
                        if quotations: says = quotations[-1]
                    names.append(name)
                    sayings.append(saying)
                    # return name, saying
                if cut_words[k] == '：':
                    name = stack.pop()
                    saying = ''.join(cut_words[k + 1:])
                    # return name, saying
                    names.append(name)
                    sayings.append(saying)

        # self.ltp.ltp_release() # 每次解析都释放资源，比较耗时
        return dict(zip(names, sayings))

#基于Word2Vec的相似度匹配
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


if __name__ == '__main__':
    #函数调用
    a = Extractor()
    print(a.main_parse_sentence('而港股突然爆发大涨，也是因为这个传闻。果然，在4日晚间，林郑月娥今日（4日）晚17时50分发表电视公告，宣布正式撤回修订《逃犯条例》草案。据环球时报报道，林郑月娥今天下午发表谈话，提出四项行动，其中包括正式撤回修改《逃犯条例》的草案。她表示她与特区政府所有司局长将从本月开始与市民广泛对话，一起探讨对各种问题的解决方法。林郑月娥表示，持续出现的暴力正动摇香港法治的根基，目前最迫切的就是要遏止暴力、捍卫法治、重建社会秩序。政府会对所有违法及暴力行为，严正执法。她表示希望今天提出的四项行动会成为社会向前行的起点，可以有助于打破困局，以对话代替对立，为社会带来改变。'))



