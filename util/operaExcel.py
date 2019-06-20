# -*- coding: UTF-8 -*-
# @Author : Song
from openpyxl import load_workbook
from openpyxl.styles import PatternFill


class OperaExcel:
    """操作excel"""

    def __init__(self, file_path, file_sheet, logger):
        self.wb = load_workbook(file_path)
        self.wb_case_sh = self.wb[file_sheet]
        sheet_names = self.wb.sheetnames
        if 'prepare_data' in sheet_names:
            self.wb_prepare_sh = self.wb['prepare_data']
        self.logger = logger

    @property
    def prepare_data(self):
        """从excel中读取初始化数据，并对初始值进行递增处理"""
        try:
            init_data = {}
            for row in range(2, self.wb_prepare_sh.max_row + 1):
                key = self.wb_prepare_sh.cell(row, GlobalVar.PREPARE_KEY).value
                value = self.wb_prepare_sh.cell(row, GlobalVar.PREPARE_VALUE).value
                init_data[key] = value
            init_data['${phone}'] = init_data['${init_phone}'] + 1
            init_data['${noReg_phone}'] = init_data['${init_phone}'] + 2
            self.logger.info('初始化数据为: {0}'.format(init_data))
            return init_data
        except (KeyError, TypeError, AttributeError):
            return None

    def update_init_data(self):
        """测试结束后更新初始化数据"""
        init_data = self.prepare_data
        if init_data:
            init_data = self.wb_prepare_sh.cell(2, 2).value
            self.wb_prepare_sh.cell(2, 2).value = init_data + 3
            self.logger.info('初始化数据已更新为: {0}'.format(init_data + 3))
        else:
            pass

    @property
    def all_case_datas(self):
        """获取全部cases"""
        all_case_data = []
        for row in range(3, self.wb_case_sh.max_row + 1):
            case_data = dict()
            case_data['case_id'] = self.get_cell(row, GlobalVar.CASE_ID).value
            case_data['is_run'] = self.get_cell(row, GlobalVar.IS_RUN).value
            api_name = self.get_cell(row, GlobalVar.API_NAME).value
            api_info = self.get_cell(row, GlobalVar.API_INFO).value
            case_data['case_name'] = self.get_cell(row, GlobalVar.CASE_NAME).value
            if not api_name:
                if not api_info:
                    api_info = 'no_expound'
                case_data['html_case_name'] = '{0}_{1}'.format(case_data['case_name'], api_info)
            else:
                case_data['html_case_name'] = '{0}_{1}_{2}'.format(case_data['case_name'], api_name, api_info)
            case_data['method'] = self.get_cell(row, GlobalVar.METHOD).value
            case_data['url'] = self.get_cell(row, GlobalVar.URL).value
            case_data['body_type'] = self.get_cell(row, GlobalVar.BODY_TYPE).value
            # headers
            temp_headers = self.get_cell(row, GlobalVar.HEADERS).value
            header_dict = dict()
            if temp_headers:
                if '\n' in temp_headers:
                    for i in temp_headers.split('\n'):
                        if ':' in i:
                            temp = i.split(':')
                        else:
                            temp = i.split(' ', 1)
                        if temp[0] == 'authorization':
                            key = 'Authorization'
                        elif temp[0] == 'user-agent':
                            key = 'User-Agent'
                        elif temp[0] == 'x-identity-code':
                            key = 'X-Identity-Code'
                        else:
                            key = temp[0]
                        header_dict[key] = temp[1].strip()
                else:
                    if ':' in temp_headers:
                        temp = temp_headers.split(':')
                    else:
                        temp = temp_headers.split(' ', 1)
                    if temp[0] == 'authorization':
                        key = 'Authorization'
                    elif temp[0] == 'user-agent':
                        key = 'User-Agent'
                    elif temp[0] == 'x-identity-code':
                        key = 'X-Identity-Code'
                    else:
                        key = temp[0]
                    header_dict[key] = temp[1].strip()
            else:
                pass
            case_data['headers'] = header_dict
            # body_data
            temp_request_body = self.get_cell(row, GlobalVar.BODY_DATA).value
            if temp_request_body is None:
                case_data['body_data'] = {}
            else:
                init_data = self.prepare_data
                if init_data:
                    for k, v in init_data.items():
                        if k in temp_request_body:
                            temp_request_body = temp_request_body.replace(k, str(v))
                            self.logger.info("初始化之后的请求数据为：{0}".format(temp_request_body))
                case_data['body_data'] = eval(temp_request_body)

            case_data['expected_res'] = self.get_cell(row, GlobalVar.EXPECT_RES).value
            case_data['compare_exp'] = self.get_cell(row, GlobalVar.COMPARE_EXP).value
            case_data['compare_type'] = self.get_cell(row, GlobalVar.COMPARE_TYPE).value
            case_data['related_exp'] = self.get_cell(row, GlobalVar.RELATED_EXP).value
            case_data['is_related'] = self.get_cell(row, GlobalVar.IS_RELATED).value
            all_case_data.append(case_data)
        return all_case_data

    @staticmethod
    def get_expected_result_list(expect_data):
        """获取期望结果list"""
        expected_result_list = []
        if expect_data:
            if isinstance(expect_data, str):
                if '\n' in expect_data:
                    for i in expect_data.split('\n'):
                        expected_result_list.append(i.strip())
                else:
                    expected_result_list.append(expect_data)
            else:
                expected_result_list.append(str(expect_data))
            return expected_result_list
        else:
            return None

    def save_excel(self, file_path):
        """保存excel"""
        try:
            self.wb.save(file_path)
        except Exception as e:
            self.logger.exception(e)

    def get_cell(self, row, col=None):
        """获取单元格对象"""
        if col is None:
            col = GlobalVar.ACTUAL_RES
        cell = self.wb_case_sh.cell(row, col)
        return cell

    def write_in_result(self, row, result):
        """写入测试结果并填充单元格颜色"""
        self.get_cell(row).value = result
        if result.upper() == 'PASS':
            self.color_fill(row, 'FF00FF00')
        elif result.upper() == 'FAIL':
            self.color_fill(row, 'FFFF0000')
        else:
            pass

    def color_fill(self, row, color):
        """
        设置单元格样式，暂支持颜色填充
        FF00FF00:绿色
        FFFF0000:红色
        """
        cell = self.get_cell(row)
        fill = PatternFill(start_color=color, end_color=color, fill_type='solid')
        cell.fill = fill

    @property
    def case_title(self):
        """用例名称"""
        title = self.get_cell(1, 2).value
        return title


class GlobalVar:
    CASE_ID = 1
    IS_RUN = 2
    API_NAME = 3
    API_INFO = 4
    CASE_NAME = 5
    METHOD = 6
    URL = 7
    HEADERS = 8
    BODY_TYPE = 9
    BODY_DATA = 10
    EXPECT_RES = 11
    COMPARE_EXP = 12
    COMPARE_TYPE = 13
    RELATED_EXP = 14
    IS_RELATED = 15
    ACTUAL_RES = 16

    PREPARE_KEY = 1
    PREPARE_VALUE = 2
