#!/usr/bin/env python
# coding: utf8

"""
Prerequisite:
    brew install mysql-connector-c
    pip install MySQL-python
    
Usage:
    $ python search_sync_item.py | tee search_sync_item.log  

"""

import argparse
import sys
import json
import itertools
from functools import partial
from multiprocessing import Pool
from jsonpath import jsonpath
import time
import requests
from random import sample
import MySQLdb as mdb
import datetime


sql = "select wp_items.name, wp_cities.city_name, wp_items.update_at, wp_items.create_at " \
      "from wp_items join wp_cities on wp_items.cityid=wp_cities.city_id " \
      "where wp_items.endtime>'%s' and name not like '%%测试%%'" % datetime.date.today()

search_url_bd = "http://10.3.10.112:2005/search/showinfo/"
search_url_ui = "http://b2cwechat.show.wepiao.com/items?city_name=全国&per_page=10&page=1&keyword=%s"

<<<<<<< HEAD
test_item = [
    '[上海]0104单张套票非选座',
    '[上海]选座单张套票',
    '[上海]爱乐汇·《奥斯卡之夜》电影经典名曲视听交响音乐会']

ki_out_item = [
    '[北京] COCO',
    '[北京]直到世界尽头——7080经典动漫演唱会 北京站',
    '[广州]超级队长MixV虚拟现实互动体验街',
    '[杭州]爱乐汇·“天空之城”久石让&宫崎骏动漫作品视听音乐会',
    '[杭州]麦斯米兰"Fancy April"2017巡回演唱会—杭州站',
    '[黄冈]开心麻花爆笑舞台剧《李茶的姑妈》',
    '[济南]2017[A CLASSIC TOUR学友.经典] 世界巡回演唱会—济南站',
    '[昆明]爱乐汇《夜的钢琴曲》—石进钢琴作品音乐会',
    '[兰州]“东方艺术周”——城市因东方而美丽！《中国东方歌舞团经典歌舞晚会》',
    '[兰州]“东方艺术周”——城市因东方而美丽！舞蹈诗画《国色》',
    '[上海]“我心永恒”醉美的旋律经典名曲音乐会',
    '[上海]《夜上海》——海之花演绎上海老歌',
    '[上海]2016年四季上海亲子年票',
    '[上海]俄罗斯芭蕾国家剧院芭蕾舞团《胡桃夹子》',
    '[上海]玲珑国乐之近筝者·墨赵墨佳古筝专场音乐会',
    '[上海]猫和老鼠“身临鼠境”主题展',
    '[上海]上海爱乐乐团室内乐系列之 德奥大师杰作音乐会',
    '[上海]悬疑爱情舞台剧《出租屋》',
    '[上海]余德耀美术馆——周力：白影',
    '[上海]原创音乐剧《致命咖啡》瘾藏者系列',
    '[西安]爱乐汇· 《夜的钢琴曲》—石进钢琴作品音乐会',
    '[西安]法国新兴电子爵士SuPerDoG四重奏',
    '[西安]吉顿克莱默与布达佩斯交响乐团西安音乐会',
    '[西安]浪漫主义的最初灵感-XSO交响音乐会',
    '[西安]立陶宛米提斯弦乐四重奏音乐会',
    '[郑州]中国广播民族乐团室内乐音乐会',
    '[重庆]儿童剧《猪探长》',
    '[株洲]2017"话剧大赏"—非常林奕华·舞台剧《红楼梦》',
    '[石家庄]《天空之城—久石让宫崎骏经典动漫作品视听音乐会》',
    '[无锡]"Human and Divine"Ashram隐修所乐队2017巡演—无锡站',
    '[成都]饶晓志导演"淡未来"系列之《咸蛋》',
    '[上海]《开放夫妻》',
    '[杭州]2017杭州五一重磅活动 超级枕头大战',
    '[上海]2017上海五一重磅活动 欧洲超模DJ巡演&超级荧光派对']

=======
>>>>>>> 119c3d317130dc70f22551747c5351d3cbc451c7

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-p', '--pool-size', type=int, default=10)
    return p.parse_args()


def get_ki_item():
    ki_test_item = [i.strip('\n') for i in open('./ki_test_item').readlines()]
    ki_off_item = [i.strip('\n') for i in open('./ki_off_item').readlines()]
    ki_change_item = [i.strip('\n') for i in open('./ki_change_item').readlines()]
    return ki_test_item, ki_off_item, ki_change_item


def get_mysql_item():
    mysql_item = []
    conn = mdb.connect(host="10.66.139.68", port=3306, user="qa_test", passwd="xrUdRmuuXOYjSC2hw3jaupnAQ",
                       db="gewara", charset="utf8")
    cursor = conn.cursor()
    cursor.execute(sql)
    r = cursor.fetchall()
    for i in r:
        mysql_item.append(i)

    return mysql_item


def merge_item(item):
    return ["[" + item[1][:-1] + "]" + item[0], item[2], item[3]]


def search_itme_bd(item):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {"keywords": item[0]}
    res = requests.post(url=search_url_bd, data=data, headers=headers).json()
    print >> sys.stderr, 'bd search: ', item[0]
    search_result = jsonpath(res, "$.data[*].itemTitleCN")
    if len(search_result) > 2:
        search_result = search_result[:3]

    return [item, search_result, res['page']['totalItem']]


def check_result(result):
    test_pass_1 = []
    test_pass_2 = []
    test_pass_3 = []
    ki_test = []
    ki_off = []
    ki_change = []
    # 搜索接口返回的列表中，第一个项目名称与搜索名称完全一致，则pass_1,以此类推，检查前3项
    test_fail = []

    ki_test_item, ki_off_item, ki_change_item = get_ki_item()

    for i in result:
        if i[2] == 0:
            test_fail.append(i[0] + ' -- null')
        elif i[0][0] == i[1][0]:
            test_pass_1.append(i[0])
        elif i[0][0] == i[1][1]:
            test_pass_2.append(i[0])
        elif i[0][0] == i[1][2]:
            test_pass_3.append(i[0])
        elif i[0][0].encode('utf8') in ki_test_item:
            ki_test.append(i[0])
        elif i[0][0].encode('utf8') in ki_off_item:
            ki_off.append(i[0])
        elif i[0][0].encode('utf8') in ki_change_item:
            ki_change.append(i[0])
        else:
            test_fail.append([i[0], i[1]])

    return {"test_pass_1": test_pass_1,
            "test_pass_2": test_pass_2,
            "test_pass_3": test_pass_3,
            "ki_test": ki_test,
            "ki_off": ki_off,
            "ki_change": ki_change,
            "test_fail": test_fail}


def main():
    args = parse_args()
    pool = Pool(args.pool_size if args.pool_size > 0 else 1)

    mysql_item = get_mysql_item()
    item_name = pool.map(merge_item, mysql_item)
    search_result_bd = pool.map(search_itme_bd, item_name)
    report = check_result(search_result_bd)

    print "items_total: %s" % len(mysql_item)
    for i in report:
        print "  %s total: %s" % (i, len(report[i]))
    for i in report['ki_test']:
        print "已知问题_测试类: %s" % i[0].encode('utf8')
    for i in report['ki_off']:
        print "已知问题_已下架: %s" % i[0].encode('utf8')
    for i in report['ki_change']:
        print "已知问题_再编辑: %s" % i[0].encode('utf8')

    for i in report['test_fail']:
        print "失败: %s||create_at:%s||update_at:%s||past:%s" \
              % (i[0][0].encode('utf8'), i[0][2], i[0][1], datetime.datetime.now()-i[0][1])
        for j in range(len(i[1])):
            print "    get%s:%s" % (j+1, i[1][j].encode('utf8'))


if __name__ == '__main__':
    main()
