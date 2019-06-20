# -*- coding: UTF-8 -*-
# @Author : Song
from common.baseRequest import base_request


class CityWeather:
    """当天天气预报"""
    url = 'http://t.weather.sojson.com/api/weather/city/'

    def __init__(self, city='北京'):
        if city == '北京':
            self.city_code = 101010100  # 北京
        elif city == '上海':
            self.city_code = 101020100  # 上海
        elif city == '广州':
            self.city_code = 101280101  # 广州
        elif city == '深圳':
            self.city_code = 101280601  # 深圳
        else:
            self.city_code = None
        self.wi = self.json_res

    @property
    def json_res(self):
        url = self.url + str(self.city_code)
        res = base_request(method='get', url=url)
        res = res.json()
        return res

    @property
    def weather_info(self):
        status = self.wi.get('status')
        if status == 200:
            data = self.wi.get('data')
            city_info = self.wi.get('cityInfo')
            forecast = data.get('forecast')[0]
            time = self.wi.get('date')
            week = forecast.get('week')
            city = city_info.get('city')
            quality = data.get('quality')
            high = forecast.get('high')
            low = forecast.get('low')
            fx = forecast.get('fx')
            fl = forecast.get('fl')
            type_ = forecast.get('type')
            notice = forecast.get('notice')
            info = '天气提醒：今天是{time} {week}\n{city}的天气 {type} {high} {low} {fx} {fl} 空气质量{quality}\n^_^ {notice}'.format(
                time=time, week=week, city=city, type=type_, high=high, low=low, fx=fx, fl=fl, quality=quality,
                notice=notice)
        else:
            info = '暂支持北上广深的天气查询，其他城市敬请期待'
        return info
