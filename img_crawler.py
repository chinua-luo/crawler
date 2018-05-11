#!/usr/bin/env python3  # 保证可以直接Unix/Linux/Mac上运行
# -*- coding: utf-8 -*-
__Author__: 'Lucifer'
__Date__: "2018/05/11  上午 11:15"
__Name__: 'baidu_img_crawler.py'
__IDE__: 'PyCharm'

import urllib.parse
import itertools
from urllib.request import urlopen, urlretrieve
import urllib.error
import re
from bs4 import BeautifulSoup
import os
import time

class Crawler:
    # 第一步定义解密包
    _str_table = {
        '_z2C$q': ':',
        '_z&e3B': '.',
        '_z&amp;e3B': '.',
        'AzdH3F': '/'
    }
    _char_table = {
        'w': 'a',
        'k': 'b',
        'v': 'c',
        '1': 'd',
        'j': 'e',
        'u': 'f',
        '2': 'g',
        'i': 'h',
        't': 'i',
        '3': 'j',
        'h': 'k',
        's': 'l',
        '4': 'm',
        'g': 'n',
        '5': 'o',
        'r': 'p',
        'q': 'q',
        '6': 'r',
        'f': 's',
        'p': 't',
        '7': 'u',
        'e': 'v',
        'o': 'w',
        '8': '1',
        'd': '2',
        'n': '3',
        '9': '4',
        'c': '5',
        'm': '6',
        '0': '7',
        'b': '8',
        'l': '9',
        'a': '0',
    }
    # str的translate方法需要单个字符串的十进制Unicode编码作为key 才能替换
    _char_table = {ord(key): ord(value) for key, value in _char_table.items()}
    """ Return the Unicode code point for a one-character string. """

    def __init__(self):
        pass

    def imgDecode(self, url):
        """
        利用字典序解码图片的Url， 获取真实URL
        :param url: encoded url
        :return: decoded url
        """
        for k, v in Crawler._str_table.items():
            url = url.replace(k, v)  # 把加密的特殊符号位置换成真正的
        # str的translate方法需要单个字符串的十进制Unicode编码作为key
        # value 中的数字会被当做十进制Unicode编成字符
        # 也可以直接用字符串作为value
        # translate() 剩下的全部换掉
        return url.translate(Crawler._char_table)

    def get_urls(self, keyword):
        """
        给定关键词进行搜索
        :param keyword: 关键词
        :return: 一个请求头的迭代器
        """
        # 生成大量网址的无限迭代器
        # S.format(*args, **kwargs) -> str
        # Return a formatted version of S, using substitutions from args and kwargs.
        # The substitutions are identified by braces ('{' and '}').
        keyword = urllib.parse.quote(keyword)  # 进行Unicode编码
        initUrl = 'http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&queryWord='+keyword+'&cl=&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=&z=&ic=&word='+keyword+'&s=&se=&tab=&width=&height=&face=&istype=&qc=&nc=&fr=&cg=girl&pn={pn}&rn=30'  # &gsm=1e&1526010493260='
        Urls = (initUrl.format(pn=x) for x in itertools.count(start=0, step=30))  # 迭代器
        """
        count(start=0, step=1) --> count object 一个count类的迭代器
        Return a count object whose .__next__() method returns consecutive values.
        Equivalent to:
            def count(firstval=0, step=1):
                x = firstval
                while 1:
                    yield x
                    x += step
        """
        return Urls

    def get_img(self, Urls, pages_num, start_page, directoryPath):
        flag = 0  # 页面标识位
        # 先把页面调到指定的开始下载页面
        for url in Urls:
            if flag in range(start_page - 1):
                #  保证从 start_page 开始下载  # 放在下面循环里面就出错了， 每次循环，flag 一直在加
                flag += 1
                continue  # 调节 url的位置

        for url in Urls:
            if start_page <= pages_num + flag:
                try:
                    js = urlopen(url)
                    bsobj = BeautifulSoup(js, 'lxml')
                except urllib.error:
                    print('不慌！！继续， 总数不会少')
                    pages_num += 1
                obj_url = re.findall(r'"objURL":"([a-z0-9A-Z\-_;&$%=]*3r2)"', str(bsobj))  # 就是除了‘,’ 之外的都匹配了
                # 把解密的url进行保存
                obj_url = [self.imgDecode(url) for url in obj_url]
                self.save_img(obj_url, directoryPath)
            else:
                print('下载完成！！！')
                break
            start_page += 1

    def save_img(self, obj_url, directoryPath):
        """
        保存这页的图片
        :param obj_url: iterable 图片链接
        :param directoryPath: 保存路径
        :return:
        """
        if not os.path.exists(directoryPath):
            os.makedirs(directoryPath)
        # 存入的时候里面有多少图片
        self._counter = len(os.listdir('./' + directoryPath)) + 1
        for imginfo in obj_url:
            try:                                          # 这个反斜杠别少了， 让图片存入指定文件夹中的
                urlretrieve(imginfo, './' + directoryPath + '/' + str(self._counter) + '.jpg')
            except Exception as err:
                time.sleep(1)
                print(err)  # HTTP Error 403: Forbidden 可能是某些图片失效了
                # HTTP Error 502: Bad Gateway HTTP Error 404: Not Found
                # <urlopen error [WinError 10060] 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。>
                # <urlopen error [Errno 11001] getaddrinfo failed>
                print("产生未知错误，放弃保存")
                continue
            else:
                print("正在下载图片.....,已下载：" + str(self._counter))
                self._counter += 1
        return None
    def start(self, keyword, pagesnum=1, startpage=1):
        """
        爬虫入口
        :param keyword:  关键词
        :param pagesnum:  下载页数 默认为1
        :param startpage: 起始页 默认为1
        :return:
        """
        #  把输入的文字转化成UTF-8编码加入到URL
        self._keyword = keyword
        self._pagenums = pagesnum
        self._startpage = startpage
        self._counter = 0  # 记录下载量的计数器
        self.get_img(self.get_urls(self._keyword), self._pagenums, self._startpage, self._keyword)



if __name__ == "__main__":
    crawler = Crawler()
    crawler.start('火灾', 20, 2)
