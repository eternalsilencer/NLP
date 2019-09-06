from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
import pymysql
import json
import opinion_extract

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s!</h1>' % name


@app.route('/showdata')
def showdata():
    conn = pymysql.connect(host='rm-8vbwj6507z6465505ro.mysql.zhangbei.rds.aliyuncs.com', user='root', password='AI@2019@ai', db='stu_db', charset='utf8')
    cur = conn.cursor()
    sql = "SELECT * FROM stu_db.news_chinese limit 5"
    cur.execute(sql)
    u = cur.fetchall()
    conn.close()

    return render_template('showdata.html', u=u)



@app.route("/hello", methods=['GET', 'POST'])
def Hello():
    message = "hello"
    return render_template(temp=message)


@app.route('/ajax_post', methods=['GET', 'POST'])  # 路由
def test_post():
    data = json.loads(request.form.get('data'))
    testInfo = {}
    testInfo['figure'] = '小明'
    testInfo['opinion'] = '很好'
    testInfo['source'] =data['id']
    return json.dumps(testInfo)


@app.route('/get_news', methods=['GET', 'POST'])
def get_news():
    print("hello")
    news = request.values.get("news")
    print(news)
    n = opinion_extract.get_opinion(news)
    # n = {'习近平': {'说': ['你好', '没事'] }}
    print(n)
    return render_template('showdata.html', n=n)


if __name__ == '__main__':
    app.run(debug=True)
    print("hh")
