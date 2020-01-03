# -*- coding: utf-8 -*-
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'index'


# 使用<param>传递参数
@app.route('/hello/<param>')
def hello_get(param):
    return 'hello %s' % param


# 使用POST请求
@app.route('/hello/<user>', methods=['POST'])
def hello_post(user):
    return 'hello %s' % user


if __name__ == '__main__':
    app.run()
