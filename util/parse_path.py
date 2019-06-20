# -*- coding: UTF-8 -*-
# @Author : Song


def get_related_data_from_response(response_data, related_exp):
    """正常应该传字符串"""
    """根据表达式，从响应结果中提取响应的数据，并且赋值给指定变量"""
    # response_data不能为空或者None
    if response_data is None or response_data == "":
        return
    # ${id}=object.[0].id
    temp = related_exp.split('=')
    keys_list = temp[1].split('.')
    # 如果字段值为null需要替换为None
    if 'null' in response_data:
        response_data = response_data.replace('null', 'None')
    # data = eval(response_data)
    data = response_data
    value = get_data(data, keys_list)
    return {temp[0]: value}


def get_data(dict_obj, keys_list):
    temp_exp = ""
    for i in keys_list:
        if '[' not in i and ']' not in i:
            i = '["{}"]'.format(i)
        temp_exp += i
    return eval("{0}{1}".format(dict_obj, temp_exp))


a = {
    "errcode": 0,
    "errmsg": "",
    "objects": [{
        "subTitle": "Daily 04.10",
        "subTitle3": "换一换",
        "subTitle2": "Apr-10"}]}
str1 = '${aa}=objects.[0].subTitle2'
b = get_related_data_from_response(a, str1)
print(b)
