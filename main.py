# -*- coding: UTF-8 -*-
# @Author : Song
import unittest
from common import HTMLTestReportCN
from testcases import testApi
from conf import filePath

suite = unittest.defaultTestLoader.discover(filePath.testcase_dir, 'test*.py')

with open(filePath.report_abspath, 'wb') as f:
    runner = HTMLTestReportCN.HTMLTestRunner(
        stream=f,
        title='接口测试报告',
        description='{case_title}'.format(case_title=testApi.case_title),
        tester='QA'
    )
    res = runner.run(suite)
    assert res.failure_count == 0
