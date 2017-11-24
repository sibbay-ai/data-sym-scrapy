# coding=utf-8
import json
import urllib2

import re

import time

class Url(object):
    def __init__(self, url):
        self.url = url

    def set_param(self, key, value):
        pattern = re.compile(r"%s=([^=&?]+)"%(key))
        matches = pattern.search(self.url)
        if matches:
            match = matches.group()
            self.url = self.url.replace(match, "%s=%s" % (key, value))
        else:
            reg = "%s&%s=%s"
            if "?" not in self.url:
                self.url = self.url + "?"
            if self.url.endWidth("?"):
                reg = "%s%s=%s"
            self.url = reg % (self.url, key, value)

    def get(self, timeout=30):
        headers = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "refer":"https://translate.google.cn/",
        }
        url = self.url.replace(" ", "%20")
        time.sleep(1)
        print url
        req = urllib2.Request(url, None, headers=headers)
        res = urllib2.urlopen(req, timeout=timeout)
        res = res.read()
        return json.loads(res)


if __name__ == "__main__":
    # m = re.match(r'hello', 'hello world!')
    # url = Url("https://play.google.com/log?format=json&authuser=0")
    # url.get()
    url = Url(
        "http://translate.google.cn/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q=google")
    print url.get()
    # print m.group()
    # print set_page_param("asdas&Page=1&asd=a", "22");
    #
    # import re
    #
    # 将正则表达式编译成Pattern对象
    # pattern = re.compile(r'Page')
    #
    # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
    # match = pattern.match('asdas&Page=1&asd=a')

    # if match:
    # 使用Match获得分组信息
    # print match.group()
    # try:
    #     print get_json("http://www.google.com/", 3)
    # except urllib2.URLError:
    #     pass
