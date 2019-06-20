# -*- coding: UTF-8 -*-
# @Author : Song
from common.baseRequest import base_request


def get_vrf_params():
    """获取vrf请求头必须参数"""
    res = base_request(method='get', url='http://aitools.dev.jzb.com/getVrfToken')
    oj_info = res.json().get('objects')
    pinus = oj_info.get('pinus')
    x_identity_code = oj_info.get('X-Identity-Code')
    return {'pinus': pinus, 'X-Identity-Code': x_identity_code}
