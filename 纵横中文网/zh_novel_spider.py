"""
    1.爬取纵横中文网排行榜
    2.获取前几名小说内容
"""
import requests
from lxml import etree
import os
from ua_info import ua_list
import random

choice = {'月票榜':1,
          '24小时畅销榜':3,
          '新书榜':4,
          '点击榜':5,
          '推荐榜':6,
          '捧场榜':7,
          '完结榜':8,
          '新书订阅榜':9,
          '24小时更新榜':10}

class Spider:
    "爬虫类"
    def __init__(self):
        self.__url = 'https://www.zongheng.com/rank/details.html?rt={}&d=1'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'User-Agent': str(random.choices(ua_list))
        }

    def get_html(self,url):
        """
        获取网页源代码
        :param url:
        :return: 返回网页源代码
        """
        res = requests.get(url,headers=self.headers)
        #更改编码风格
        res.encoding = "utf-8"
        #得到HTML网页
        html = res.text
        #print(html)

        return html

    def parse_html(self,url):
        """
        解析每个榜单中的所有小说，包括小说名，以及小说网址
        :param url:
        :return: 字典（包括小说名，以及地址）
        """
        passage = self.get_key_info(url,"//div[@class='rank_d_pagesize pagebar']/@count")
        print("总页数：{}".format(passage[0]))

        novel_dict = {}
        for i in range(1,eval(passage[0])+1):
            pass_url = self.__url + "&p="+str(i)
            #print(pass_url)
            r_list = self.get_key_info(pass_url,"//div[@class='rank_d_b_name']/a/text()")
            novel_url = self.get_key_info(pass_url, "//div[@class='rank_d_b_name']/a/@href")
            novel_ticket = self.get_key_info(pass_url, "//div[@class='rank_d_b_ticket']/text()")

            #print(r_list)
            #print(novel_url)
            #print(len(r_list) == len(novel_url))
            for tmp in range(len(r_list)):
                # if not novel_ticket:
                #     novel_dict[r_list[tmp]] = [novel_url[tmp], []]
                # else:
                #     novel_dict[r_list[tmp]] = [novel_url[tmp],novel_ticket[tmp]]
                tickets = novel_ticket[tmp] if novel_ticket else 0
                novel_dict[r_list[tmp]] = [novel_url[tmp],tickets]


        #print(novel_dict)
        return novel_dict

    def get_key_info(self,url,key):
        """
        提取网站源代码中的关键信息
        :param key:
        :return: 关键信息
        """
        parse_html = etree.HTML(self.get_html(url))

        return parse_html.xpath(key)


    def turn_novel_page(self,url):
        """
        实现小说翻页功能
        :param url:
        :return: 返回下一页小说源代码
        """
        next_novel_add = self.get_key_info(url,"//a[@class='nextchapter']/@href")
        return next_novel_add[0]

    def choice_and_save_novel(self,novel):
        """
        选择小说，并打印相关的小说内容
        :return:
        """
        #打印小说榜单
        print("===============小说榜单=====================")
        print("{:^20} {:^20}".format("小说名","人气值"))
        for novel_name,tmp in novel.items():
            print("{:.^20} {:^20}".format(novel_name,tmp[1]))
        print("===========================================")

        choice = input("选择你想看的小说：")
        #choice = "不宋"
        passage_add = self.get_key_info(novel[choice][0],"//a[@class='btn read-btn']/@href")[0]
        #print(novel_con)



        os.makedirs("小说/"+choice,exist_ok=True)
        next_novel_add = passage_add
        novel_con = passage_add
        while True:
            novel_content = self.get_key_info(next_novel_add, "//div[@class='content']/p/text()")
            # print(novel_content)
            novel_title = self.get_key_info(next_novel_add,"//div[@class='title_txtbox']/text()")
            filename = choice + ' ' + novel_title[0].replace('\t',' ')
            with open("./小说/"+choice+"/"+filename+".txt",'w') as f:
                for tmp in novel_content:
                    f.write(str(tmp)+'\n')

            next_novel_add = self.turn_novel_page(next_novel_add)



    def run(self):
        print("==================小说榜单===================")
        for tmp,_ in choice.items():
            print(tmp)
        print("============================================")

        index = input("请选择你感兴趣的榜单：")
        #index = "月票榜"
        self.__url = self.__url.format(choice[index])
        novel = self.parse_html(self.__url)
        self.choice_and_save_novel(novel)

if __name__ == '__main__':
    Spider().run()
