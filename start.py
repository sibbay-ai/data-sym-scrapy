# coding=utf-8
import logging

import time
import datetime

from core import Task, Schedule
from utils import NetTools
from utils.ExcelUtils import ExcelParse


def init_logger():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s\n',
                        datefmt='%Y-%m-%d  %H:%M:%S', filename='myapp.log', filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


init_logger()
url = NetTools.Url(
    "http://browser.ihtsdotools.org/api/v1/snomed/en-edition/v20170731/descriptions?query=Headaches&limit=50&searchMode=partialMatching&lang=english&statusFilter=activeOnly&skipTo=0&returnLimit=100&normalize=true");
translateUrl = NetTools.Url('http://translate.google.cn/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q=google')


# excel STID获取任务
class GrapTask(Task):
    def run(self, args):
        logging.info("run");
        url, table, row, index, title = args
        url.set_param("query", title)
        result = None
        try:
            result = url.get()
        except Exception, e:
            logging.error("%s=%s" % (e, url.url))
        if result == None:
            return
        matches = result.get("matches")
        # logging.info(url)
        if matches and len(matches) > 0:
            match = matches[0]
            conceptId = match.get("conceptId")
            fsn = match.get("fsn")
            term = match.get("term")
            title = title.strip()
            term = term and term.strip()
            if fsn and "finding" in fsn :#and term and term.lower() == title.lower():
                table.set_cell_value(index, "SCTID", conceptId)
                table.set_cell_value(index, "fsn", fsn)
                logging.info("[%s]>[%s][%s]")
        elif title.endswith("s") or title.endswith("es"):
            if title.endswith("es"):
                title = title[0:-2]
            elif title.endswith("s"):
                title = title[0:-1]
            schedule.append_task(TranslateTask(), (translateUrl, table, row, index, title))
            pass
            # print url.url, title, conceptId


excel = None


# 翻译title,about任务
class TranslateTask(Task):
    def parse(self, translate_url, value, row, table, header):
        result = None
        try:
            translate_url.set_param("q", value)
            result = translate_url.get()
        except Exception, e:
            logging.error(e)
        if result != None and len(result) > 0:
            results = result[0]
            resultStr = "";
            for r in results:
                if len(r) > 0 and r[0] is not None:
                    resultStr = resultStr + r[0]
            table.set_cell_value(row, header, resultStr)

    def run(self, args):
        translate_url, table, row, index, title = args
        about = table.get_cell_value(index, "about")
        self.parse(translate_url, title, index, table, "ctitle")
        self.parse(translate_url, about, index, table, "cabout")

i=0
def finish():
    excel and excel.save()
    global i
    i = i+1
    logging.info("sleep start"+str(datetime.datetime.now()))
    time.sleep(30)
    logging.info("sleep end"+str(datetime.datetime.now()))
    exec_task(i)


#多线程处理框架
schedule = Schedule(thread_num=10, finish=finish)


def callback(table, row, index):
    title = table.get_cell_value(index, "title")
    # url.set_param("query", title)
    #执行匹配
    schedule.append_task(GrapTask(), (url, table, row, index, title))
    #执行翻译
    # schedule.append_task(TranslateTask(), (translateUrl, table, row, index, title))
    # UrlTask.run((url, table, row, index, title),schedule)
    # sleep(1);

def exec_task(i):
    if i<232:
        desc_name=("s%s.xls"%(str(i+1)))
        global excel
        excel = ExcelParse("s%s.xls"%(str(i)), desc_name=desc_name, callback=callback, offset=50*i, limit=50)
        try:
            excel.prase_body()
        except Exception ,e:
            logging.error("e,"+e)

exec_task(i);
