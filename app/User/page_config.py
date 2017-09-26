# -*- coding:utf-8 -*-
'''
@email:289012724@qq.com
@author: shuiyaoyao
@telephone:13587045516
'''

department =[
                {'field': 'id', 'title': u'编号', 'width': 60},
                {'field': 'name', 'title': u'部门名称', 'width': 150},
                {'field': 'description', 'title': u'描述', 'width': 550}
]

user       = [
                {'field': 'id', 'title': u'编号', 'width': 60},
                {'field': 'username', 'title': u'用户名', 'width': 150},
                {'field': 'department_id', 'title': u'部门', 'width': 250},
                {'field': 'telephone', 'title': u'联系方式', 'width': 250},
                {'field':"state", 'title':u"状态", 'width':100 }
]

def addCenter(cell):
    for _c in cell:
        if _c.get("field")=="id":
            _c.update({'hidden':True})
        _c.update({'align':'center'})
    return cell

page_table_configs = {
    "department":addCenter(department),
    "user":addCenter(user),
    }
