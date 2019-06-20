# -*- coding: UTF-8 -*-
# @Author : Song
from util import getVrfParams
from common.baseLogin import BaseLogin

base_login = BaseLogin()
token = base_login.token


def base_headers():
    """
    请求头必须参数
    :return: {'Authorization':x, 'pinus':y, 'X-Identity-Code':z}
    """

    headers = dict()
    headers['Authorization'] = token
    vrf_params = getVrfParams.get_vrf_params()
    headers.update(vrf_params)
    return headers
