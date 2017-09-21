/**
 * Created by Administrator on 2016/7/27 0027.
 */

window._success_msg = "";
window._global = new Object();

function allCommon(date,dateId) {
	$('.btn-primary').css('width', '120px');
	$(dateId).val(date);
	$('#notice').css('resize', 'none').css('height', 60);
	$('input[name="operator_id"]').attr('disabled', 'disabled');
}

function Util() {
	var _o = new Object();
	_o.clearInit = function(divId,dataType){
		dataType = dataType || "input[type='text']";
		$("#" + divId.trim("#") +" "+dataType).val("");
	}
	_o.get_partial=function(parentFilter){
		return function(element_id){
			element_id = element_id.trim("#");
			return $("#" + parentFilter +" #"+element_id);
		}
	}
	_o.get_option_selected = function(id) {
		return $(id + " option:selected").val()
	}
	_o.get_option_selected_text = function(id) {
		return $(id + " option:selected").text()
	}
	_o.get_serialize_obj = function(form_id) {
		var _data = $(form_id).serializeArray();
		var _o = new Object();
		for ( var _one in _data) {
			_cell = _data[_one];
			_o[_cell.name] = _cell.value;
		}
		return _o;
	}
	_o.get_tickets = function(prefix) {
		tickets = $('#tickets').val();
		return tickets
	}
	_o.get_datagrid_row_index = function(_data, datagrid_id) {
		return $(datagrid_id).datagrid('getRowIndex', _data);
	}
	_o.get_datagrid_row_value = function(row, datagrid_id) {
		return $(datagrid_id).datagrid('getData')[row];
	}

	_o.msgBase = function(msg, state) {
		$.messager.alert("提示", msg, state);
	}
	_o.msgError = function(msg) {
		this.msgBase(msg, "error");
	}
	_o.msgInfo = function(msg) {
		this.msgBase(msg, "infor");
	}
	_o.msgQues = function(msg) {
		this.msgBase(msg, "question");
	}
	_o.msgWarn = function(msg) {
		this.msgBase(msg, "warning");
	}
	_o.confirm = function(msg, func) {
		$.messager.confirm('确认', msg, function(r) {
			if (r) {func(arguments);}
		});
		return false;
	}
	_o.form_ajax = function(url, data, success) {
		$.ajax({
		    url : url,
		    method : 'POST',
		    data : data,
		    success : success
		})
	}
	_o.common_success = function(data) {
		if (!data['state']) {
			$.messager.alert('错误', data['msg'], 'error');
		} else {
			$.messager.show({
			    title : '提示',
			    msg : window._success_msg,
			    timeout : 1000,
			    iconCls : 'icon-ok',
			});
		}
	}
	_o.add_or_insert = function(data,datagrid) {
		if (_global.selected == null) {
			$(datagrid).datagrid("insertRow", {
			    index : 0,
			    row : data.msg[0],
			});
			$(datagrid).data("filterObj").add_row(data.msg[0],0);
		} else {
			$(datagrid).datagrid("updateRow", {
			    index : _global.selected,
			    row : data.msg[0]
			});
			$(datagrid).data("filterObj").modify_row(data.msg[0]);
		}
	}
	return _o;
}
function comgridOpt() {
	var _o = new Object();
	_o.dataid = null;
	_o.old_data = null;
	_o.selectId = null;
	_o.filed = null;
	_o.selectData = null;
	_o.selectRow = null;
	_o.selectRowFun = null;
	_o._init_data = function() {
		if (_o.old_data == null) {
			_o.old_data = $(_o.id).combogrid('grid')
								  .datagrid('getData');
		}
	}

	_o.get_partial=function(parentFilter){
		return function(element_id){
			element_id = element_id.trim("#");
			return $("#" + parentFilter +" #"+element_id);
		}
	}
	_o._get_new_data = function(rowData, newData) {
		_data = [];
		var newData = newData.toString().replace("_", "")
		for ( var _one in rowData) {
			rowData[_one][_o.filed].toString()
					.indexOf(newData) != -1 ? _data
			        .push(rowData[_one]) : 0;
		}
		return _data
	}
	_o.get_filter_data = function(rowData, newData) {
		_data = rowData;
		if (newData)
			_data = _o._get_new_data(rowData, newData);
		return _data;
	}

	_o.filter_data = function(newData) {
		_data = _o.get_filter_data(_o.old_data.rows, newData);
		_o._refresh_select(_data, null);
	}
	_o._refresh_select = function(_data, _select_id) {
		$(_o.id).combogrid('grid').datagrid('loadData', {
		    total : _data.length,
		    rows : _data
		});
		if (_select_id != null) {
			$(_o.id).combogrid('grid')
					 .datagrid('selectRow', _select_id);
		}
	}
	_o.main = function(id, filterField) {
		_o.id = id;
		_o.selectId = null;
		_o.filed = filterField;
	}
	_o.onChange = function(newValue, oldValue) {
		_oldData = _o._init_data();
		_o.filter_data(newValue);
		if (!newValue) {
			_o.selectId = null;
			_o.selectData = null;
		}
	}
	_o.onClickRow = function(rowIndex, rowData) {
		var _str = "_" + rowData[_o.filed].toString();
		_o.setValue(_str);
		_o.selectId = rowData.id;
		_o.selectData = rowData;
		_o.selectRow = rowIndex;
		if (_o.selectRowFun != null) {
			_o.selectRowFun();
		}
	}
	_o.setValue = function(string) {
		$(_o.id).combogrid('setValue', string);
	}
	_o.remove = function(index) {
		_o.old_data.rows.splice(index, 1);
		_o.old_data.total -= 1;
	}
	return _o;
}

function deleteLine() {
	var _o = new Object();
	_o.datagridId = "#datagrid";
	_o.confirmMsg = "是否删除选中数据?";
	_o.element_id = "#delete";
	function check(data) {
		return data
	}
	function closeFunction(data) {
		concole.log("未删除数据");
	}
	function okFunction(data) {
		if (data.state) {
			$(_o.datagridId).datagrid('deleteRow', _index);
		} else {
			_util.msgError(data.msg);
		}
	}

	function delete_one_line(data) {
		_index = $(_o.datagridId).datagrid("getRowIndex", data);
		query_data = {
		    'data_id' : data.id,
		    "operType" : _o.operType
		};
		$.ajax({
		    url : _o.delete_url,
		    method : 'POST',
		    data : query_data,
		    success : _o.okFunction,
		});
	}

	function _confirmData(isTrue) {
		if (isTrue) {
			var selections = $(_o.datagridId).datagrid('getSelections');
			for ( var index in selections) {
				var data = selections[index];
				if (_o.check) {
					data = _o.check(data);
				}
				_o.delete_one_line(data);
			}
		} else {
			if (_o.closeFunction) {
				_o.closeFunction();
			}
		}
	}
	_o.bind = function() {
		$(_o.element_id).bind('click', function() {
			$.messager.confirm("确认", _o.confirmMsg, _confirmData);
		});
	}
	_o.main = function(option) {
		$.extend(_o,option);
		_o.bind();
	}
	return _o
}

var _util = Util();
var _global = window._global;
var _comgridOpt = comgridOpt();
var _deletUtil = deleteLine();