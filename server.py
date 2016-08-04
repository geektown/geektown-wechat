# -*- coding: utf-8 -*-

from flask import Flask, request
import time
import tempfile
import subprocess
import servicemanager,json,sys,os
import re
import urllib2
import urllib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import logging
# 创建一个logger
logger = logging.getLogger('webserver')
logger.setLevel(logging.DEBUG)
# 创建一个handler，用于写入日志文件
fh = logging.FileHandler('webserver.log')
fh.setLevel(logging.DEBUG)
# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)
  
app = Flask(__name__)

@app.route('/xiaoi')
def xiaoi():
    echostr = request.args.get('echostr')
    if echostr == "":
        return "not found echostr"
    return echostr 
    
@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

@app.route('/openapi', methods=['POST'])
def aiService():       
    print "++++++++++++++++++++++++", request.get_data()
    
    data = json.loads(request.get_data())

    robotAnswer = requestService(data["userid"], data["userinput"])
    return robotAnswer

def requestService(openid, userInput):
    """
    调用小i云服务，得到robot回复的内容。两个参数分别是用户标识openid,和用户输入的文本。
    """
    answer = u""
    result = servicemanager.request(userInput,openid)
    answer = json.dumps(result)
    for item in result:
        if item.has_key("value"):
            if bool(re.search(u'错误的服务请求', item["value"].decode('utf-8'), re.IGNORECASE)) == True:       
                url = 'http://localhost:9090/turing?userId='+openid+'&userSay='+urllib.quote(userInput.encode('utf-8'))
                print "request to turing", url 
                tResponse = urllib.urlopen(url).read()                
                print 'turing response ', tResponse
                data = json.loads(tResponse)
                print data
                if data["code"] == 100000:
                    answer = data["text"]
                elif data["code"] == 200000:
                    answer = data["text"] + "点这个链接查看吧。" 
                elif data["code"] == 302000:
                    answer = data["text"] + u"。来自" + data["list"][0]["source"] +":" + data["list"][0]["article"] 
                elif data["code"] == 308000:
                    answer = data["text"] + u"\n菜名：" +  data["list"][0]["name"] + u"\n食材："  + data["list"][0]["info"] 
                answer =  '[{"cmd":"say","value":"' + answer + '"}]'
                break

    logger.info("user|input|answr: [" + openid + "|" + userInput + "|" + answer + "]")        
    return answer
    
# just for test
@app.route('/xiaoi/user/<name>')
def sayHello(name):
    return '<h1> Hello,%s </h1>' % name
    


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=6000) 
