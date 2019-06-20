# -*- coding: UTF-8 -*-
# @Author : Song
import requests
import urllib3


def base_request(method, url, body_type=None, body_data=None, headers=None, timeout=10):
    """
    requests基类
    :param method: 请求方法get/post
    :param url: 请求url
    :param body_type: 请求头类型(枚举)，举例：body_type=BodyType.JSON
    :param body_data: 需要传字典格式的请求体
    :param headers: 需要传字典格式的请求头
    :param timeout: 请求超时时间
    :return: response对象
    """
    urllib3.disable_warnings()

    if headers is None:
        headers = {}
    try:
        if method.upper() == 'GET':
            res = requests.get(url=url, params=body_data, headers=headers, verify=False, timeout=timeout)
        elif method.upper() == 'POST' and body_type == 'URL_ENCODE':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            res = requests.post(url=url, data=body_data, headers=headers, verify=False, timeout=timeout)
        elif method.upper() == 'POST' and body_type == 'JSON':
            headers['Content-Type'] = 'application/json'
            res = requests.post(url=url, json=body_data, headers=headers, verify=False, timeout=timeout)
        elif method.upper() == 'POST' and body_type == 'MULTIPART':
            res = requests.post(url=url, data=body_data, headers=headers, verify=False, timeout=timeout)
        else:
            res = None
    except AttributeError:
        raise AttributeError
    else:
        return res


class BodyType:
    """请求体类型"""
    URL_ENCODE = 'URL_ENCODE'
    FORM = 'FORM'
    JSON = 'JSON'
    FILE = 'MULTIPART'
