# -*- coding:utf-8 -*-
'''
@email:289012724@qq.com
@author: shuiyaoyao
@telephone:13587045516
'''
from ..                         import app,database
from flask_admin                import expose,Admin,AdminIndexView,BaseView
from flask_admin.contrib.sqla   import ModelView
from flask_login                import current_user
from ..Production.models        import stock,sell,roll_back,roll_out
from flask                      import request,session
from flask_babelex              import Babel
from ..common                   import _dataBaseUtil
import copy
babel = Babel(app)
from ..common import _dataBaseUtil as dataUtil

user  = dataUtil.getDataBase("UserOperate", "User")
money = dataUtil.getDataBase("money", "Production")

def get_isout(data):
    return [u'否',u'是'][data]

def get_money(ids):
    _my = dataUtil.getModel(money,id=ids)[0]
    return "%s@%s@%s"%(ids,_my.price,_my.money_type)

def get_name(ids):
    return dataUtil.getModel(user,id=ids)[0].username

@babel.localeselector
def get_locale():
    override = request.args.get('lang')
    if override:
        session['lang'] = override
    return session.get('lang', 'zh_Hans_CN')

class FruitView(AdminIndexView):
    @expose('/')
    def index(self):
        arg1 = 'home'
        if current_user.is_authenticated:
            return self.render('Admin/AdminIndex.html',arg1=arg1)
        else:
            return u"请用管理员帐户登录"

class InputDataView(BaseView):
    @expose('/')
    def index(self):
        return self.render('Admin/InputDialog.html',date=_dataBaseUtil.CurrentDateStr)
    
class BaseModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.username =='admin'
    column_display_pk   = True
    can_create          = False
    can_view_details    = True
    can_export          = True
    column_searchable_list = ['id', 'date','tickets']
    column_filters      = column_searchable_list
    column_labels       = {
        'id': u'编号',
        'notice':u"备注",
        'notice_a':u"备注A",
        'date':u"日期",
        'operator_id':u"经办人",
        'support_id':u"供应商",
        'customer_id':u"客户",
        "tickets":u"凭据号",
        'number':u"数量",
        'price':u"价格",
        'stock':u"入库",
        'sell':u"销售",
    }
    column_formatters = {
        'date' : lambda v, c, m, p: ("%s"%m.date).split(" ")[0],
        'support_id':lambda v, c, m, p:get_name(m.support_id),
         'operator_id':lambda v, c, m, p:get_name(m.operator_id),
        'customer_id':lambda v, c, m, p:get_name(m.customer_id),
        'money_id':lambda v, c, m, p:get_money(m.money_id),
        'isout':lambda v, c, m, p:get_isout(m.isout),
    }
class StockModelView(BaseModelView):
    column_labels = copy.deepcopy(BaseModelView.column_labels)
    column_searchable_list = copy.deepcopy(BaseModelView.column_searchable_list)
    column_searchable_list.extend(["name",'support_id','isout'])
    column_filters = column_searchable_list
    column_labels.update({
        'name':u"品名",
        'brand_id':u"品牌",
        'standard':u"规格",
        'car_number':u"车牌柜号",
        'category':u"类别",
        'isout':u"已售完",
        'sells':u"销售",
        'rolls':u"转出/报损",
    })
    
class SellModelView(BaseModelView):
    column_labels = copy.deepcopy(BaseModelView.column_labels)
    column_searchable_list = copy.deepcopy(BaseModelView.column_searchable_list)
    column_searchable_list.extend(["sell_type",'customer_id'])
    column_filters = column_searchable_list
    column_labels.update({
        'sell_type':u"类型",
        'price_a':u"备注价格",
        'money_id':u"付款",
        'roll_backs':u"退货",
    })

class RollOutModelView(BaseModelView):
    column_labels = copy.deepcopy(SellModelView.column_labels)
    column_searchable_list = copy.deepcopy(BaseModelView.column_searchable_list)
    column_searchable_list.extend(["roll_type"])
    column_filters = column_searchable_list
    column_labels.update({
        'reason':u"原因",
        'roll_type':u"类别",
    })
class RollBackModelView(BaseModelView):
    column_labels = copy.deepcopy(SellModelView.column_labels)
    column_searchable_list = copy.deepcopy(BaseModelView.column_searchable_list)
    column_searchable_list.extend(["roll_type"])
    column_filters = column_searchable_list
    column_labels.update({
        'roll_type':u"类别",
    })

admin = Admin(app,name=u'后台管理',index_view=FruitView())
admin.add_view(InputDataView(name=u"导入/导出"))
admin.add_view(StockModelView(stock, database.session,name=u'入库'))
admin.add_view(SellModelView(sell, database.session,name=u'销售'))
admin.add_view(RollBackModelView(roll_back, database.session,name=u'退货'))
admin.add_view(RollOutModelView(roll_out, database.session,name=u'转出/报损'))

