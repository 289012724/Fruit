# -*- coding:utf-8 -*-
'''
@author: Administrator
'''
import unittest

from ...DataBaseOperate    import _dataBaseUtil

class Test(unittest.TestCase):

    def testGetDataBase(self):
        print _dataBaseUtil.getDataBase("user", 1)
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()