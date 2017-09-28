# -*- coding:utf-8 -*-
"""
@author: shuiyaoyao
@email  : 289012724@qq.com
"""
_buyorsell = [
    {"field": "date", "title": u"入库时间", "width": 80},
    {"field": "category", "title": u"类别", "width": 50},
    {"field": "name", "title": u"品名", "width": 80},
    {"field": "brand_id", "title": u"品牌", "width": 80},
    {"field": "standard", "title": u"规格", "width": 80},
    #          {"field": "price",     "title": u"价格",     "width": 60},
    {"field": "support_id", "title": u"供货商", "width": 80},
    {"field": "notice", "title": u"入库备注", "width": 80},
    {"field": "notice_a", "title": u"入库备注A", "width": 80},
    {"field": "curstock", "title": u"今日库存", "width": 80},
    {"field": "prestock", "title": u"昨日库存", "width": 80},
    {"field": "stock", "title": u"今日入库", "width": 80},
    {"field": "sell", "title": u"今日销售", "width": 80},
    {"field": "rollback", "title": u"今日退货", "width": 80},
    {"field": "rollloss", "title": u"今日报损", "width": 80},
    {"field": "rollout", "title": u"今日转出", "width": 80},
    {"field": "total_price", "title": u"库存总价", "width": 140, "formatter": "1"},
]
_sell = [
    {"field": "date", "title": u"日期", "width": 80},
    {"field": "customer_id", "title": u"客户", "width": 100},
    {"field": "tickets", "title": u"凭据号", "width": 100},
    {"field": "name", "title": u"品名", "width": 80},
    {"field": "brand_id", "title": u"品牌", "width": 80},
    {"field": "standard", "title": u"规格", "width": 80},
    {"field": "number", "title": u"销售数量", "width": 80},
    {"field": "rollNumber", "title": u"退货数量", "width": 80},
    {"field": "price", "title": u"销售单价", "width": 80, "formatter": "1"},
    {"field": "all_price", "title": u"总金额", "width": 80, "formatter": "1"},
    {"field": "has_get", "title": u"已收账款", "width": 80, "formatter": "1"},
    {"field": "for_get", "title": u"应收账款", "width": 80, "formatter": "1"},
    {"field": "sell_type", "title": u"销售类别", "width": 100},
    {"field": "car_number", "title": u"车牌柜号", "width": 100},
    {"field": "category", "title": u"入库类别", "width": 100},
    {"field": "support_id", "title": u"供货商", "width": 80},
]
_profit = [
    {"field": "date", "title": u"日期", "width": 80},
    {"field": "tickets", "title": u"凭据号", "width": 80},
    {"field": "customer_id", "title": u"客户", "width": 80},
    {"field": "name", "title": u"品名", "width": 80},
    #          {"field": "brand_id",      "title": u"品牌",     "width": 80},
    {"field": "standard", "title": u"规格", "width": 80},
    #          {"field": "car_number",    "title": u"车牌柜号", "width": 80},
    {"field": "support_id", "title": u"供货商", "width": 80},
    {"field": "category", "title": u"入库类别", "width": 100},
    {"field": "stock_notice", "title": u"入库备注", "width": 100},
    {"field": "all_number", "title": u"数量", "width": 60},
    {"field": "price", "title": u"销售单价", "width": 80, "formatter": "1"},
    {"field": "stock_price", "title": u"入库单价", "width": 80, "formatter": "1"},
    {"field": "sell_all", "title": u"销售总额", "width": 80, "formatter": "1"},
    {"field": "stock_all", "title": u"成本总额", "width": 80, "formatter": "1"},
    {"field": "all_price", "title": u"利润", "width": 80, "formatter": "1"},
    #          {"field": "notice",        "title": u"销售备注", "width": 100},
]
_agent = [
    {"field": "date", "title": u"日期", "width": 100},
    {"field": "_type", "title": u"事项", "width": 80},
    {"field": "support_id", "title": u"供货商", "width": 80},
    {"field": "customer_id", "title": u"客户", "width": 100},
    {"field": "name", "title": u"品名", "width": 80},
    {"field": "brand_id", "title": u"品牌", "width": 80},
    {"field": "standard", "title": u"规格", "width": 80},
    {"field": "car_number", "title": u"车牌柜号", "width": 100},
    {"field": "stock_notice", "title": u"入库备注", "width": 100},
    {"field": "number", "title": u"数量", "width": 80},
    #          {"field": "rollNumber",    "title": u"退货数量", "width": 80},
    {"field": "price", "title": u"单价", "width": 80, "formatter": "1"},
    {"field": "all_price", "title": u"总金额", "width": 80, "formatter": "1"},
    {"field": "notice", "title": u"备注", "width": 100}
]


def addCenter(cell):
    for _c in cell:
        if _c.get("field") == "id":
            _c.update({'hidden': True})
        _c.update({'align': 'center'})
    return cell


page_table_configs = {
    "buyorsell": addCenter(_buyorsell),
    "sell": addCenter(_sell),
    "agent": addCenter(_agent),
    "profit": addCenter(_profit)
}
