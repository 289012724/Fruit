# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
import os
import traceback
from Queue import Queue


class AppQueue(object):
    Queues = Queue()

    def __init__(self, appNumber=1):
        pass

    @classmethod
    def GetApp(cls):
        # pythoncom.CoInitialize()
        # app = client.Dispatch('Excel.Application')
        app = object()
        app.Visible = 0
        return app

    @classmethod
    def DeleteFile(cls, fileName):
        if os.path.exists(fileName): os.remove(fileName)

    @classmethod
    def DeleteFolder(cls, folder):
        if os.path.exists(folder): os.rmdir(folder)


class Excel(object):
    """A utility to make it easier to get at Excel.    Remembering 
      to save the data is your problem, as is    error handling. 
      Operates on one workbook at a time."""

    def __init__(self, app):
        self.xlApp = app

    def open(self, filename=None):
        if filename:
            self.xlBook = self.xlApp.Workbooks.Open(filename)
        else:
            self.xlBook = self.xlApp.Workbooks.Add()

    def save(self, newfilename=None):
        """
        @attention: 保存文件
        @param newfilename: 新文件名称 
        """
        if newfilename:
            if os.path.exists(newfilename): os.remove(newfilename)
            self.xlBook.SaveAs(newfilename)
        else:
            self.xlBook.Save()

    def close(self):
        self.xlBook.Close(SaveChanges=0)
        self.xlApp.Quit()
        del self.xlApp

    def getCell(self, sheet, row, col):
        """
        @attention: Get value of one cell
        @param sheet: 表的名称
        @param row: 行
        @param col: 列   
        """
        sht = self.xlBook.Worksheets(sheet)
        return sht.Cells(row, col).Value

    def setCell(self, sheet, row, col, value):
        """
        @attention: set value of one cell
        @param sheet: 表的名称
        @param row: 行
        @param col: 列   
        @param value: 值 
        """
        sht = self.xlBook.Worksheets(sheet)
        sht.Cells(row, col).Value = value

    def getRange(self, sheet, row1, col1, row2, col2):
        """
        @attention: 获取区域块的数据
        @param sheet: 表的名称
        @param row1: 起始行
        @param col: 起始列   
        @param row2: 终止行 
        @param co2: 终止列   
        """
        sht = self.xlBook.Worksheets(sheet)
        return sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2)).Value

    def setRange(self, sheet, row1, col1, data):
        """
        @attention: 获取区域块的数据
        @param sheet: 表的名称
        @param row1: 起始行
        @param col: 起始列   
        @param data: 二维数据 
        """
        sht = self.xlBook.Worksheets(sheet)
        row2 = row1 + len(data) - 1
        col2 = col1 + len(data[0]) - 1
        sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2)).Value = data

    def addPicture(self, sheet, pictureName, Left, Top, Width, Height):
        """
        @attention: 想文件中插入图片
        @param sheet: 表的名称
        @param pictureName: 图片地址
        @param Left: 左边位置
        @param Top:  距顶部位置
        @param Width:图片宽度 
        @param Height:图片高度 
        """
        sht = self.xlBook.Worksheets(sheet)
        sht.Shapes.AddPicture(pictureName, 1, 1, Left, Top, Width, Height)

    def merge(self, sheet, row1, col1, row2, col2):
        """
        @attention: 获取区域块的数据
        @param sheet: 表的名称
        @param row1: 起始行
        @param col: 起始列   
        @param row2: 终止行 
        @param co2: 终止列   
        """
        sht = self.xlBook.Worksheets(sheet)
        sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2)).Merge()

    def setCellformat(self, sheet, row, col):  # 设置单元格的数据
        "set value of one cell"
        sht = self.xlBook.Worksheets(sheet)
        sht.Cells(row, col).Font.Size = 15  # 字体大小
        sht.Cells(row, col).Font.Bold = True  # 是否黑体
        sht.Cells(row, col).Name = "Arial"  # 字体类型
        sht.Cells(row, col).Interior.ColorIndex = 3  # 表格背景
        # sht.Range("A1").Borders.LineStyle = xlDouble
        sht.Cells(row, col).BorderAround(1, 4)  # 表格边框
        sht.Rows(3).RowHeight = 30  # 行高
        sht.Cells(row, col).HorizontalAlignment = -4131  # 水平居中xlCenter
        sht.Cells(row, col).VerticalAlignment = -4160  #

    def setPrint(self, sheet, row1, col1, row2, col2):
        sht = self.xlBook.Workbooks(sheet)
        sht.PageSetup.PrintArea = "$%s$%s:$%s$%s" % (row1, col1, row2, col2)

    def AppendSheetByTemp(self, tempIndex=2):
        shts = self.xlBook.Worksheets
        shts.Add(after=shts.Count())
        last = shts.Count()
        shts(last).Copy(None, shts(tempIndex))
        shts(last).Name = "%02d" % (last - 1)

    def ExcelFormat(self, sheet, row1, col1, row2, col2):
        sht = self.xlBook.Worksheets(sheet)
        rang = sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2))
        rang.Font.Size = 15
        rang.Font.Bold = True
        rang.Font.Name = "Arial"
        #         rang.Interior.ColorIndex = 3
        rang.BorderAround(1, 4)
        sht.Rows("%s:%s" % (row1, row2)).RowHeight = 15
        rang.HorizontalAlignment = -4131
        rang.VerticalAlignment = -4160

    def WriteDataToExcelNull(self, data, fileName):
        if os.path.exists(fileName):
            os.remove(fileName)
        self.open()
        self.ExcelFormat(1, 1, 1, len(data), len(data[0]))
        try:
            self.setRange(1, 1, 1, data)
            return True
        except:
            traceback.print_exc()
            return False


class ExcelToPdf(object):
    """
    @attention: 将输入的excel文件转换为PDF文件,未调整任何excel文件的格式
    """

    def __init__(self):
        object.__init__(self)
        self.__excelApp = AppQueue.GetApp()
        self.FileFormat = 57

    @property
    def ExcelList(self):
        return self.__excels

    @ExcelList.setter
    def ExcelList(self, value):
        if not isinstance(value, list):
            value = [value]
        self.__excels.extend(value)

    @property
    def Pdfs(self):
        return self.__pdfs

    @Pdfs.setter
    def Pdfs(self, value):
        self.__pdfs.append(value)

    def GetPdfName(self, excelPath):
        """
        @attention: get the filename path of PDF file,filename is same as input file
        @param excelPath: the excel filename path 
        """
        basePath = os.path.dirname(excelPath)
        fileName = os.path.basename(excelPath).split(".")[0]
        return os.path.join(basePath, "%s.pdf" % fileName).encode("CP936")

    def SelectChangeSheet(self, workBook):
        shts = workBook.Worksheets
        for index in range(1, shts.Count + 1):
            shts(index).Select(False)

    def ExcelToPdfOne(self, excelPath):
        """
        @attention: start to change excel file to pdf file
        @param excelPath: the excel filename path 
        """
        workBook = self.__excelApp.Workbooks.Open(excelPath.encode("CP936"))
        pdf = self.GetPdfName(excelPath)
        self.SelectChangeSheet(workBook)
        workBook.SaveAs(pdf, FileFormat=self.FileFormat)
        self.__pdfs.append(pdf)
        workBook.Close()

    def Main(self, excelList):
        """
        @attention: change excel list  to PDF file list
        @param excelList: excel files or one excel file
        """
        self.__pdfs = []
        self.__excels = []
        self.ExcelList = excelList
        map(self.ExcelToPdfOne, self.ExcelList)
        self.__excelApp.Quit()
        print "转换excel 文件成功"


def export_pdf():
    excel = r"C:\Users\Administrator\Desktop/2016-11-28.xlsx"
    ExcelToPdf().Main(excel)


def to_execl():
    print "start"
    AppQueue()
    fileName = r"C:\Users\Administrator\Desktop/2016-11-28.xlsx"
    app = AppQueue.GetApp()
    _excel = Excel(app)
    _excel.save(fileName)
    _excel.close()
    print "end"


if __name__ == '__main__':
    export_pdf()
