# -*- coding: utf-8 -*-

from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
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

try: 
  import xml.etree.cElementTree as ET 
except ImportError: 
  import xml.etree.ElementTree as ET

import logging
# 创建一个logger
logger = logging.getLogger('wechat')
logger.setLevel(logging.DEBUG)
# 创建一个handler，用于写入日志文件
fh = logging.FileHandler('wechat.log')
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
    
# 用户的请求内容 (Request 中的 Body)
# 请更改 body_text_of_user_request 的内容来测试下面代码的执行情况
body_text_of_user_request = """
<xml>
<ToUserName><![CDATA[geektownCN]]></ToUserName>
<FromUserName><![CDATA[oUMXVvrMfJwjq0vnBp-sK4R5hfxY]]></FromUserName>
<CreateTime>1469348830</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[geektown.cn]]></Content>
<MsgId>9038700799783131222</MsgId>
</xml>
"""

conf = WechatConf(
    token='xiaoigeektown', 
    appid='wx07c475ee8eb047ab', 
    appsecret='36223eab33cf07794151918ed98a4550', 
    encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    encoding_aes_key='4SSZw3Kn7WXcucEYqDarlV4G1fo4mTDgVCjCy77k9us'  # 如果传入此值则必须保证同时传入 token, appid
)

# 实例化 wechat
wechat = WechatBasic(conf=conf)


# /service 会通过nginx转发过来
@app.route('/xiaoi')
def xiaoi():
    echostr = request.args.get('echostr')
    if echostr == "":
        return "not found echostr"
    return echostr 
    
@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

# 测试微信公众平台api接口, 直接返回echoStr，不做校验 , FIXME can not get the post body 
@app.route('/xiaoi/service', methods=['POST'])
def service():
    if request.method == 'POST':
        print "get a post request", request
        # print request.args
        # print request.form
        # print request.values
        # print request.cookies
        # print request.get_data()
        # print request.form['body']
        body_text_of_user_request = request.get_data()
        # print 'encrypt_type,', request.form['encrypt_type']
        # print body
        try: 
            # tree = ET.parse(xmlfile)     #打开xml文档 
            tree = ET.fromstring(body_text_of_user_request) #从字符串传递xml 
                    #获得root节点  
        except Exception, e: 
            print "Error:cannot parse xml."

         
    # 对签名进行校验，此处跳过。
    if wechat.check_signature(signature=request.args.get('signature'), timestamp=request.args.get('timestamp'), nonce=request.args.get('nonce')):
        # 对 XML 数据进行解析 (必要, 否则不可执行 response_text, response_image 等操作)
        wechat.parse_data(body_text_of_user_request)
        id = wechat.message.id          # 对应于 XML 中的 MsgId
        # print id
        target = wechat.message.target  # 对应于 XML 中的 ToUserName
        # print target
        source = wechat.message.source  # 对应于 XML 中的 FromUserName
        # print source
        createTime = wechat.message.time      # 对应于 XML 中的 CreateTime
        # print createTime
        type = wechat.message.type      # 对应于 XML 中的 MsgType
        # print type
        raw = wechat.message.raw        # 原始 XML 文本，方便进行其他分析
        # print "raw xml ----:", raw
        # 获得解析结果, message 为 WechatMessage 对象 (wechat_sdk.messages中定义)
        message = wechat.get_message()
        # print "wechat.get_message()", message
        response = wechat.response_text(u'^_^')
        userInput = u'你好'
        openid = request.args.get('openid')
        if message.type == 'text':
            if message.content == 'wechat':
                response = wechat.response_text(u'^_^')
            else:
                userInput = tree.findtext('Content') 
                # 在此阶段，直接返回。测试用。
                response = wechat.response_text(u'云平台将会对你智能回复，即将开放测试，敬请期待。\n你输入的内容是：'+ userInput +'\n@' + time.ctime())
        elif message.type == 'voice':
            userInput = tree.findtext('Recognition')
            response = wechat.response_text(u'云平台将会对你智能回复，即将开放测试，敬请期待。\n你输入的语音是：'+ userInput +'\n@' + time.ctime())
        else:
            response = wechat.response_text(u'不好意思，你的输入小i我不理解。')
        
        #robotSay 包含的内容会反馈给用户
        robotAnswer = requestService(openid, userInput)
        # robotAnswer = userInput
        # 将robotsay的内容转换成语音，存入到素材库中。
        # putVoiceToWechatRepo(openid, robotSay)
        response = wechat.response_text(robotAnswer)
        
    return response

def putVoiceToWechatRepo(openid, robotSay):
    
    # 使用讯飞的语音输出 
    fname = "/tmp/"+openid+".amr"
    cmd = ['/home/xiaoi/Linux_voice_1.109/bin/tts_sample', fname, robotSay]
    print fname
    subprocess.call(cmd)
    # 需要认证 OfficialAPIError: 48001: api unauthorized hint，个人账号无法认证。            
    wechat.upload_media("voice", file(fname))
    os.remove(fname)
      
    

def requestService(openid, userInput):
    """
    调用小i云服务，得到robot回复的内容。两个参数分别是用户标识openid,和用户输入的文本。
    """
    answer = u"通过智能硬件终端设备可以自动读出来："
    result = servicemanager.request(userInput,openid)
    for item in result:
        if item.has_key("value"):
            print "**robot answer**   cmd:"+item["cmd"]+",value:"+item["value"].decode('utf-8').encode(sys.getfilesystemencoding())
            if bool(re.search(u'错误的服务请求', item["value"].decode('utf-8'), re.IGNORECASE)) == True:       
                url = 'http://localhost:9090/turing?userId='+openid+'&userSay='+urllib.quote(userInput.encode('utf-8'))
                print "request to turing", url
                answer += urllib.urlopen(url).read()
                break
                
            if item["cmd"]=="say":
                answer += item["value"].decode('utf-8').encode(sys.getfilesystemencoding()) + "\n"
            if item["cmd"]=="play":
                answer += "\n即将为你播放:" + item["value"].decode('utf-8').encode(sys.getfilesystemencoding())
        else:
            print "**robot answer**   cmd:"+item["cmd"]
    logger.info("user|input|answr: [" + openid + "|" + userInput + "|" + answer + "]")        
    return answer
    
# just for test
@app.route('/xiaoi/user/<name>')
def sayHello(name):
    return '<h1> Hello,%s </h1>' % name
    


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000) 
