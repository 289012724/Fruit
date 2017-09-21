# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: views.py
@time: 2016/7/11 0011
"""
import os
from flask  			import request, make_response, send_file
from ...common 			import _dataBaseUtil
from ... 				import database
from flask_login 		import current_user
from werkzeug.utils 	import secure_filename
from flask import current_app

class UpLoadDataBase:
	User = ["fruit_users","fruit_departments"]
	Pro  = ["fruit_stocks", "fruit_sells", "fruit_roll_backs", "fruit_roll_outs"]
	Fin  = ['fruit_bill_rebund','fruit_bill_rebate','fruit_bill_writeoff','fruit_bill_bill']
	
	def get_oper_user(self,index):
		index = int(index) - 13
		return UpLoadDataBase.User[index]

	def get_oper_finance(self,index):
		index = int(index) - 6
		if index <=3:
			data = UpLoadDataBase.Fin[index]
		else:
			data = " ".join(UpLoadDataBase.Fin)
		return data
	def get_oper_production(self,index):
		index= int(index) - 1
		if index <=3:
			data = UpLoadDataBase.Pro[index]
		else:
			data = " ".join(UpLoadDataBase.Pro)
		return data

	def get_oper(self, index):
		"""
		@attention: 根据用户选的数据库名称类确定导出那个数据表的内容
		"""
		index = int (index)
		if index < 13:
			if index>=1 and index <= 5:
				data = self.get_oper_production(index)
			elif  6<= index and index <= 11:
				data = self.get_oper_finance(index)
			else:
				data = UpLoadDataBase.Pro+UpLoadDataBase.Fin
				data =" ".join(data)
				print data
		else:
			data = self.get_oper_user(index)
		return data

	def create_bat_cmmond(self, index):
		"""
		@attention: 创建导出数据的bat执行语句
		"""
		batStr = "mysqldump -uroot -p123456 --no-create-info --databases fruit --tables %s"
		oper   = self.get_oper(index)
		return batStr % oper
	
	def dump(self, _bat, _dw):
		"""
		@attention: 创建导出数据的 where 查询条件
		@param _bat: bat 文件路径 现在不是用
		@param _dw:  导出数据写入的地址 
		"""
		index 	 = request.form.get("database_name") 
		dateFrom = request.form.get('dateFrom') 
		dateTo   = request.form.get("dateTo") 
		batS 	 = self.create_bat_cmmond(index)
		_where 	 = ''
		if dateFrom:
			_where += "date >= '%s'" % dateFrom
			if dateTo:
				_where += " AND date<= '%s'" % dateTo
		else:
			if dateTo:
				_where = "date <= %s" % dateTo
		if _where:
			batS += ' --where "%s"' % _where
		batS = batS + " >%s" % _dw
		return batS

	def get_temp_file(self):
		"""
		@attention: 获取临时的bat 文件路径和 导出数据的 文件路径
		"""
		path 	= "c:/temp"
		if not os.path.exists(path):os.mkdir(path)
		_file 	= "%s/%s_dump.bat" % (path,current_user.username)
		_file2 	= "%s/%s_dump.sql" % (path,current_user.username)
		return _file,_file2

	def dumpData(self):
		"""
		@attention: 导出用户指定的数据
		"""
		_bat, _dw = self.get_temp_file()
		batS 	  = self.dump(_bat, _dw)
		res 	  = os.system(batS)
		if res == 0:
			return _dataBaseUtil.ResOkJson(_dw)
		return _dataBaseUtil.ResErrorJson("导出数据失败")
	
	def downLoad(self):
		"""
		@attention: 下载用户最近一次导出的数据
		"""
		_fileName= self.get_temp_file()[-1]
		_name    = _dataBaseUtil.CurrentDateStr
		_name	 = "%s_dump_%s.sql"%( current_user.username,_name )
		response = make_response(send_file(_fileName))
		response.headers["Content-Disposition"] = "attachment; filename=%s;" % _name.encode("utf-8")
		return response
	
	def checkHasIn(self,tableName,uuid):
		"""
		@attention: 检测该行数据是否已经存在
		"""
		sql = "select id from %s where id='%s'"%(tableName,uuid)
		data= database.get_engine(current_app).execute(sql).fetchall()
		return data
	
	def anaytable(self,path):
		"""
		@attention: 过滤掉已经存在的数据行
		@param path: 用户上传的文件 
		"""
		fp    = open(path,'r')
		lines = fp.readlines()
		fp.close()
		isstart= False
		name  =""
		_dict = {}
		okline= []
		for line in lines:
			if line.startswith("LOCK"):
				name    = line.split(" ")[2].replace("`","")
				isstart = True
				okline.append(line)
				continue
			
			if line.startswith("UNLOCK"):
				okline.append(line)
				isstart= False
				name   = ""
				continue
			
			if isstart:
				if line.startswith("INSERT"):
					uuid = line.split("(")[1].split(",")[0]
					if not self.checkHasIn(name, uuid):
						okline.append(line)
		path	= path.split(".")[0]+'-b.sql'
		fp		=open(path,'w')
		fp.writelines(okline)
		fp.close()
		return path
	
	def importDataToMysql(self,oldPath):
		"""
		@attention: 将上传的文件导入到数据库中
		@note: 当前没有使用 mysqldump的导入功能，目前存在异常
		"""
		okPath = self.anaytable(oldPath)
		dbses  = database.get_engine(current_app)
		_file  = open(okPath)
		lines  = _file.readlines()
		_file.close()
		for line in lines:
			try:
				dbses.execute(line)
			except Exception,e:
				self.delete_down_ok(okPath)
				self.delete_down_ok(oldPath)	
				return _dataBaseUtil.ResErrorJson("导入数据失败:%s"%e.message);
		self.delete_down_ok(okPath)
		self.delete_down_ok(oldPath)
		return _dataBaseUtil.ResOkJson(u"导入数据成功")
	
	def importData(self):
		ufile = request.files.get('file_name')
		down  = current_app.config.get("DOWNLOAD_FILE")
		if ufile:
			fname = secure_filename(ufile.filename) 
			path  = os.path.join(down, fname)
			ufile.save(path)
			return self.importDataToMysql(path)
			
			if self.importDataToMysql(path) :
				return _dataBaseUtil.ResOkJson(path)
			else:
				return _dataBaseUtil.ResErrorJson("数据写入数据库失败");
		else:
			return _dataBaseUtil.ResErrorJson("导入文件有误")
	
	def delete_down_ok(self,_file):
		if os.path.exists(_file):os.remove(_file)
	
	def delete_down_ok_file(self):
		_path = self.get_temp_file()[1]
		self.delete_down_ok(_path)
