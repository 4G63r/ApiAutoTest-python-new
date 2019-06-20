# -*- coding: UTF-8 -*-
# @Author : Song
import re


class CompExpUtil:
    """正则表达式匹配"""

    def __init__(self, compare_exp, res, res_text, logger):
        self.res = res
        self.res_text = res_text
        self.compare_exp = compare_exp
        self.logger = logger
        self.exp_list = self.get_compare_exps()
        self.data_dict = self.get_data_by_exp()

    def get_data_by_exp(self):
        """根据表达式，从响应结果中提取数据"""
        data_dict = {}
        if self.exp_list:
            mark = 1
            for _pattern in self.exp_list:
                # 检查响应状态码
                if _pattern == 'code':
                    data_dict["status_code"] = self.res.status_code
                elif '<->' in _pattern:
                    patt1 = _pattern.split('<->')[0]
                    patt2 = _pattern.split('<->')[1]
                    m_len = re.findall(r'{}'.format(patt1), self.res_text)
                    m_val = re.findall(r'{}'.format(patt2), self.res_text)
                    if m_len and m_val:
                        try:
                            r = len(eval(m_len[0]))
                            if r == int(m_val[0]):
                                self.logger.info("列表长度检查匹配到值：{0}和{1}".format(r, int(m_val[0])))
                                m = True
                            else:
                                m = False
                        except TypeError as e:
                            self.logger.info("请检查表达式书写格式是否正确，正确格式为<->左边为长度表达式，右边为字段表达式")
                            self.logger.exception(e)
                            m = None
                        data_dict[_pattern] = m
                    else:
                        self.logger.info("列表长度检查没有匹配到内容，请检查表达式书写是否正确")
                elif '->' in _pattern:
                    tag = _pattern.split('->')[0]
                    patt = _pattern.split('->')[1]
                    # 检查字段值是否为空
                    if tag == 'isNone':
                        m = self.is_param_null(patt)
                        data_dict[_pattern] = m
                    # 检查列表长度
                    elif tag == 'len':
                        r = re.findall(r'{}'.format(patt), self.res_text)
                        if r:
                            m = len(r)
                            self.logger.info("列表长度检查匹配到值：{0}".format(m))
                            data_dict[_pattern] = m
                        else:
                            self.logger.info("列表长度检查没有匹配到内容，请检查表达式格式是否正确")
                    # 检查实际结果是否大于/小于预期结果
                    elif tag == 'greater' or tag == 'less':
                        m = re.findall(r'{}'.format(patt), self.res_text)
                        if m:
                            data_dict[_pattern] = m[0]
                        else:
                            self.logger.info("正则表达式没有匹配到内容，请检查表达式格式是否正确")
                    else:
                        # 响应内部字段值检查
                        r1 = re.search(r'{}'.format(tag), self.res_text)
                        self.logger.info("响应内部字段值1匹配：{0}".format(r1.group(1)))
                        r2 = re.search(r'{}'.format(patt), self.res_text)
                        self.logger.info("响应内部字段值2匹配：{0}".format(r2.group(1)))
                        if r1.group(1) == r2.group(1):
                            m = True
                        else:
                            self.logger.info("内部字段值校验不相等")
                            m = False
                        s = 'reg_vs_reg%s' % str(mark)
                        data_dict[s] = m
                        mark += 1
                elif '$' in _pattern:
                    patt = _pattern.split('$')[0]
                    index = _pattern.split('$')[1]
                    index = int(index) if index else 1
                    m = re.findall(r'{}'.format(patt), self.res_text)
                    if m:
                        m = m[index - 1]
                        data_dict[patt] = m
                    else:
                        self.logger.info("$正则表达式没有匹配到内容，请检查表达式格式是否正确")
                else:
                    if _pattern in self.res_text:
                        self.logger.info("单个字段检查匹配到值：{0}".format(_pattern))
                        m = True
                    else:
                        self.logger.info("单个字段检查没有匹配到内容，请检查表达式书写是否正确")
                        m = False
                    data_dict[_pattern] = m
                # self.data_list.append(data_dict)
        return data_dict

    def get_compare_exps(self):
        exp_list = []
        if self.compare_exp:
            if '\n' in self.compare_exp:
                for i in self.compare_exp.split('\n'):
                    exp_list.append(i.strip())
            else:
                exp_list.append(self.compare_exp)
        else:
            e = '请添加匹配表达式'
            raise e
        return exp_list

    def is_param_null(self, param):
        """
        字段为空判断
        :return
        False: 字段值不为空
        True: 字段值为空
        """
        s1 = '"{}":""'.format(param)
        s2 = '"{}":None'.format(param)
        s3 = r'"{}":\[]'.format(param)

        r = re.findall(param, self.res_text)
        if r:
            for _ in r:
                m = re.search('{0}|{1}|{2}'.format(s1, s2, s3), self.res_text)
                if m:
                    self.logger.info("字段值判空匹配到空值：{}".format(m.group()))
                    flag = True
                else:
                    self.logger.info("字段值{}判空没有匹配到空值".format(param))
                    flag = False
                return flag
        else:
            self.logger.info("响应体中未找到字段名，请检查表达式书写是否正确")
            return
