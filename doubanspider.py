# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: 孟徐  Address: 919906433@qq.com
import scrapy
import urllib.request
from scrapy.http import Request,FormRequest
from PIL import Image
import re
#  import getpass  将密码进行隐藏
from douban.items import DoubanItem
import datetime
import sys
import io
class DoubanspiderSpider(scrapy.Spider):
    # 2018年4月8日 22:36:06爬取豆瓣时，IP被禁！# 未能爬取fav_num数据
    sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
    i=2
    weekdays={0:"星期一",1:"星期二",2:"星期三",3:"星期四",4:"星期五",5:"星期六",6:"星期日"}
    name = 'doubanspider'
    allowed_domains = ['douban.com']
    start_urls = ['https://www.douban.com/']
    # 设置头信息变量，供下面的代码中模拟成浏览器爬取
    headers={
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"zh-CN,zh;q=0.8",
        "Connection":"keep-alive",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "Referer":"https://www.douban.com/",
            }
    def next(self,response):
        """
        提取该页面中的全部日记url，并且跟踪这些url
        """
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(response.url)
        all_urls=response.xpath('//div[@class="content"]/div[@class="title"]/a/@href').extract()
        all_urls=list(filter(lambda x:True if "note" in x else False,all_urls))
        for url in all_urls:
            yield Request(url,headers=self.headers,meta={"cookiejar":response.meta["cookiejar"]},callback=self.parse_content)
        next_page_str=response.xpath('//span[@class="next"]/a/text()').extract_first(default='0')
        print(next_page_str)
        if next_page_str!='0':
            next_page="https://www.douban.com/"+"?p="+str(self.i)
            self.i=self.i+1                                                          #  调用全局变量i
            yield Request(next_page,meta={"cookiejar":response.meta["cookiejar"]},headers=self.headers,callback=self.next)
        else:
            print("爬取结束！")
    def parse_content(self,response):
        douban_item=DoubanItem()
        title=response.xpath('//*[@class="note-header note-header-container"]/h1/text()').extract()[0]
        author=response.xpath('//a[@class="note-author"]/text()').extract()[0]
        time=response.xpath('//span[@class="pub-date"]/text()').extract()[0]
        article_url=response.url
        if 'class="mod-tags"' in response.text:
            topics=response.xpath('//div[@class="mod-tags"]//a/text()').extract()
            topics=(',').join(topics)  # 将list转化为字符串
        else:
            topics='None'
        if "rec-num" in response.text:
            print("存在")
            recomment_num=int(response.xpath('//div[@class="rec-sec"]//span[@class="rec-num"]/text()').extract()[0])
        else:
            recomment_num=0
        author_url=response.xpath('//a[@class="note-author"]/@href').extract()[0]
        douban_item['title']=title
        douban_item['author']=author
        try:
            #time=datetime.datetime.strptime(time,"%Y-%m-%d %H:%M:%S")
            time=time.split(" ")
            time1=datetime.datetime.strptime(time[0],"%Y-%m-%d").date()
            time2=datetime.datetime.strptime(time[1],"%H:%M:%S").time()
            weekday=self.weekdays[time1.weekday()]
        except Exception as e:
            time=str(datetime.datetime.now())
            time=time.split(" ")
            time1=datetime.datetime.strptime(time[0],"%Y-%m-%d").date()
            time2=datetime.datetime.strptime(time[1].split('.')[0],"%H:%M:%S").time()
            weekday=self.weekdays[time1.weekday()]
        douban_item['time']=time2
        douban_item['date']=time1
        douban_item['weekday']=weekday
        douban_item['article_url']=article_url
        douban_item['author_url']=author_url
        douban_item['topics']=topics
        douban_item['recomment_num']=recomment_num
        # yield Request(author_url,meta={"cookiejar":response.meta["cookiejar"]},headers=self.headers,callback=self.author_info)
        yield douban_item
    def start_requests(self):  # 编写start_request()方法，第一次默认会调用该方法中的请求
        return [Request(url="https://accounts.douban.com/login/",headers=self.headers,meta={'cookiejar':1},callback=self.parse)]
    def parse(self, response):
        print('登录前Post表单填充')
        UserName=input("请输入您的豆瓣账号：")
        PassWord=input("请输入您的豆瓣密码：")
        response_text=response.text
        if "captcha_image" in response_text:
            # 获取验证码图片所在地址，获取后赋给captcha变量，此时captcha为一个列表
            captcha=response.xpath('//*[@id="captcha_image"]/@src').extract()  # 验证码的图片储存地址
            print("验证码地址："+captcha[0])
            match_obj=re.match('.*?name="captcha-id" value="(.*?)"',response_text,re.DOTALL)  # re.DOTALL是匹配带有回车键的字符串
            captcha_id=match_obj.group(1)
            print("验证码ID："+captcha_id)
            print("此时有验证码")
            # 设置将验证码图片存储到本地的本地地址
            localpath="D:\\python\\WebSpider\\web_scrapy\\模拟登录豆瓣并且爬取相应的数据\\captcha.png"
            # 将服务器中的验证码存储到本地，供我们在本地直接进行查看
            urllib.request.urlretrieve(captcha[0],filename=localpath)
            # 打开图片，方便我们识别图片中的验证码
            try:
                im=Image.open('D:\\python\\WebSpider\\web_scrapy\\模拟登录豆瓣并且爬取相应的数据\\captcha.png')
                im.show()
                # 通过input函数输入对应的验证码并赋予给captcha_value变量
                captcha_value=input("请输入验证码：")
            except:
                print("Error:代码出错！！！")
            # 设置要传递的POST表单
            data={
                "source":"None",
                 "redir":"https://www.douban.com/",
                 "form_email":UserName,  # 设置登录账号
                "form_password":PassWord,# 设置登录密码
                "captcha-solution":captcha_value,
                "captcha-id":captcha_id,
                "login":"登录",
                }
        else:
            print("此时没有验证码！！")
            # 设置没有验证码时，需要传入的POST的表单
            data={
                "source":"index_nav",
                "redir":"https://www.douban.com/",
                "form_email":UserName,
                "form_password":PassWord,
                }
        print("稍等，登陆中···")
        # 通过FormRequest.from_response() 进行登录
        return [FormRequest.from_response(response,meta={"cookiejar":response.meta["cookiejar"]},
                                              headers=self.headers,formdata=data,callback=self.next
                                              )]
