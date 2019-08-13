# -*- coding: utf-8 -*-
import scrapy
import os
from scrapy import Request
import requests
from requests import codes
import jsonpath_rw_ext
from urllib.parse import urlencode
import json
from ..items import ImageItem

'''
created_time:2018.7.16
recode_time:2019.8.3
author:zhangjuyang
'''

class ImagesSpider(scrapy.Spider):
    name = 'images'
    allowed_domains = ['images.so.com']
    start_urls = ['http://images.so.com/']

    header = {
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Host':'images.so.com',
        'Proxy-Connection':'keep-alive',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                     ' Chrome/73.0.3683.86 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
    }

    header_download = {
        'Accept':'text/html,application/xhtml+xml,application/xml;'
                 'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'p1.so.qhimgs1.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                     '(KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }

    def start_requests(self):
        data = {'ch': 'beauty', 'listtype': 'new'}
        #TYPE_ID is an image type keyword that can be set in settings
        base_url = 'http://images.so.com/zjl?ch=beauty&t1={type_id}'.format(type_id=self.settings.get('TYPE_ID'))
        for page in range(0,self.settings.get('MAX_PAGE') + 1):
            data['sn'] = page * 30
            params = urlencode(data)
            url = base_url + params
            yield Request(url, headers=self.header, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)
        for image in result.get('list'):
            item = ImageItem()
            gid = image.get('grpmd5')
            item['id'] = image.get('id')
            item['url'] = image.get('qhimg_url')
            item['title'] = image.get('title')
            item['thumb'] = image.get('qhimg_thumb')
            item['gid'] = gid
            yield item

            img_path = 'D:\\images.so_webspider\\images' + os.path.sep + image.get('title')
            if not os.path.exists(img_path):
                os.mkdir(img_path)
                try:
                    t = requests.get(
                        'http://images.so.com/z?a=jsondetailbygidv2&currsn=0&identity=list&ch=beauty&gid={gid}'.format(
                            gid=gid),headers = self.header)
                    if codes.ok == t.status_code:
                        img_url = json.loads(t.text)
                        imgs  = jsonpath_rw_ext.match('$..qhimg_url', img_url)
                        for img in imgs:
                            image = requests.get(img, headers=self.header_download)
                            file_path = img_path + os.path.sep + '{img}'.format(img=img[24:])
                            with open(file_path, 'wb') as f:
                                f.write(image.content)
                                print('Downloaded image path is %s' % file_path)
                except Exception as e:
                    print(e)
