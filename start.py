import logging

import time
import datetime

from core import Task
from utils import net_tools
from utils.excel_utils import ExcelParse


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
IHT_URL = net_tools.Url(
    'http://browser.ihtsdotools.org/api/v1/snomed/en-edition/v20170731/descriptions?query=Headaches&limit=50&searchMode=partialMatching&lang=english&statusFilter=activeOnly&skipTo=0&returnLimit=100&normalize=true');
TRANSLATE_URL = net_tools.Url('http://translate.google.cn/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q=google')

"""
    根据query去查询信息
    TranslateTask().run(TRANSLATE_URL, table, row, index, title)
    可以修改为：Schedule.appendTask(TranslateTask(),(table, row, index, title))
"""


class GrapTask(Task):
    def run(self, args):
        logging.info("run");
        url_str, table, row, index, title = args
        url_str.set_param("query", title)
        result = None
        try:
            result = url_str.get()
        except Exception as e:
            logging.error("%s=%s" % (e, url_str.url))
        if result is None:
            return
        matches = result.get("matches")
        if matches:
            match = matches[0]
            concept_id = match.get("conceptId")
            fsn = match.get("fsn")
            term = match.get("term")
            title = title.strip()
            term = term and term.strip()
            if fsn and "finding" in fsn and term and term.lower() == title.lower():
                table.set_cell_value(index, "SCTID", concept_id)
                table.set_cell_value(index, "fsn", fsn)
                logging.info("[%s]>[%s][%s]")
        elif title.endswith("s") or title.endswith("es"):
            """
                主要是这两个判断需要同样的处理步骤，只是取得字段内容不一样
            """
            if title.endswith("es"):
                title = title[0:-2]
            elif title.endswith("s"):
                title = title[0:-1]
            TranslateTask().run(TRANSLATE_URL, table, row, index, title)


excel = None

"""
    翻译excel中的ctitle和cabout
"""


class TranslateTask(Task):

    @staticmethod
    def parse(translate_url, value, row, table, header):
        result = None
        try:
            translate_url.set_param("q", value)
            result = translate_url.get()
        except Exception as e:
            logging.error(e)
        if result:
            results = result[0]
            resultStr = "";
            for r in results:
                if r:
                    resultStr = resultStr + r[0]
            table.set_cell_value(row, header, resultStr)

    def run(self, args):
        translate_url, table, row, index, title = args
        about = table.get_cell_value(index, "about")
        ctitle = table.get_cell_value(index, "ctitle")
        cabout = table.get_cell_value(index, "cabout")
        if ctitle is not '' and cabout is not "":
            return
        self.parse(translate_url, title, index, table, "ctitle")
        self.parse(translate_url, about, index, table, "cabout")


def finish():
    excel and excel.save()
    global EXECUTE_NUM
    EXECUTE_NUM = EXECUTE_NUM + 1
    logging.info("sleep start" + str(datetime.datetime.now()))
    time.sleep(10)
    logging.info("sleep end" + str(datetime.datetime.now()))
    exec_task(EXECUTE_NUM)


"""
    excel：执行回掉函数 
    通过线程执行方法
    schedule = Schedule(thread_num=10, finish=finish) 创建线程调度器
    schedule.append_task(GrapTask(), (url, table, row, index, title)) ihtsdotools 查询fsn,stid
    schedule.append_task(TranslateTask(), (translateUrl, table, row, index, title)) 翻译
    非线程执行方法：
    UrlTask.run((url, table, row, index, title),schedule) 查询fsn,stid
    TranslateTask().run((TRANSLATE_URL, table, row, index, title)) 翻译
"""


def callback(table, row, index):
    title = table.get_cell_value(index, "title")
    TranslateTask().run((TRANSLATE_URL, table, row, index, title))


"""
    执行任务
    i：用来解决ihtsdotools访问过于频繁导致的ip被封的情况
    具体逻辑：将excel中逻辑分成多个片段，每个片段执行后睡眠30s
"""

EXECUTE_NUM = 0


def exec_task(execute_num):
    """
        execute_num只针对ihtsdotools封ip的时候才会使用，其余不需要使用
    """
    if execute_num < 232:
        print(execute_num)
    """
        2 1两个数字只是为了生成的目的excel文件和源文件不一致
    """
    desc_name = ("full_match%s.xls" % (str(2)))
    global excel
    excel = ExcelParse("full_match%s.xls" % 1, desc_name=desc_name, callback=callback, offset=0, limit=None)
    try:
        excel.prase_body()
    except Exception as e:
        logging.error("e," + e)
    excel.save()


exec_task(EXECUTE_NUM)
