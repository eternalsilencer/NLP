# coding=utf-8

from gensim.models import Word2Vec
from pyltp import Postagger, Segmentor, Parser, NamedEntityRecognizer
from collections import defaultdict
import os


def search_words(serch_word, model, max_size=800):
    visitied = defaultdict(int)
    unvisitied = [serch_word]

    while unvisitied and len(visitied) <= max_size:
        word = unvisitied.pop(0)

        successors = [w for w, p in model.most_similar(word, topn=20)]

        unvisitied += successors

        visitied[word] += 1
        # if we need more sophsiticated, we need change the value as the function(layer, similarity)

    return visitied


def find_sentence(pos, words):
    for i in range(pos, len(words)):
        if words[i] == "。":
            return "".join(words[pos + 1: i])
    return "null"


model = Word2Vec.load('./model/news.model')
relate_word = search_words('说', model)
sorted_realte = sorted(relate_word.items(), key=lambda x: x[1], reverse=True)[:100]
relate = [word[0] for word in sorted_realte]

LTP_DATA_DIR = 'E:/NLP_excrise/ltp_data_v3.4.0'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型


pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
postagger = Postagger()  # 初始化实例
postagger.load(pos_model_path)  # 加载模型

ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`pos.model`
recognizer = NamedEntityRecognizer()  # 初始化实例
recognizer.load(ner_model_path)  # 加载模型

par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
parser = Parser()  # 初始化实例
parser.load(par_model_path)  # 加载模型


def get_opinion(test_news):

    words = segmentor.segment(test_news)  # 分词
    # print ('\t'.join(words))
    # segmentor.release()  # 释放模型

    postags = postagger.postag(words)  # 词性标注
    # postagger.release()  # 释放模型

    netags = recognizer.recognize(words, postags)  # 命名实体识别
    # print ('\t'.join(netags))
    # recognizer.release()  # 释放模型

    arcs = parser.parse(words, postags)  # 句法分析
    # print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
    # parser.release()  # 释放模型

    arc_relate = defaultdict(dict)

    for i, arc in enumerate(arcs):
        if arc.relation == "SBV":
            #         print(words[arc.head-1],netags[i],words[i])
            if words[arc.head - 1] in relate and netags[i] == 'S-Nh':
                #             print(words[arc.head-1])

                if words[arc.head - 1] not in arc_relate[words[i]]:
                    arc_relate[words[i]][words[arc.head - 1]] = []

                sentence = find_sentence(arc.head - 1, words).strip('，')
                sentence = sentence.replace('\r\n', '')
                arc_relate[words[i]][words[arc.head - 1]].append(sentence)

    return arc_relate


if __name__ == '__main__':
    test_news = """今年是“一带一路”倡议提出五周年。五年来，中国已经同140多个国家和国际组织签署共建“一带一路”合作协议，一大批重大合作项目已经落地生根。在今年的外访和参加国际会议期间，习近平主席几乎每到一个国家都会提到“一带一路”，亲自推动“一带一路”倡议走深走实。

    在阿联酋，习近平强调中阿是共建“一带一路”的天然合作伙伴，中方视阿联酋为“一带一路”建设重要支点国家。在塞内加尔，习近平见证了中塞共建“一带一路”等多项双边合作文件的签署，塞内加尔也成为西非首个签署“一带一路”合作文件的国家。在卢旺达，习近平表示，中方欢迎卢方积极参与共建“一带一路”国际合作，鼓励中国企业赴卢旺达投资兴业，助力卢旺达工业化和现代化进程。在南非，习近平强调，中南双方要加强在“一带一路”和中非合作论坛框架内合作。在毛里求斯，习近平提议，发挥毛里求斯参与共建“一带一路”的独特区位优势，加强沟通对接，深化广泛领域合作。

    习近平今年外访收官，向国际社会传达了什么讯息？（来源：CCTV-新闻）
    △独家V观丨盛装歌舞！习近平出席巴新独立大道移交启用仪式
    巴布亚新几内亚是太平洋岛国地区首个同中方签署共建“一带一路”合作协议的国家。在巴新，习近平表示，双方要在“一带一路”框架内加强发展战略对接，争取尽早就启动双边自由贸易协定谈判达成一致。在文莱，习近平强调，中方视文莱为建设21世纪海上丝绸之路重要合作伙伴，愿将“一带一路”倡议同文莱经济多元化战略“2035宏愿”相对接。在菲律宾，习近平见证了《中华人民共和国政府与菲律宾共和国政府关于共同推进“一带一路”建设的谅解备忘录》等多项双边合作文件的签署。

    在西班牙，习近平表示，中西开展“一带一路”合作具有历史、地理等多重优势，要加强“一带一路”倡议同西班牙亚洲战略、地中海走廊建设等对接。在阿根廷，习近平强调，双方要在共建“一带一路”框架内加强沟通和合作，对接两国发展规划。在巴拿马，习近平指出，巴方“2030年国家物流战略”同中方共建“一带一路”倡议高度契合，双方要加强战略对接。在葡萄牙，习近平强调，双方要以签署中葡政府间共建“一带一路”合作谅解备忘录为契机，全面加强“一带一路”框架内合作，促进互联互通。

    习近平今年外访收官，向国际社会传达了什么讯息？习近平在APEC工商领导人峰会上发表主旨演讲

    在今年的APEC工商领导人峰会上，习近平发表主旨演讲时还郑重表示，共建“一带一路”是开放的合作平台，秉持的是共商共建共享的基本原则，没有地缘政治目的，不针对谁也不排除谁，不会关起门来搞小圈子，不是有人说的这样那样的所谓“陷阱”，而是中国同世界共享机遇、共谋发展的阳光大道。中国将于明年4月在北京举办第二届“一带一路”国际合作高峰论坛。

    四次踏出国门，每到一地，习近平都在积极扩大“一带一路”朋友圈，寻找“一带一路”倡议和各国发展战略之间的契合点，并亲自发声排除外界对“一带一路”倡议的各种杂音。可以说，共建“一带一路”是习近平2018年外访行程的一大中心主题。"""

    get_opinion(test_news)

