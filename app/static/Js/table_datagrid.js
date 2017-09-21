/**
 * 
 */
function tabelGrid() {
    var _o                  = new Object();
    _o.datagridId           = null;
    _o.loadMsg              = "正在加载数据,请稍等......";
    _o.toolbarId            = null;
    _o.registerDialogId     = null;
    _o.url_load_data        = null;
    _o.url_table_config     = null;
    _o.load_data_at_start   = false;
    _o.old_data             = null;
    _o.pageSize             = 50;
	
	_o.formatter =function(data) {
	    _formatter = function(value, row, index) {
	        return _Fmoney.money(value);
	    }
	    for (index = 0; index < data.length; index++) {
	        one = data[index];
	        for (var key in one) {
	            if (one.formatter == "1") {
	                one.formatter = _formatter;
	            }
	        }
	    }
	}

    _o.refresh_footer = function(data) {
        var _obj = {};
        for (var j = 0; j <= data.length; j++) {
            for (var key in data[j]) {
                var _d = _Fmoney.rmoney(data[j][key]);
                if (_obj[key] == undefined) {
                    if (_d && !isNaN(_d)) {
                        _obj[key] = parseFloat(_d);
                    } else {
                        _obj[key] = _d;
                    }
                } else {
                    if (_d && !isNaN(_d)) {
                        _obj[key] += parseFloat(_d);
                    }
                }
            }
        }
        _obj['id'] = "汇总";
        var footer = $(_o.datagridId).datagrid("getFooterRows");
        footer[0] = _obj;
        $(_o.datagridId).datagrid("reloadFooter");
    }

    function __ajax() {
        $.ajax({
            url: _o.url_table_config,
            success: function(data) {
                _init_(data);
            }
        });
    }

    function _init_(data) {
        _o.formatter(data);
        $(_o.datagridId).datagrid({
            rownumbers: true,
            fit: true,
            columns: [data],
            striped: true,
            loadMsg: _o.loadMsg,
            toolbar: _o.toolbarId,
            fitColumns: false,
            singleSelect: true,
            autoRowHeight: false,
            showFooter: true,
            pageSize: _o.pageSize,
            view: scrollview,
            onLoadSuccess: function(data) {
                if(data.rows.length !=0){
                    _filter = $(_o.datagridId).data("filterObj");
                    _total  = _filter.filterFeildData;
                    setTimeout(_o.refresh_footer(_total.rows), 1);
                }
            }
        });
        if(_o.url_load_data)_o.load_data(_o.url_load_data);
    	
    }
    _o.load_data=function(url){
    	$.ajax({
        	url: url,
        	method:"post",
        	success:function(data){
        		$(_o.datagridId).datagrid('enableFilter');
        		_data = {total:data.length,rows:data,footer:[{id:'汇总'}]}
        		$(_o.datagridId).datagrid("loadData",_data);
	        }
        });
    }
    _o.main = function(option) {
        $.extend(_o, option);
        _o.start();
        return _o;
    }
    _o.start = function(){
    	__ajax();
    }

    _o.prev = null;
    _o.init_dialog = function(title, icons, height, width) {
            $(_o.registerDialogId).dialog({
                modal: true,
                title: title,
                iconCls: icons,
                height: height,
                width: width
            });
        }
        /* 保证在下一次点击按钮的时候，保存了之前的状态，这样可以提高效率*/
    _o.addCell = function(title, href, height, width) {
        _global.selected = null;
        _global.operate = "添加";
        if (_o.prev == 1) {
            $(_o.registerDialogId).dialog('open');
        } else {
            _o.init_dialog(title, 'icon-add', height, width);
            $(_o.registerDialogId).dialog({ href: href });
            $(_o.registerDialogId).dialog('open');
        }
        _o.prev = 0
    }
    _o.modifyCell = function(title, href, height, width) {
        var _data = $(_o.datagridId).datagrid('getSelected');
        if (!_data || _data.length > 1) {
            _util.msgError('请选择一行数据');
            return
        }
        if (_o.prev) {
            $(_o.registerDialogId).dialog({
                href: href + "/" + _data.id,
            });
            $(_o.registerDialogId).dialog('open');
        } else {
            _o.init_dialog(title, 'icon-edit', height, width);
            $(_o.registerDialogId).dialog({
                href: href + "/" + _data.id,
            });
            $(_o.registerDialogId).dialog('open');
        }
        _o.prev = 2;
        _global.operate = "修改";
        _global.data_id = _data.id;
        _global.selected = _util.get_datagrid_row_index(_data, _o.datagridId);
    }
    _o.refresh = function() {
        $(_o.datagridId).data("filterObj").init(null);
        _o.load_data(_o.url_load_data);
    }

    _o.search = function(url_search, height, width) {
    	$(_o.datagridId).data("filterObj").init(null);
        $(_o.registerDialogId).dialog({
            modal: true,
            title: "搜索",
            iconCls: 'icon-search',
            href: url_search,
            height: height,
            width: width
        });
        $(_o.registerDialogId).dialog("open");
    }
    return _o
}

