/**
 * Created by Administrator on 2016/7/7 0007.
 */
$(function() {
	
	function load_data(title, url) {
		is_creat_tabs = false;
		$('#panel_control').panel({
			fit : true,
			title : ">>" + title,
			border : false,
			href : url,
			onLoadError : function(error) {
				alert('加载数据出错');
				console.log(error);
			}
		});
	}
	function load_data_grid(obj, url) {
		var title = obj.text();
		var index = obj.attr('data-url');
		var url = url.format(index);
		load_data(title, url);
	}
	var is_creat_tabs = false;
	function load_data_tabs(title, url) {
		if (!is_creat_tabs) {
			$("#center").empty();
			$("#center").append("<div id='panel_control'></div>");
			$('#panel_control').tabs({
				border : false,
				fit:true,
				onSelect : function(title) {
					console.log(title + ' is selected');
				}
			});
			is_creat_tabs = true;
		}
		var _exist = $('#panel_control').tabs("exists", title);
		if(_exist){
			$('#panel_control').tabs('select', title);
		}else{
			$('#panel_control').tabs('add', {
				title : title,
				href : url,
				closable : true,
				fit : true,
				border : false,
				iconCls : "sys-excel",
			});
		}
	}
	function load_data_grid_tabs(obj, url) {
		var title = obj.text();
		var index = obj.attr('data-url');
		var url = url.format(index);
		load_data_tabs(title, url);
	}
	$('.user_control').click(function() {
		var url = "User/load_datagrid/{0}";
		load_data_grid($(this), url);
	});

	$(".production_control").click(function() {
		var url = "Production/load_datagrid/{0}";
		load_data_grid_tabs($(this), url);
	});
	$(".finance_control").click(function() {
		var url = "Finance/load_datagrid/{0}";
		load_data_grid_tabs($(this), url);
	});

	$(".bom_control").click(function() {
		var url = "Bom/load_datagrid/{0}";
		load_data_grid_tabs($(this), url);
	});
	$(".bill_control").click(function() {
		var url = "Bill/load_datagrid/{0}";
		load_data_grid_tabs($(this), url);
	});
	$(".bill_manager").click(function() {
		var url = "Bill/bill_manager";
		load_data_grid_tabs($(this), url);
	});

});