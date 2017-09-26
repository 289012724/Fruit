# -*- coding:utf-8 -*-
'''
@email:289012724@qq.com
@author: shuiyaoyao
@telephone:13587045516
'''
import os
import uuid
import time
import hashlib


def md5_data(data):
    md = hashlib.md5()
    md.update(data)
    return md.hexdigest()


basedir = "c:/Fruits"


def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    return '%s:%s:%s:%s:%s:%s' % (mac[0:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:])


def get_md5_mac(): return md5_data(get_mac_address())


def reverseCode(code):
    cell = list(code)
    cell[4], cell[-1] = cell[-1], cell[4]
    cell[5], cell[-3] = cell[-3], cell[5]
    cell[10], cell[-6] = cell[-6], cell[10]
    cell[16], cell[-10] = cell[-10], cell[16]
    code = "".join(cell)
    return code


def GetLincece(basedir):
    _file = os.path.join(basedir, "license.lic")
    _fp = open(_file)
    _lines = _fp.readlines()
    _fp.close()
    _keyIndex = [1, 8, 20, 30]
    _code = ""
    _start = False
    for line in _lines:
        if not line.startswith("#"):
            if line.startswith("START"):
                _start = True
                continue
            if line.startswith("END"):
                break
            if _start: _code += line.strip()

    _code = reverseCode(_code)
    _mac = get_md5_mac()
    return True, ""
    # if _mac == get_md5_mac():
    #     return check_date(_code)
    # return False,u"主机地址不正确,请联系管理员"


def get_code_md5(_code):
    _macs = []
    cell = list(_code)
    _macs.append(cell[2])
    _macs.append(cell[7])
    _macs.append(cell[9])
    _macs.extend(cell[12:16])
    _macs.append(cell[19])
    _macs.extend(cell[21:30])
    _macs.extend(cell[31:])
    return "".join(_macs)


def check_date(_code):
    _year = [3, 7]
    _moth = [10, 12]
    _data = [16, 18]
    _years = _code[_year[0]:_year[1]]
    _moths = _code[_moth[0]:_moth[1]]
    _datas = _code[_data[0]:_data[1]]
    timeStr = "%s-%s-%s" % (_years, _moths, _datas)
    stamp = time.mktime(time.strptime(timeStr, "%Y-%m-%d"))
    _local = time.mktime(time.localtime())
    _str = ""
    if stamp >= _local:
        if (stamp - _local) < 1 * 3600 * 24:
            _data = (stamp - _local) / 3600
            _str = u"License%d小时后,将过期,请更换License" % int(_data)
        return True, _str
    return False, u"软件已经到期"


print get_mac_address()
