# -*- coding: utf-8 -*-

import requests
import re
from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = ''
app.config['SQLALCHEMY_DATABASE_URI']=''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

form_url = ""

class User(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/api/users/register', methods = ['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    user = User(username = username)
    user.hash_password(password)
    user.email = email
    db.session.add(user)
    db.session.commit()
    return "1"


@app.route('/api/users/login', methods = ['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    print(username)
    url = form_url + "member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&inajax=1"
    postData = {'username': username, 'password': password, 'answer': '', 'cookietime': '2592000', 'handlekey': 'ls', 'questionid': '0', 'quickforward': 'yes',  'fastloginfield': 'username'}
    content = requests.post(url,postData)
    text = content.text
    print(text)

    if text.find(username) > 0:
        print('login success!')
        return "1"
    else:
        print('login faild!')
        return "0"


@app.route('/api/users/logout', methods = ['POST'])
def logout():
    url = form_url + "member.php?mod=logging&action=logout&infloat=yes&inajax=1"
    content = requests.post(url)
    text = content.text
    print(text)

    if text.find(form_url+'./') > 0:
        print('logout success!')
        return "1"
    else:
        print('logout faild!')
        return "0"


@app.route('/api/forum/threads', methods = ['GET'])
def threads():
    url = form_url + "forum.php?mod=forum"
    resp = requests.get(url)
    pattern = '<a href="'+ form_url +'thread-(\d+)-1-1.html" title="([^<]+)"'
    threads = re.findall(pattern, resp.text)
    if threads:
        result = [{'thread': i[0], 'title': i[1]} for i in threads]
        print(result)
        print(len(result))
        return "1"
    else:
        print('failed')
        return "-1"

@app.route('/api/users/profile', methods = ['GET'])
def profile():
    uid = request.json.get('uid')
    url = form_url + "home.php?mod=space&uid=" + uid + "&do=profile"
    content = requests.get(url)
    pattern = 'from=space" target="_blank">([^<]+)</a>'
    profile = re.findall(pattern, content.text)
    print(profile)

    if profile:
        result = [{'info': i.split(" ")[0], 'count': i.split(" ")[1]} for i in profile]
        print(result)
        return "1"
    else:
        print("failed")
        return "-1"


@app.route('/api/users/message', methods = ['POST'])
def message():
    username = request.json.get('username')
    password = request.json.get('password')
    print(username)
    url = form_url + "member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&inajax=1"
    postData = {'username': username, 'password': password, 'answer': '', 'cookietime': '2592000', 'handlekey': 'ls', 'questionid': '0', 'quickforward': 'yes',  'fastloginfield': 'username'}
    session = requests.session()
    content = session.post(url,postData)
    text = content.text

    if text.find(username) > 0:
        print('login success!')
        url = form_url + "home.php?mod=space&do=pm&filter=privatepmm"
        content = session.post(url)
        print(content.text)
        pattern = '<a href="' + form_url + 'space-uid-(\d+).html" target="_blank" class="xw1">([^<]+)</a> 对 <span class="xi2">您</span> 说 :<br />([^<]+)<br />'
        message = re.findall(pattern, content.text)
        if message:
            result = [{'from': i[0], 'name': i[1], 'content': i[2]} for i in message]
            print(result)
        else:
            print("no message")
        print("message sucess")
        return "0"
    else:
        print("failed")
        return "-1"

