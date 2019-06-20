# -*- coding: UTF-8 -*-
# @Author : Song
from common.baseRequest import base_request
import collections
import hashlib
import time
import json


class TestEnvir:
    TEST = 0  # 测试线
    ONLINE = 1  # 线上


class BaseLogin:
    """
    获取头信息必要参数
    仿真：u:'大热天的' p:'jzb111111'
    线上：u:'JZB150' p:'g9a6y5e4'
    """

    def __init__(self, username=None, passwd=None, test_envir=1):
        self.username = username
        self.passwd = passwd
        self.test_envir = test_envir

    @property
    def __sign(self):
        if self.test_envir == 0:
            self.username = '大热天的'
            self.passwd = 'jzb111111'
        elif self.test_envir == 1:
            self.username = 'JZB150'
            self.passwd = 'g9a6y5e4'
        else:
            pass

        app_secret = '5b7cc94c284f4dad745e343d7d66faee'  # 秘钥(不能泄露)
        param = collections.OrderedDict()
        param['passwd'] = self.passwd
        param['uname'] = self.username
        param['version'] = '7.3'
        str_param = json.dumps(param, ensure_ascii=False)  # 防止中文乱码
        day = time.strftime('%Y%m%d')
        sign = app_secret + day + str_param
        sign = sign.replace(" ", "")
        m = hashlib.md5()
        m.update(sign.encode('utf-8'))
        sign = m.hexdigest()
        param['sign'] = sign
        return param

    @property
    def api_key(self):
        param = self.__sign
        if self.test_envir == 0:
            res = base_request(method='post', url="http://m-dev.jzb.com/user/login/v2016", body_data=param)
        elif self.test_envir == 1:
            res = base_request(method='post', url="http://m.jzb.com/user/login/v2016", body_data=param)
        else:
            res = None
        try:
            auth = res.json().get('res').get('api_key')
            return auth
        except:
            print('测试环境选择错误！环境选择举例：test_envir=TestEnvir.TEST')

    def login_new(self):
        """750+版本登录"""
        if self.test_envir == 1:
            url = 'https://passport.jzb.com/login?v=7.55&ver=7.55&channel=website&deviceId=ffffffff-c7a8-b0f1-0000-0000265bc76d&deviceType=MIX_2&deviceVersion=8.0.0'
            data = {'uname': 'JZB150', 'passwd': 'g9a6y5e4'}
            res = base_request(method='post', url=url, body_data=data)
            return res
        else:
            pass

    @property
    def token(self):
        res = self.login_new()
        if res:
            api_key = res.json().get('objects').get('api_key')
        else:
            api_key = None
        return api_key
