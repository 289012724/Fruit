/*
	@attention: 向 datagrid 中添加 excel 筛选的按钮组
	@author   : shuiyaoyao 
	@telephone: 13587045516
	@email    : 289012724@qq.com
	@license  : free
	@plateform: sublime text 3
	@notice   ; 如果你自己调用 ajax 来设置 datagrid 的数据,需在加载数据之前，调用
	$(datagrid).datagrid("initData",null); 或者在设置数据之后,调用 $(datagrid).datagrid("initData",data);
	来更新当前页面的 filterSource 数据源;
*/

(function($){
	var datagrid = null; //当全全局中的 datagrid 对象当点击在列上面点击的时候会获取这个对象
	/*
	@attention:对数据进行排序
	@param type: 排序类型,1 升序,0 降序
	@param field: the datagrid column field
	*/
	function _s(type,field){
		if(type==1){
			return function(one,two){
				_one = one[field];_two = two[field];
				if(_one < _two){code= -1}
				else if(_one==_two){code= 0}
				else{code= 1};
				return code
			}
		}else{
			return function(one,two){
				_one = one[field];_two = two[field];
				if(_one < _two){code= 1}
				else if(_one==_two){code= 0;}
				else{code=-1};
				return code;
			}
		}
	}
	var operators = {
		sortUp  :function(source,field){
			source.sort(_s(1,field));
		},
		sortDown:function(source,field){
			source.sort(_s(0,field));
		},
		nofilter:function(source,field){
			return $(datagrid).data('filterObj').filterSource.rows;
		},
		contains:function(source, value){
			return source.toLowerCase().indexOf(value.toLowerCase()) >= 0;
		},
		notcontains:function(source, value){
			return !source.toLowerCase().indexOf(value.toLowerCase()) >= 0;
		},
		equal:function(source, value){
			return source == value;
		},
		notequal:function(source, value){
			return source != value;
		},
		beginwith:function(source, value){
			return source.toLowerCase().indexOf(value.toLowerCase()) == 0;
		},
		endwith:function(source, value){
			return source.toLowerCase().indexOf(value.toLowerCase(), source.length - value.length) !== -1;
		},
		less:function(source, value){
			return source < value;
		},
		lessorequal: function(source, value){
			return source <= value;
		},
		greater:function(source, value){
			return source > value;
		},
		greaterorequal:function(source, value){
			return source >= value;
		}
	};
	/*@attention: 获取当前datagrid 的指定列
	@param target:当前的datagrid
	@param field: 列名称*/
	function _g2(target,field){
		var header = $(target).datagrid("getPanel").find("div.datagrid-header");
		var td 	   = header.find('td[field="'+field+'"]');
		var cell   = td.find('.datagrid-cell');
		return cell;
	}

	/*@attention: 执行用户选择的过滤操作，即执行自定义筛选中选择的数据操作项目 
	@param fun:   操作函数1
	@param fun1:  操作函数2*/
	function _u3(fun,fun1){
		_filter = $(datagrid).data("filterObj");
		_f   = _filter.field;
		_do  = $.extend({},_filter.filterFeildData);
		_ds  = _do.rows;
		_v   = _g1("input.excel_prompt_input").combobox("getText");
		_v1  = _g1("input.excel_prompt_input1").combobox("getText");
		_r2  = _g1("input.excel_checkbox1").attr("checked");
		var _rs = [];
		if(_v || _v1){
			for(var _1 in _ds){
				_c  = _ds[_1][_f];
				_f1 = fun ? fun(String(_c),String(_v))  : true;
				_f2 = fun1? fun1(String(_c),String(_v1)): true;
				if(_r2){
					_ok = _f1 || _f2;
				}else{
					_ok = _f1 && _f2;
				}
				if(_ok)_rs.push(_ds[_1]);
			}
		}else{
			_rs = _do;
		}
		_do.total = _rs.length;
		_do.rows  = _rs;
		_filter.filterFeildData = _do;
		return _do
	}
	/*
	@attention: 指定排序,清除筛选操作
	@param opt: 操作方法
	@notice: 以当前的数据为准*/
	function _d1(opt){
		_filter = $(datagrid).data("filterObj");
		data   = _filter.filterFeildData;
		field  = _filter.field;
		_do    = $.extend({},data);
		var fun= operators[opt];
		if (opt == 'sortUp' || opt == 'sortDown'){
			fun(_do.rows,field);
		}else{
			_do = $.extend({},_filter.filterSource);
		}
		_filter.filterFeildData = _do;
		$(datagrid).datagrid('loadData', _do);
		return _do
	}
	/*
	@attention: 构建供用户选择的数据条目
	@param data: 操作方法
	@param field: 列名称
	*/
	function _d3(data,field){
		var _filter=[];
		_total = data.rows;
		for(var cell in _total){
			var _r = _total[cell];
			if(_filter.indexOf(_r[field]) == -1){
				_filter.push(_r[field]);}
		}
		_ok = [];
		for(ids in _filter){
			_ok.push({
				id:_filter[ids],
				text:_filter[ids],
			});
		}
		return _ok;
	}
	/*
	@attention: 初始化自定义筛选对话框
	@param opt: 操作方法
	*/
	function _u2(opt){
		_filter = $(datagrid).data("filterObj").init();
		_data   = _filter.filterFeildData;
		field   = _filter.field;
		_ok     = _d3(_data,field);
		_inpnut = $(datagrid).data("filter_dialog")
				  .find("input.excel_prompt_input,input.excel_prompt_input1");
		_inpnut.combobox("clear");
		_inpnut.combobox("loadData",_ok);
		_g1("input.excel_user_opt").combobox('select',opt);
	}
	/*
	@attention: 获取自定义对话框下面的子对象
	@param selector: 过滤条件
	*/
	function _g1(selector){
		return $($(datagrid).data("filter_dialog")
							.find(selector)[0])
	}

	/*
	@attention: 创建/打开自定义对话框
	@param opt: 过滤方法
	*/
	function _u1(opt){
		_filter    = $(datagrid).data("filterObj");
		var _input = $(datagrid).datagrid("getColumnOption",
								_filter.field);
		var title  = "自定义筛选---"+_input.title+"---列";
		var _div   = $(datagrid).data("filter_dialog");
		if(_div){
			_u2(opt);_div.dialog("open");
		}else{
			_div  = _d2(datagrid);_u2(opt);
			_div.dialog({
				title:title,
				iconCls:"icon-search",
				width:500,
				height:230,
				modal:false,
				buttons:"#filter_button",
			});
			$(".excel_button").linkbutton({
				onClick:function(){
					if($(this).attr('data') == 1){
						opt  = _g1("input.excel_user_opt").combobox("getValue");
						opt2 = _g1("input.excel_user_opt1").combobox("getValue");
						if(operators[opt] || operators[opt2]){
							data = _u3(operators[opt],operators[opt2]);
							$(datagrid).datagrid('loadData',data);
						}else{
							$.messager.alert("操作无效",'提示','info');
						}
					}
					$(datagrid).data("filter_dialog").dialog("close");
				}
			});
		}
	}
	var user_opt_info = [
		{id:'contains',		text:"包含"},
		{id:'notcontains',	text:"不包含"},
		{id:'equal',		text:'等于'},
		{id:'notequal',		text:'不等于'},
		{id:'beginwith',	text:'开头是...'},
		{id:'endwith',		text:'结尾是...'},
		{id:'less',			text:'小于'},
		{id:'lessorequal',	text:'小于等于'},
		{id:'greater',		text:'大于'},
		{id:'greaterorequal',text:'大于等于'},
	]
	/*
	@attention: 创建自定义对话框
	@param target: 当前datagrid 对象
	*/
	function _d2(target){
		_div   = $('<div class="execel_prompt"></div>');
		_div.css("padding","10px 5px");
		//-------------------------------------------------------------
		_text  = $("<label>显示行:</label>");
		_text.css("padding","1px");
		_text.appendTo(_div);
		//-------------------------------------------------------------
		_type  = $('<div class="excel_prompt_opt">问题描述<br/></div>');
		_type.appendTo(_div);
		_userSelect = $("<input class='excel_user_opt'></input>");
		_userSelect.appendTo(_type);
		_input      = $("<input class='excel_prompt_input'></input>");
		_input.appendTo(_type);
		//-------------------------------------------------------------
		_type1  = $('<div class="excel_prompt_opt" style="margin-top:10px"></div>');
		_type1.appendTo(_div);
		_radio1 = $('<input type="radio" value="1" class="excel_checkbox0" >与</input>');
		_radio1.appendTo(_type1);
		_radio1.attr("checked","checked");
		_radio2 = $('<input type="radio" value="2" class="excel_checkbox1" >或</input>');
		_radio2.appendTo(_type1);
		_type1.find("input[type='radio']").attr("name","excel_and_or");
		_type1.find("input[type='radio']").css({marginLeft:"10px"});
		_type1.find("input[type='radio']").eq(0).css({marginLeft:"30px"});
		//-------------------------------------------------------------
		_type2  = $('<div class="excel_prompt_opt" style="margin-top:10px"></div>');
		_type2.appendTo(_div);
		_userSelect1 = $("<input class='excel_user_opt1'></input>");
		_userSelect1.appendTo(_type2);
		_input2      = $("<input class='excel_prompt_input1'></input>");
		_input2.appendTo(_type2);
		//-------------------------------------------------------------
		b_div = $("<div class='filter_button' id='filter_button'></div>")
		b_div.css("marginTop","-10px");
		//-------------------------------------------------------------
		bt1   = $("<a href='#' class='excel_button'  data=1>确定</a>");
		bt2   = $("<a href='#' class='excel_button'  data=0>取消</a>");
		bt1.appendTo(b_div);
		bt2.appendTo(b_div);
		// _div.data("field",target.parent().attr("field"));
		$(datagrid).data("filter_dialog",_div);
		//-------------------------------------------------------------
		b_div.appendTo("body");
		_div.appendTo("body");
		//-------------------------------------------------------------
		$(".excel_user_opt,.excel_user_opt1").combobox({
			width:130,
			panelHeight:100,
			valueField:'id',    
    		textField:'text',   
    		data :user_opt_info,
		});

		$(".excel_prompt_input,.excel_prompt_input1").combobox({
			width:300,
			panelHeight:100,
			valueField:'id',    
    		textField:'text',   
		});
		_div.find("div.excel_prompt_opt").find("span.combo").css("marginLeft","15px");
		$("a.excel_button").css({width:"65px"});
		_div.find("div.excel_prompt_opt").css({marginLeft:"10px"});
		return _div
	}
	function filter_obj(){
		var _o = new Object();
		_o.excel_menu   = null;
		_o.field 		= null;
		_o.menu_data 	= null;
		_o.field_menus  = {};
		_o.filterSource = null;
		_o.filterFeildData=null;
		_o.init_menus   =[];
		_o.main = function(options){
			$.extend(_o,options);
		}
		//when init the datagrid data,must clear inited menu information;
		_o.init = function(data){
			_o.init_menus  = [];
			if(data != null){
				_o.filterSource    = $.extend({},data);
				_o.filterFeildData = $.extend({},data);
			}else{
				_o.filterSource    = null;
				_o.filterFeildData = null;
			}
		}
		_o.clearMenu=function(){
			_o.field_menus ={};
		}
		_o.getMenu =function(field){
			return _o.field_menus[field];
		}
		_o.addMenu =function(field,menu){
			_o.field_menus[field] = menu;
		}
		_o.menu_is_init=function(field){
			return _o.init_menus.indexOf(field) >=0;
		}
		_o.add_row = function(data,index){
			if(_o.filterSource ==null)return;
			if($.isArray(data))data=data[0];
			if(_o.filterSource.rows[0].id != data.id){
				if(index == 0){
					_o.filterSource.rows.unshift(data);
					_o.filterFeildData.rows.unshift(data);
				}else if (data.length<=index){
					_o.filterSource.rows.push(data);
					_o.filterFeildData.rows.push(data);
				}else{
					_o.filterSource.rows.splice(index,0,data);
					_o.filterFeildData.rows.splice(index,0,data);
				}
			}
			_o.filterSource.total 	 = _o.filterSource.rows.length;
			_o.filterFeildData.total = _o.filterFeildData.rows.length;
		}

		_o.delete_row = function(data){
			if(_o.filterSource ==null)return;
			if($.isArray(data))data=data[0];
			id = data.id;
			_d_a = function(id,key){
				_datas = _o[key].rows;
				for(var ids in _datas){
					_one = _datas[ids];
					if(_one.id == id){
						_datas.splice(ids,1);
						_o[key].total -= 1;
					}
				}
			}
			setTimeout(_d_a(id,'filterSource'),1);
			setTimeout(_d_a(id,'filterFeildData'),1);
		}
		_o.modify_row = function(data){
			if(_o.filterSource ==null)return;
			if($.isArray(data))data=data[0];
			id = data.id;
			_m_a = function(id,key,data){
				_datas = _o[key].rows;
				for(var ids in _datas){
					if(_datas[ids].id == id){
						_datas[ids] = data;
					}
				}
			}
			setTimeout(_m_a(id,"filterSource",data),1);
			setTimeout(_m_a(id,"filterFeildData",data),1);
		}
		return _o;
	}
	
	/*@attenttion:初始化excel 筛选组件
	@param target：datagrid */
	function init(target){
		var dg    = $.data(target, 'datagrid');
		var opts  = dg.options;
		$(target).data("filterObj",filter_obj());

		var onBeforeLoad   = opts.onBeforeLoad;
		opts.onBeforeLoad  = function(param){
			$(datagrid).datagrid("filterObj").init(null);
			return onBeforeLoad.call(this,param);
		}
		
		var onLoadSuccess = opts.onLoadSuccess;
		/*当这个结合scrollView*/
		opts.onLoadSuccess = function(data){
			_filter = $(datagrid).data("filterObj");
			if(_filter.filterSource == null || _filter.filterSource.length <0 ){
				_filter.init(data);
			}
			return onLoadSuccess.call(this, data);
		}
		/*获取按钮组中树中选择的节点*/
		function _g4(_menu){
			var _s=[];
			nodes = _menu.menu('excel_tree').tree('getChecked');
			for(ids in nodes){
				_s.push(nodes[ids].id);
			}
			return _s
		}
		function _change_checked(node){
			node.checked = !node.checked;
			_check =  $(node.target).find("span.tree-checkbox");
			if(node.checked ){
				_check.removeClass("tree-checkbox0");
				_check.addClass("tree-checkbox1");
			}else{
				_check.removeClass("tree-checkbox1");
				_check.addClass("tree-checkbox0");
			}
		}
		/*向按钮组中的过滤树中添加初始化数据，数据当前 表格中的数据为准*/
		function _e1(_menu) {
			_tree = _menu.menu("excel_tree");
			_tree.tree({
				onClick:function(node){
					_change_checked(node);
				},
				onDblClick:function(node){},
			});
		}
		/*绑定menu组中的确定按钮事件*/
		function _mf1(event){
			_filter = $(datagrid).data('filterObj');
			_menu = _filter.excel_menu;
			_alert= $.messager.alert;
			if($(this).attr("_type") =="ok"){
				_selects  = _g4(_menu)
				if(_selects.length !=0){
					_field= _filter.field;
					data  = _filter.filterSource;
					_total= data.rows;
					_ok   = [];
					for(var cell in _total){
						_c = _total[cell][_field];
						if(_selects.indexOf(_c) !=-1){
							_ok.push(_total[cell]);
						}
					}
					if(_ok.length !=0){
						_data = {total: _ok.length,rows:_ok,footer:data.footer};
						$(datagrid).data("filterObj").filterFeildData = _data;
						$(datagrid).datagrid("loadData",_data);
					}else{
						_alert("提示","获取过滤数据失败,请重新加载后筛选","info");
					}
				}else{
					_alert("提示","未选中任何数据,请重新操作","error");
				}
			}
			$(_menu).menu('hide');
		}

		/*添加按钮组*/
		function _a1(target,menu){
			var _labels = [{text: '升序',
							iconCls: 'sys-sort-up',
							onclick: function(){_d1("sortUp")}},
						   {text: '降序',
						   iconCls:'sys-sort-down',
						   onclick: function(){_d1("sortDown")}},
						   {text:'清除筛选',
							onclick:function(e){
								tree = $($(e.target).parent()).menu('excel_tree');
								nodes = tree.tree('getChecked');
								for(ids in nodes){
									_change_checked(nodes[ids]);
								}
								_d1('nofilter');
							}}
						  ];
			for (ids in _labels){menu.menu('appendItem',_labels[ids])}
			menu.menu('appendItem',{'text':'文本筛选'});
			var parent = menu.menu('findItem', '文本筛选');
			var _labels=[{text:'包含',
						 onclick:function(){_u1('contains')}},
						 {text:'不包含',
						 onclick:function(){_u1('notcontains')}},
						 {text:'等于',
						 onclick:function(){_u1('equal')}},
						 {text:'不等于',
						 onclick:function(){_u1('notequal')}},
						 {text:'开头是...',
						 onclick:function(){_u1('beginwith')}},
						 {text:'结尾是...',
						 onclick:function(){_u1('endwith')}},
						 {text:'自定义筛选',
						 onclick:function(){_u1('less')}}];

			for(ids in _labels){
				cell = _labels[ids];
				cell.parent = parent.target;
				menu.menu('appendItem',cell);
			}
			if(menu.menu("findItem",'__excel__filter')){
				alert("已经存在为 __excel__filter的按钮,请核实");
			}else{
				menu.menu('appendItem',{_type:'excel',text:'__excel__filter'});
			}
		}
		
		function _m1(target){
			var menu = $('<div></div>');
			menu.appendTo('body');
			menu.menu({alignTo:target,'align':'right'});
			return menu;
		}
		
		function _af1(target){
			var menu  = _m1(target);
			_a1(target,menu);
			return menu;
		}
		/*在列上面绑定鼠标左键点击事件*/
		function _bdm(e){
			datagrid= ("#"+e.data["datagrid"][0].options.id);
			_parent = $(this).find('.datagrid-cell')[0];
			_field  = $(this).attr('field');
			_filter = $(datagrid).data("filterObj");
			var menu= _filter.getMenu(_field);
			if(!menu){
				menu   = _af1($(_parent));
				_filter.addMenu(_field,menu);
				menu.find(".excel-menu-btn").bind('click',{'menu':menu},_mf1);
				_e1(menu);
			}
			var _totalData = _filter.filterSource;
			if(! _filter.menu_is_init(_field)){
				if(_totalData.rows.length >0){
					menu.menu("init_excel_tree",_d3(_totalData,_field));
					_filter.init_menus.push(_field);
				}
			}
			//保存当前执行的 字段和菜单项
			_filter.field      = _field;
			_filter.excel_menu = menu;
			menu.menu("show");
		}
		
		/*向列中添加过滤图标*/
		function _bdi(target,fields){
			function _ico(target){
				var _span = $("<span>　</span>");
				_span.addClass("datagrid-filter");
				_span.addClass("icon-filter");
				_span.css("float","right");
				_span.appendTo(target);
			}
			cells = $(target).datagrid("getPanel")
						     .find("div.datagrid-header")
						     .find('td[field] .datagrid-cell')
			cells.find("span.datagrid-filter.icon-filter").remove();
			cells.each(function(){
				col = $(this);
				if (!(col && (col.checkbox || col.expander))){
					_ico(col);
				}
			});
		}
		/*
		 * 创建过滤组件
		 */
		function _c1(frozen){
			var dc     = dg.dc;
			var fields = $(target).datagrid('getColumnFields', frozen);
			if (opts.rownumbers){fields.unshift('_');}
			_bdi(target,fields);
			dc.header2.find("td[field]").bind('click',{datagrid:$(dg)},_bdm);
		};
		_c1(); //开始创建组件
	}	
	
	$.extend($.fn.datagrid.methods, {
		enableFilter: function(jq){
			datagrid = jq;
			return jq.each(function(){init(this);});
		},
		removeFilter:function(jq){
			datagrid = jq;_d1('nofilter'); 
		},
		initData:function(jq,data){
			$(jq).data("filterObj").init(data);
		},
		filterObj:function(jq){
			return $(jq).data("filterObj");
		}
	});
})(jQuery);

/*
	创建excel 按钮组,当传入的数据的 _type 为 excel 的时候将在后面天内excel 按钮组合 
*/
(function($) {
    var _r1 = function(jq) {
    	jq 	= $(jq);
        jq.find("div.menu-line").height(jq.height());
    }
    /*调整树节点中的样式,删除默认的file 和folder 图标*/
    var _cs1 = function(tree){
		tree.find("span.tree-icon").each(function(){
        		$(this).removeClass('tree-file');
        		$(this).removeClass('tree-folder');
        	});
    	tree.hover(function (argument) {
    		$(this).find("li").css({background:'white',color:'black'});
    	});
	}

    /*绑定按钮组中,输入框的回车的事件*/
    var _e1 = function(e){
    	if(e.keyCode !=13)return true;
		var menu = $(e.target).parent().parent().parent();
		var _tree= menu.menu("excel_tree");
		_do      = _tree.data("tree_data");
		_input   = _gp1(menu);
		value    = $(_input).val();
		_ds   	 = [];
		if(value){
			for(ids in _do){
				_c = _do[ids];
				_t = _c.text;
				if(String(_t).toLowerCase().indexOf(value.toLowerCase()) >= 0){
					_ds.push(_c);
				} 
			}
		}else{_ds = _do}
		_tree.tree({
			data:[{id:-1,text:"全选",children:_ds}]
		});
		_cs1(_tree);
    }
    /*添加确定和取消按钮*/
    var _b = function(parent){
        var _bt1 = $("<button href='#' class='excel-menu-btn ' _type ='ok' >确定</button>");
        var _bt2 = $("<button href='#' class='excel-menu-btn ' _type ='cls'>取消</button>");
        var _jq  = parent.parent().parent();
        _bt2.bind("click", function() { _jq.menu('hide')});
        _bt2.appendTo(parent);
        _bt1.appendTo(parent);
        $(".excel-menu-btn").linkbutton({height:'25px'});
        $(".excel-menu-btn").css({marginLeft:10,width:"65px",marginTop:6,float:"right"});
    }
    /*获取树对象*/
    var _tr1 = function(jq){
        tree = jq.menu('excel').find("div.excel-menu .excel-menu-tree");
        return tree;
    }
	
	/*初始化树节点中的数据	*/
    var InitPanel = function (jq,data){
        jq.find("ul.excel-menu-tree").each(function(){
			$(this).tree({
				lines:true,
    		 	data:[{id:-1,text:"全选",children:data}]
    		});
			_cs1($(this));
        	$(this).data('tree_data',data);
      	});
    }
	
	/*添加树节点*/
    var _p = function(parent,data){
        var _panel  = $("<ul class='excel-menu-tree' style='overflow: auto;'></ul>");
        _panel.appendTo(parent);
        _panel.css({
        	marginTop:'5px',
            width : parent.width(),
            height: parent.height() - 20 - 15,
            border:"1px solid gray",
        });
        _panel.tree({
        	checkbox:true,
    		fit:true,
        });
        
    }
    /*获取输入框对象*/
    var _gp1=function(jq){
		return $(jq).find("input.excel-menu-input");
    }
    /*添加输入框对象*/
    var _p1 = function(parent){
        _input = $("<input class='excel-menu-input' placeholder='搜索(按回车确认)' style='width:100%'></input>");
        _input.appendTo(parent);
        _input.css('height',20);
        _input.bind("keypress",function(event){
			_e1(event)
        });
        return _input;
    }
	/*添加按钮组对象*/
    var _d = function(parent){
        var _divs = $("<div class='excel-menu' style='margin-left:30'></div>");
        _divs.width(parent.width() - 40);
        _divs.height(parent.height - 15);
        _divs.appendTo(parent);
        return _divs;
    }
    /*初始 excel 按钮*/
    var _ef = function(menu,data) {
    	menu= $(menu);
    	_opt= menu.menu("options");
        _ht = data.height || _opt.excelMenuTreeHeight;
        menu.css("width",menu.width()+_opt.excelMenuWidth);
        _excel= menu.menu("findItem","__excel__filter");
        _excel= $(_excel.target);
        _excel.find('div.menu-text').remove();
        _excel.removeClass('menu-item');
        _excel.addClass("excel-menu-row");
        _excel.css({height:_ht,width:menu.width()});
        _excel.unbind(".menu");
        //-------------------------------------------
        _divs = _d(_excel); _divs.height(_ht);
		//-------------------------------------------
        _input= _p1(_divs);_panel= _p(_divs);
        //-------------------------------------------
        _b(_divs);
        _divs.css({position:'relative',left:30});
        menu.css('height',_ht+_opt.excelMenuTreeHeight-40);
    }
	
    var oldAppendItem = $.fn.menu.methods.appendItem;
    $.fn.menu.methods.appendItem = function(menu, data) {
        menu.each(function() {
            oldAppendItem.call($.fn.datagrid.methods, menu, data);
            if (data._type && data._type == 'excel') _ef(menu,data); _r1(this);
        });
    }
	$.extend($.fn.menu.defaults,{
		excelMenuWidth:100,
		excelMenuTreeHeight:160,
	});
    $.extend($.fn.menu.methods,{
        excel:function(menu) {
            return $(menu).find("div.excel-menu-row");
        },
        excel_tree:function(menu){
            return _tr1(menu);
        },
        init_excel_tree:function(menu,data){
        	InitPanel(menu,data);
        }
    });
})(jQuery);
