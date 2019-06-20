# -*- coding: UTF-8 -*-
# @Author : Song
import os
import time
from util.readConfUtil import ReadConf

rc = ReadConf()

cur_dir = os.path.dirname(__file__)
cur_time = time.strftime('%Y-%m-%d %H%M%S')

# cases.xlsx路径
testdata_dir = cur_dir.replace('conf', 'testdatas')
testdata_abspath = '%s/%s' % (testdata_dir, rc.get_ini_value('testcase', 'testcase_name'))

# testcase目录
testcase_dir = cur_dir.replace('conf', 'testcases')

# report.html路径
report_dir = cur_dir.replace('conf', 'reports')
report_abspath = '%s/api_autotest_report_%s.html' % (report_dir, cur_time)

# log路径
log_dir = cur_dir.replace('conf', 'logs')
log_abspath = '%s/api_autotest_log_%s.log' % (log_dir, cur_time)

# 图片目录
img_dir = cur_dir.replace('conf', 'resources')

if not os.path.exists(report_dir):
    os.makedirs(report_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
