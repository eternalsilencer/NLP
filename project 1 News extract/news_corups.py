from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pyltp import Segmentor
import re
import codecs
import os


# 初始化链接
engine = create_engine('mysql+pymysql://root:AI@2019@ai@rm-8vbwj6507z6465505ro.mysql.zhangbei.rds.aliyuncs.com:3306/stu_db', echo=True)
Base = declarative_base()
DBsession = sessionmaker(bind=engine)
session = DBsession()

# 描述表结构
class News(Base):
    __tablename__ = 'News_chinese'
    id = Column(Integer, primary_key=True)
    author = Column(String(20), nullable=False)
    content = Column(String(), nullable=False)
    feature = Column(String(), nullable=False)
    title = Column(String(64), nullable=False)
    url = Column(nullable=False)

# 数据查询
def Query_Iteration(session, i):
    news_all = ''

    for new in session.query(News).order_by(News.id)[i*1000:(i+1)*1000]:
        news_all += new.content
    return news_all


LTP_DATA_DIR='E:/NLP_excrise/ltp_data_v3.4.0'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`

segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path) # 加载模型
with codecs.open('news_cut.txt', 'w', encoding='utf-8') as f:
    for i in range(69):
        news_corups = Query_Iteration(session, i)
        news_corups = news_corups.replace(u'\u3000', u' ')
        news_corups = news_corups.replace(u'\\n', u'\n')
#         regex = re.compile(r'\S.*')
#         find = regex.findall(news_corups)
        words = segmentor.segment(str(news_corups))
        line_seg = ' '.join(words)
        print(words)
        f.write(line_seg)

segmentor.release()


