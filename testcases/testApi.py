# -*- coding: UTF-8 -*-
# @Author : Song
from conf import filePath
from util.readConfUtil import ReadConf
from util.operaExcel import OperaExcel
from common.baseRequest import base_request
from util.loggerUtil import LoggerUtil
from util import dingTalk
from common import baseHeader
from util.compExpUtil import CompExpUtil
from util.imgUpload import ImgUpload
import unittest
import ddt
import re

rc = ReadConf()
auth = rc.get_ini_value('token', 'auth')
switch_mode = rc.get_ini_value('dingtalk', 'switch_mode')  # 钉钉通知状态
case_sheet = rc.get_ini_value('testcase', 'testcase_sheet')
logger = LoggerUtil()
oe = OperaExcel(filePath.testdata_abspath, case_sheet, logger)
all_case_data = oe.all_case_datas
valid_cases = []  # 有效case
for case in all_case_data:
    if case.get('is_run') == 1:
        valid_cases.append(case)
case_title = oe.case_title  # case标题
error_list = []  # 失败case
GLOBAL_VARS = {}


@ddt.ddt
class TestApi(unittest.TestCase):
    # TestCase.maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.base_header = baseHeader.base_headers()
        # 默认header参数
        header = {
            'Authorization': auth}
        cls.base_header.update(header)

    @classmethod
    def tearDownClass(cls):
        oe.update_init_data()
        oe.save_excel(filePath.testdata_abspath)

        total_case_num = len(valid_cases)
        failed_num = len(error_list)
        passed_num = total_case_num - failed_num
        msg = '项目名称：%s\n测试结果：共< %d >条测试用例，通过< %d >条，失败< %d >条\n概况如下：' % (
            case_title, total_case_num, passed_num, failed_num)
        error_list.insert(0, msg)
        if switch_mode == 'on' and len(error_list) > 1:
            dingTalk.push_to_dingtalk(error_list)

    @ddt.data(*valid_cases)
    def test_api(self, case_data):
        global GLOBAL_VARS
        case_id = case_data['case_id']
        url = case_data['url']
        method = case_data['method']
        body_type = case_data['body_type']
        self.base_header.update(case_data['headers'])  # 动态更新headers
        body_data = case_data['body_data']
        logger.info("============== 开始执行第%d条接口测试用例，请求数据如下 ===============" % case_id)
        logger.info("请求地址：{}".format(url))
        logger.info("请求类型：{}".format(method))

        expected_res = case_data['expected_res']  # 单个期望结果
        expected_res_list = oe.get_expected_result_list(expected_res)  # 多个期望结果
        compare_exp = case_data['compare_exp']
        is_related = case_data['is_related']
        if GLOBAL_VARS and is_related == 1:  # is_related=1：需要替换依赖字段
            temp_url = []
            temp_body_data = []
            temp_expected_res = []
            temp_compare_exp = []
            for key, value in GLOBAL_VARS.items():
                if key in url:
                    url = re.sub(key, value, url)  # 动态替换url中的依赖数据
                    temp_url.append(1)
                if key in str(body_data):
                    body_data = eval(re.sub(key, value, str(body_data)))  # 动态替换body_data中的依赖数据
                    temp_body_data.append(1)
                if key in str(expected_res):
                    expected_res = re.sub(key, value, expected_res)  # 动态替换expected_res中的依赖数据
                    expected_res_list = oe.get_expected_result_list(expected_res)
                    temp_expected_res.append(1)
                if compare_exp:
                    if key in str(compare_exp):
                        compare_exp = re.sub(key, value, compare_exp)
                        temp_compare_exp.append(1)
            if len(temp_url) > 0:
                logger.info("url动态更新为{}".format(url))
            if len(temp_body_data) > 0:
                logger.info("请求体动态更新为{}".format(body_data))
            if len(temp_expected_res) > 0:
                logger.info("期望结果动态更新为{}".format(expected_res_list))
            if len(temp_compare_exp) > 0:
                logger.info("匹配表达式动态更新为{}".format([i for i in compare_exp.split('\n')]))
        # 发起请求
        if body_type == 'MULTIPART':
            iu = ImgUpload(method=method, url=url, body_type=body_type, headers=self.base_header, logger=logger)
            res = iu.upload_data
        else:
            logger.info("请求头信息：")
            logger.info("{}".format(self.base_header))
            logger.info("请求体类型：{}".format(body_type))
            if not body_data:
                msg = "空"
            else:
                msg = body_data
            logger.info("请求体内容：{}".format(msg))
            res = base_request(method=method, url=url, body_type=body_type, body_data=body_data,
                               headers=self.base_header)
        res_text = res.text
        if r'\u' in res.text:  # str存在unicode，将unicode转成中文
            try:
                res_text = res.text.encode('utf-8').decode('unicode_escape')
            except UnicodeEncodeError:
                res_text = res.text
        res_text = r'%s' % res_text  # 响应文本
        # 响应结果中有空白的(包括" ",\n,\r,\t)替换为空字符，有null的替换为None
        if res_text:
            if 'null' in res_text:
                res_text = res_text.replace('null', 'None')
            res_r = re.findall(r'\s', res_text)
            if res_r:
                res_text = re.sub(r'\s', '', res_text)

        res_status_code = res.status_code  # 响应状态码
        res_elapsed_time = round(res.elapsed.total_seconds() * 1000)  # 响应时长(毫秒)
        logger.info("本次请求的响应状态码：{}".format(res_status_code))
        logger.info("本次请求的响应时长：{}毫秒".format(res_elapsed_time))
        logger.info("本次请求的响应结果：")
        logger.info(res_text)
        # 先要判断返回数据中是否有关联字段，如果有，则需要按表达式提取出来并赋值给全局变量
        related_exp = case_data['related_exp']
        if 'related_exp' in case_data.keys() and related_exp:
            temp = case_data['related_exp'].split('=')
            r = re.findall(temp[1], res_text)
            if r:
                logger.info("从响应结果中提取依赖数据：{}".format(r[0]))
            else:
                logger.info("请检查表达式格式是否正确")
            GLOBAL_VARS[temp[0]] = r[0]
            logger.info("global_vars动态更新为：{}".format(GLOBAL_VARS))

        # 检查点校验
        compare_type = case_data['compare_type']  # 匹配类型，0，1，2
        logger.info("本次请求的期望结果与实际结果比对方式为：")
        if compare_type == 0:
            logger.info("->全值匹配模式")
            try:
                self.assertEqual(expected_res, res_text)
                oe.write_in_result(case_id + 2, 'PASS')
                logger.info(Msg.PASS)
            except AssertionError as e:
                error_msg = Msg.DEFAULT(case_id, case_data['html_case_name'], e)
                error_list.append(error_msg)
                oe.write_in_result(case_id + 2, 'FAIL')
                logger.exception(Msg.FAIL)
                raise AssertionError
        elif compare_type == 1:
            logger.info("->正则匹配模式")
            logger.info("本次请求的期望结果：{}".format(expected_res_list))
            ce = CompExpUtil(compare_exp, res, res_text, logger)
            ce_dict = ce.data_dict
            logger.info("本次请求的实际结果：")
            logger.info("{}".format(ce_dict))
            m = 1
            msg = ''
            try:
                for exp_res, key_val in zip(expected_res_list, ce_dict.items()):
                    logger.info("----开始比对第%d个检查点%s和%s----" % (m, exp_res, str(key_val[1])))
                    if key_val[0] == 'status_code':
                        msg = Msg.STATUS_CODE(exp_res, key_val[1])
                    elif 'isNone->' in key_val[0]:
                        msg = Msg.IS_NONE(exp_res, key_val[1])
                    elif 'greater->' in key_val[0]:
                        msg = Msg.GREATER(key_val[1], exp_res)
                        self.assertGreater(int(key_val[1]), int(exp_res), msg=msg)
                        m += 1
                        continue
                    elif 'less->' in key_val[0]:
                        msg = Msg.LESS(key_val[1], exp_res)
                        self.assertLess(int(key_val[1]), int(exp_res), msg=msg)
                        m += 1
                        continue
                    elif 'len->' in key_val[0]:
                        msg = Msg.LEN(exp_res, key_val[1])
                    else:
                        msg = Msg.EXP_COMPARE(exp_res, key_val[1])
                    self.assertEqual(exp_res, str(key_val[1]), msg=msg)
                    m += 1
                oe.write_in_result(case_id + 2, 'PASS')
                logger.info(Msg.PASS)
            except AssertionError:
                error_msg = Msg.ASSERT_ERROR(case_id, case_data['html_case_name'], m, msg)
                error_list.append(error_msg)
                oe.write_in_result(case_id + 2, 'FAIL')
                logger.exception(Msg.FAIL)
                raise AssertionError
        elif compare_type == 2:
            logger.info("->响应结果为列表串进行长度校验")
            logger.info("接口请求的期望结果是：{}".format(expected_res))
            try:
                list_len = len(eval(res_text))
                logger.info("响应结果实际长度为%d" % list_len)
                self.assertEqual(expected_res, list_len)

                oe.write_in_result(case_id + 2, 'PASS')
                logger.info(Msg.PASS)
            except AssertionError as e:
                error_msg = Msg.DEFAULT(case_id, case_data['html_case_name'], e)
                error_list.append(error_msg)
                oe.write_in_result(case_id + 2, 'FAIL')
                logger.exception(Msg.FAIL)
                raise AssertionError
        else:
            pass
        logger.info("====================== 结束第%d条接口测试用例 =======================" % case_id)


class Msg:
    STATUS_CODE = lambda a, b: "响应状态码检查失败，期望结果{0}，实际结果{1}".format(a, b)
    IS_NONE = lambda a, b: "字段值为空检查失败，期望结果{0}，实际结果{1}".format(a, b)
    GREATER = lambda a, b: "字段值大于期望结果检查失败，实际结果{0}，期望结果{1}".format(a, b)
    LESS = lambda a, b: "字段值小于期望结果检查失败，实际结果{0}，期望结果{1}".format(a, b)
    LEN = lambda a, b: "字段长度检查失败，期望结果{0}，实际结果{1}".format(a, b)
    EXP_COMPARE = lambda a, b: "字段值检查正则匹配失败，期望结果{0}，实际结果{1}".format(a, b)
    ASSERT_ERROR = lambda a, b, c, d: "第 {0} 条用例<{1}>\n第 {2} 个检查点测试失败，失败原因：{3}".format(a, b, c, d)
    DEFAULT = lambda a, b, c: "第 {0} 条用例<{1}>测试失败，\n失败原因：{2}".format(a, b, c)
    FAIL = "结果比对失败！"
    PASS = "结果比对成功，测试通过"


if __name__ == '__main__':
    unittest.main()
