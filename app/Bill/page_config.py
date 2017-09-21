# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@time: 
"""
_cstbill = [
         {'field': 'date',          'title': u'日期',      'width': 100},
         {'field': 'tickets',       'title': u'凭据号',    'width': 100},
         {'field': 'sell_type',     'title': u'类别',      'width': 80},
         {'field': 'customer_id',   'title': u'客户',      'width': 80},
         {'field': 'name',          'title': u'品名',      'width': 80},
         {'field': 'brand_id',      'title': u'品牌',      'width': 80},
         {'field': 'standard',      'title': u'规格',      'width': 80},
         {'field': 'number',        'title': u'数量',      'width': 80},
         {'field': 'price',         'title': u'单价',      'width': 80,"formatter":"1"},
         {'field':'total_price',    'title': u'金额',      'width':80,"formatter":"1"},
         {'field': 'money_id',      'title': u'已收款',    'width': 80,"formatter":"1"},
         {'field': 'bill_money',      'title': u'账单金额',  'width': 80,"formatter":"1"},
         {'field': 'notice',        'title': u'备注',      'width': 100}, 
         ]

_sptbill = [
         {'field': 'date',          'title': u'日期',      'width': 80},
         {'field': 'tickets',       'title': u'凭据号',    'width': 100},
         {'field': 'category',      'title': u'类别',      'width': 60},
         {'field': 'support_id',    'title': u'供货商',    'width': 60},
         {'field': 'name',          'title': u'品名',      'width': 100},
         {'field': 'brand_id',      'title': u'品牌',      'width': 100},
         {'field': 'standard',      'title': u'规格',      'width': 100},
         {'field': 'car_number',    'title': u'车牌柜号',  'width': 80},
         {'field': 'number',        'title': u'数量',      'width': 60},
         {'field': 'price',       'title': u'单价',      'width': 60,"formatter":"1"},
         {'field': 'all_money',     'title': u'金额',      'width': 100,"formatter":"1"},
         {'field': 'notice',        'title': u'备注',      'width': 100},
         ]
_bill_manager = [
         {'field': 'id',            'title': u'编号',          'width': 100},
         {'field': 'date',            'title': u'月份',          'width': 80},
         {'field': 'customer_id',   'title': u'客户',          'width': 80},
         {'field': 'p_total',    'title': u'上月账单',      'width': 120,"formatter":"1"},
         {'field': 'prev_money',    'title': u'上月余额',      'width': 120,"formatter":"1"},
         {'field': 'writeOff',      'title': u'本月冲销',      'width': 120,"formatter":"1"},
         {'field': 'rebund',        'title': u'本月还款',      'width': 120,"formatter":"1"},
         {'field': 'rebate',        'title': u'本月折扣',      'width': 120,"formatter":"1"},
         {'field': 'total_money',   'title': u'本月对账单合计','width': 120,"formatter":"1"},
         {'field': 'cell_money',   'title': u'本月账单',      'width': 120,"formatter":"1"},
#          {'field': 'has_filled',    'title': u'已结帐',        'width': 60},
         {'field': 'operator_id',   'title': u'经办人',        'width': 60},
         ]
_forget  = [
         {'field': 'customer_id',   'title': u'客户',         'width': 80},
         {'field': 'prev_bill',     'title': u'上月账单金额', 'width': 100},
         {'field': 'writeOff',      'title': u'本月冲销',     'width': 100},
         {'field': 'rebund',        'title': u'还款',         'width': 100},
         {'field': 'rebate',        'title': u'折扣',         'width': 80},
         {'field': 'writeOff',      'title': u'冲销',         'width': 120,"formatter":"1"},
         {'field': 'next_money',    'title': u'上月余款',     'width': 120,"formatter":"1"},
         {'field': 'rebund',        'title': u'还款',         'width': 100,"formatter":"1"},
         {'field': 'rebate',        'title': u'折扣',         'width': 100,"formatter":"1"},
         {'field': 'writeOff',      'title': u'冲销',         'width': 100,"formatter":"1"},
         {'field': 'has_filled',    'title': u'已还',         'width': 80},
         {'field': 'operator_id',   'title': u'经办人',       'width': 60},
         ]
def addCenter(cell):
    for _c in cell:
        if _c.get("field")=="id":
            _c.update({'hidden':True})
        _c.update({'align':'center'})
    return cell
page_table_configs ={
    "cstbill":addCenter(_cstbill),
    "sptbill":addCenter(_sptbill),
    "bill_manager":addCenter(_bill_manager),
    "forget":addCenter(_forget),
    }
