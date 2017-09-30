/** 格式化输入字符串* */
// 用法: "hello{0}".format('world')；返回'hello world'
String.prototype.format = function() {
	var args = arguments;
	return this.replace(/\{(\d+)\}/g, function(s, i) {
		return args[i];
	});
}

function identify_select(id, _select_data) {
	return $(id).datagrid("getRowIndex", _select_data);
}

function get_datagrid_select(id, isRow) {
	var _select = $(id).datagrid("getSelected");
	if (isRow) {
		return identify_select(id, _select);
	} else {
		return _select;
	}
}

function formateDate(date, id) {
	var day = date.getDate() > 9 ? date.getDate() : "0" + date.getDate();
	var month = (date.getMonth() + 1) > 9 ? (date.getMonth() + 1) : "0"
			+ (date.getMonth() + 1);
	var date = date.getFullYear() + '/' + month + '/' + day;
	if (id) {
		$(id).datebox('setValue', date);
	}
	return date;
}

function _$(id) {
	return $('#' + id);
}

function Fmoney() {
	var _o = new Object();
	_o.prefix = "￥";
	_o.money  = function (s) {
		if(!s){return s}
		var n = 2;
		n = n > 0 && n <= 20 ? n : 2;
		s = parseFloat((s + "").replace(/[^\d\.-]/g, "")).toFixed(n) + "";
		var l = s.split(".")[0].split("").reverse(), r = s.split(".")[1];
		var t = "";
		for (i = 0; i < l.length; i++) {
			t += l[i] + ((i + 1) % 3 == 0 && (i + 1) != l.length ? "," : "");
		}
		var _money = _o.prefix + t.split("").reverse().join("") + "." + r;
		var _money = _money.trim().replace("-,","-");
		return _money
	}
	_o.rmoney = function (s){
		var data = String(s);
		if(data && data.substring(0,1) == _o.prefix){
			data = s.replace(_o.prefix,"").trim();
			data = parseFloat(data.replace(/[^\d\.-]/g, ""));   
		}
		return data;
	}
	_o.main =function(option){
		for(var key in option){
			_o[key] = option[key];
		}
	}
	return _o;
}

_Fmoney = Fmoney();
