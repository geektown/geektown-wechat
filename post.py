# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
    
def http_post():
    url='http://115.29.199.8:6000/openapi'
    values ={'userid':u'Smith','userinput':u' 红烧肉怎么做？ '}

    jdata = json.dumps(values)             # 对数据进行JSON格式化编码
    req = urllib2.Request(url, jdata)       # 生成页面请求的完整数据
    response = urllib2.urlopen(req)       # 发送页面请求
    return response.read()                    # 获取服务器返回的页面信息

resp = http_post()
print resp