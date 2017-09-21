# -*- coding:utf-8 -*-
'''
@email:289012724@qq.com
@author: shuiyaoyao
@telephone:13587045516
'''
import hashlib
import time

def md5_data(data):
    md = hashlib.md5()
    md.update(data)
    return md.hexdigest()

def generate(mac,dateStr):
    data        = dateStr.split("-")
    _macs       = md5_data(mac)
    cell        = ["0"]*(len(_macs)+4+4+2+2)
    cell[0]     = _macs[0]
    cell[1]     = "S"
    cell[2]     = _macs[1]
    cell[3:7]   = data[0] #到期时间
    cell[7]     = _macs[2]
    cell[8]     = "Y"
    cell[9]     = _macs[3]
    _moths      = "%02d"%int(data[1])
    cell[10:12] = _moths  #到期时间
    cell[12:16] = _macs[4:8]
    _datas      = "%02d"%int(data[2])
    cell[16:18] = _datas  #到期时间
    cell[19]    = _macs[8]
    cell[20]    ="3"
    cell[21:30] = _macs[9:19]
    cell[30]    ="S"
    cell[31:]   = _macs[19:]
    cell[4],cell[-1] = cell[-1],cell[4]
    cell[5],cell[-3] = cell[-3],cell[5]
    cell[10],cell[-6]=cell[-6],cell[10]
    cell[16],cell[-10]= cell[-10],cell[16]
    code   = "".join(cell)
    return code

import wx
import wx.calendar

class Gen ( wx.Frame ):
    
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = "LICENCE GEN", pos = wx.DefaultPosition, size = wx.Size( 300,350 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        fgSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        self.date = wx.calendar.CalendarCtrl( self.m_panel1, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.calendar.CAL_SHOW_HOLIDAYS )
        fgSizer1.Add( self.date, 1, wx.ALL|wx.EXPAND, 5 )
        
        fgSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer3.SetFlexibleDirection( wx.BOTH )
        fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText3 = wx.StaticText( self.m_panel1, wx.ID_ANY, "MAC", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer3.Add( self.m_staticText3, 0, wx.ALL, 5 )
        
        self.mac = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(225,-1), 0 )
        fgSizer3.Add( self.mac, 1, wx.ALL, 5 )
        fgSizer1.Add( fgSizer3, 1, wx.EXPAND, 5 )
        
        self.gencode = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
        fgSizer1.Add( self.gencode, 1, wx.EXPAND, 5 )
        
        fgSizer4 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer4.SetFlexibleDirection( wx.BOTH )
        fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.okBtn = wx.Button( self.m_panel1, wx.ID_ANY, u"生成", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer4.Add( self.okBtn, 0, wx.ALL, 5 )
        
        self.clsBtn = wx.Button( self.m_panel1, wx.ID_ANY, u"关闭", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer4.Add( self.clsBtn, 0, wx.ALL, 5 )
        
        fgSizer1.Add( fgSizer4, 1, wx.ALIGN_RIGHT, 5 )
        self.m_panel1.SetSizer( fgSizer1 )
        self.m_panel1.Layout()
        fgSizer1.Fit( self.m_panel1 )
        bSizer1.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )
        
        self.SetSizer( bSizer1 )
        self.Layout()
        self.Centre( wx.BOTH )
        
        # Connect Events
        self.okBtn.Bind( wx.EVT_BUTTON, self.OnOk )
        self.clsBtn.Bind( wx.EVT_BUTTON, self.OnCls )
    
    # Virtual event handlers, overide them in your derived class
    def OnOk( self, event ):
        date=self.date.Date.Format("%Y-%m-%d")
        mac  = self.mac.GetValue()
        if date and mac:
            self.gencode.Clear()
            self.gencode.AppendText( generate(mac.upper(),date.upper()) )
        else:
            wx.MessageBox("请输入MAC和日期")
        event.Skip()
    
    def OnCls( self, event ):
        self.Close()
        event.Skip()

class App(wx.App):
    def OnInit(self):
        self.frame = Gen(None)
        self.frame.Show()
        return True

if __name__=='__main__':
    App().MainLoop()
