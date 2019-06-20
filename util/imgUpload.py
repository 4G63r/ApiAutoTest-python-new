# -*- coding: UTF-8 -*-
# @Author : Song, Hu
import os
import random
from conf import filePath
from common.baseRequest import base_request
from requests_toolbelt import MultipartEncoder


class ImgUpload:
    def __init__(self, method, url, body_type, headers, logger):
        self.img_dir = filePath.img_dir
        self.method = method
        self.url = url
        self.body_type = body_type
        self.headers = headers
        self.logger = logger

    @property
    def upload_data(self):
        imgs = self.img_list
        random_img = random.choice(imgs)  # 随机选取list中一个元素

        with open('%s/%s' % (self.img_dir, random_img), 'rb') as f:
            file = {
                'image': ('%s' % random_img, f, 'image/%s' % random_img.split('.')[1]),
                'isimage': '1'
            }
            file = MultipartEncoder(file)
            headers = {'Content-Type': file.content_type}
            headers.update(self.headers)
            self.logger.info("请求头信息：")
            self.logger.info("{}".format(headers))
            self.logger.info("请求体类型：{}".format(self.body_type))
            self.logger.info("请求体内容：{}".format(file))
            res = base_request(method=self.method, url=self.url, body_type=self.body_type, body_data=file,
                               headers=headers)
            return res

    @property
    def img_list(self):
        """获取resources目录下所有图片"""
        try:
            imgs = os.listdir(self.img_dir)  # list
        except FileNotFoundError:
            self.logger.exception('resources目录不存在')
        else:
            return imgs
