from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
import pymysql
import json
from project_01 import Extractor


app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    conn = pymysql.connect(host='rm-8vbwj6507z6465505ro.mysql.zhangbei.rds.aliyuncs.com', user='root', password='AI@2019@ai', db='stu_db', charset='utf8')
    cur = conn.cursor()
    sql = "SELECT * FROM stu_db.news_chinese limit 5"
    cur.execute(sql)
    u = cur.fetchall()
    conn.close()
    return render_template('index.html', u=u)


@app.route('/textarea_news_opinion', methods=['GET', 'POST'])  # 路由
def textarea_news_opinion():
    data = json.loads(request.form.get('data'))
    extract_dic = extract.main_parse_sentence(data['news'])
    extract_json = []

    for key, value in extract_dic.items():
        node = {}
        node['figure'] = key
        node['opinion'] = value
        extract_json.append(node)

    return json.dumps(extract_json)


@app.route('/database_news_opinion', methods=['GET', 'POST'])  # 路由
def database_news_opinion():
    data = json.loads(request.form.get('data'))

    id_select = data['id']
    conn = pymysql.connect(host='rm-8vbwj6507z6465505ro.mysql.zhangbei.rds.aliyuncs.com', user='root',
                           password='AI@2019@ai', db='stu_db', charset='utf8')
    cur = conn.cursor()
    sql = "SELECT * FROM stu_db.news_chinese where id = %s" % id_select
    cur.execute(sql)
    u = cur.fetchall()
    content = u[0][3].replace(u'\u3000', u' ').replace(u'\\n', u'\n')
    conn.close()

    extract_dic = extract.main_parse_sentence(content)
    extract_json = []
    extract_json.append({'content': content})

    for key, value in extract_dic.items():
        if key is not None and value is not None:
            node = {}
            node['figure'] = key
            node['opinion'] = value
            extract_json.append(node)

    return json.dumps(extract_json)




if __name__ == '__main__':
    extract = Extractor()
    app.run(debug=True, host='0.0.0.0')
