#!/usr/bin/env python
# coding: utf8

"""
Usage:
$ python test_search.py -p 20

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


host = "http://b2cwechat.show.wepiao.com"
search = "/items?city_name=全国&per_page=1000&page=1&keyword=%s"
items = "/items?city_name=全国&page=1&per_page=3000&return_type=2"
search_url = host + search
items_url = host + items


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-p', '--pool-size', type=int, default=10)
    return p.parse_args()


def urlopen(url):
    print >> sys.stderr, 'urlopen', url
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount('http://', adapter)
    res = session.get(url, timeout=10).content
    data = json.loads(res)
    return data


def get_item_title(url):
    item_data = urlopen(url)
    item_title = jsonpath(item_data, "$.list[*].item_title_cn")
    if item_title:
        return item_title


def search_itme_title(item):
    item_data = urlopen(search_url % item.encode('utf8'))
    search_result = jsonpath(item_data, "$.list[*].item_title_cn")
    return [item, search_result, item_data['info']['total']]


def check_result(result):
    test_pass = []
    test_fail = []
    for i in result:
        if i[2] == 0:
            test_fail.append(i[0] + ' -- null')
        elif i[0] == i[1][0]:
            test_pass.append(i[0])
        else:
            test_fail.append(i[0] + '--' + i[1][0])

    return {"test_pass": test_pass, "test_fail": test_fail}


def main():
    args = parse_args()
    pool = Pool(args.pool_size if args.pool_size > 0 else 1)

    item_title = get_item_title(items_url)
    search_result = pool.map(search_itme_title, item_title)
    # 验证时可使用少量项目，例如： item_title[:10]
    report = check_result(search_result)

    print "items_total: %s " % len(item_title)
    for i in report:
        print "  %s total : %s " % (i, len(report[i]))
    for i in report['test_fail']:
        print "fail: %s" % i

if __name__ == '__main__':
    main()



