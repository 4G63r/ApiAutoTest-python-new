# -*- coding: UTF-8 -*-
# @Author : Song
from common.baseRequest import base_request, BodyType
from util.cityWeather import CityWeather
from util.readConfUtil import ReadConf

cw = CityWeather().weather_info
rc = ReadConf()
access_tokens = rc.get_value_list()


def push_text(res_msg, access_token, send_all=False):
    """
    钉钉推送
    :param res_msg: list()
    :param access_token: list()
    :param send_all: 是否群发
    :return:
    """
    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % access_token
    # content_with_img = '# 构建失败\n![screenshot](https://ss2.bdstatic.com/70cFvnSh_Q1YnxGkpoWK1HF6hhy/it/u=2934092001,3164812011&fm=26&gp=0.jpg)\n\n' \
    #                    '>#### 失败原因：%s\n\n>%s' % (result, cw)
    # data_with_img = {
    #     "msgtype": "markdown",
    #     "markdown": {"title": "后端业务监控",
    #                  "text": content_with_img
    #                  },
    #     "at": {
    #         "atMobiles": [
    #             "134xxxxxxxx"
    #         ],
    #         "isAtAll": False
    #     }
    # }
    temp = ""
    for i in range(len(res_msg)):
        if i == 0:
            temp += '%s\n' % res_msg[i]
            continue
        temp += '-->%s\n\n' % res_msg[i]

    content = temp + cw
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        },
        "at": {
            "atMobiles": [
                ""
            ],
            "isAtAll": send_all
        }
    }
    base_request(method='post', url=url, body_data=data, body_type=BodyType.JSON)


def push_to_dingtalk(res_msg):
    for access_token in access_tokens:
        push_text(res_msg, access_token)
