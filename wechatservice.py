# -*- coding: utf-8 -*-

from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from flask import Flask, request
import time

app = Flask(__name__)
    
# 下面这些变量均假设已由 Request 中提取完毕
token = 'xiaoigeektown'  # 你的微信 Token
signature = 'f24649c76c3f3d81b23c033da95a7a30cb7629cc'  # Request 中 GET 参数 signature
timestamp = '1406799650'  # Request 中 GET 参数 timestamp
nonce = '1505845280'  # Request 中 GET 参数 nonce
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
@app.route('/xiaoi/service', methods=['GET','POST'])
def service():
    response = body_text_of_user_request
    if request.method == 'POST':
        print "get a post request", request
        print request.args
        print request.form
        print request.values
        print request.cookies
        
        # print request.form['body']
        
        # print 'encrypt_type,', request.form['encrypt_type']
        # print body
    # 对签名进行校验
    if True:
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
        if message.type == 'text':
            if message.content == 'wechat':
                response = wechat.response_text(u'^_^')
            else:
                response = wechat.response_text(u'这是公众号阿里云服务器返回的数据。\n@' + time.ctime())
        elif message.type == 'image':
            response = wechat.response_text(u'图片')
        else:
            response = wechat.response_text(u'未知')

        # 现在直接将 response 变量内容直接作为 HTTP Response 响应微信服务器即可，此处为了演示返回内容，直接将响应进行输出
    # print response

    return response

# just for text
@app.route('/xiaoi/user/<name>')
def sayHello(name):
    return '<h1> Hello,%s </h1>' % name
    


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000) 
