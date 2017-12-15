#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
# Created by yaochao at 2017/12/6


import requests
from selenium import webdriver

class Downloader:

    def __init__(self, url, is_ajax=False):
        self.url = url
        self.is_ajax = is_ajax
        if is_ajax:
            service_args = []
            service_args.append('--load-images=false')
            self.browser = webdriver.Chrome(service_args=service_args)

    def _downlod(self):
        ''' 下载页面，返回页面源代码 '''
        if self.is_ajax:
            self.browser.get(url=self.url)
            return self.browser.page_source
        res = requests.get(url=self.url,)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            return res.text

    @property
    def html(self):
        return self._downlod()

    def __del__(self):
        # try:
        #     self.browser.close()
        # except AttributeError:
        #     pass

        # builtins.hasattr(o, name):This is done by calling getattr(obj, name) and catching AttributeError
        if hasattr(self, 'browser'):
            self.browser.close()

