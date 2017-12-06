import json
import logging
from urllib import request

import re

import time
from urllib.parse import quote


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
            "refer":"http://translate.google.cn/",
            "Content-Type":"application/json"
        }
        url = self.url.replace(" ", "%20")
        url = url.replace("\n", "%20")
        url = url.replace("\t", "%20")
        url = url.replace("\r", "%20")
        logging.error(url)
        time.sleep(1)
        req = request.Request(url, None, headers=headers)
        res = request.urlopen(req, timeout=timeout)
        res = res.read()
        return json.loads(res)


if __name__ == "__main__":
    print(quote("http://             ",safe="/:?&="))
