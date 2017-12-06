import xlrd
from xlutils3.copy import copy


class ExcelParse(object):
    """
        path:excel路径
        sheet:excel中的sheet下表
        head_index:excel标题头所在的行数
        callback：遍历每一行的回掉
        offset：内容体遍历的起始位置
        limit：遍历的总记录数
        descName：最终生成的excel
    """
    def __init__(self, path, sheet=0, head_index=0, callback=None, offset=0, limit=None, desc_name="aaa.xls"):
        data = xlrd.open_workbook(path)
        self.table = data.sheet_by_index(sheet)
        self.nrows = self.table.nrows
        self.callback = callback
        self.headIndex = head_index
        self.ncols = self.table.ncols
        self.headers = []
        self.bodys = []
        self.limit = limit
        self.descTable = copy(data)
        self.desc_name = desc_name
        self.offset = offset
        self.parse_header()

    def parse(self):
        for i in range(self.nrows):
            row = self.table.row_values(i)
            # data = self.callback and self.callback(self.table, row)
            self.callback and self.callback(self.table, row)

    def prase_body(self):
        start = self.offset or (self.headIndex + 1)
        end = (self.limit + start) if None is not self.limit else self.nrows
        for bodyIndex in range(start, end):
            self.callback and self.callback(self, self.table.row_values(bodyIndex), bodyIndex)

    def parse_header(self):
        head = self.table.row_values(self.headIndex)
        for i in range(self.ncols):
            self.headers.append(head[i])

    """
        获取单元格的值
    """
    def get_cell_value(self, row_index, header):
        row = self.table.row_values(row_index)
        index = self.headers.index(header)
        return row[index]

    """
        设置excel的单元格的值
    """
    def set_cell_value(self, row_index, header, value, sheet=0):
        index = self.headers.index(header)
        table = self.descTable.get_sheet(sheet)
        table.write(row_index, index, value)

    """
    保存
    """
    def save(self):
        self.descTable.save(self.desc_name)

# http://browser.ihtsdotools.org/api/v1/snomed/en-edition/v20170731/descriptions?query=Headaches&limit=50&searchMode=partialMatching&lang=english&statusFilter=activeOnly&skipTo=0&returnLimit=100&normalize=true
# table, nRows = read_excel("../sym_about.xlsx")
# print nRows
