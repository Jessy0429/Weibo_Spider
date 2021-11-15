import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import requests
import json
import time
import gc
from util.spider_fans import get_file_list, read_json_files, item_num
"""
    网址：https://m.weibo.cn/p/2304133479691367_-_WEIBO_SECOND_PROFILE_WEIBO
"""

def repeat_request(url):
    try:
        response = requests.request("GET", url)
    except:
        time.sleep(5)
        response = requests.request("GET", url)
    data = response.content
    data = json.loads(data)
    if data['ok'] == 0:
        # 未获取到数据
        return data, False
    elif len(data['data']['cards']) == 0:
        # 数据不完整
        return data, False
    elif data['data']['cards'][-1]['card_type'] == 58:
        # 数据不完整
        return data, False
    else:
        return data, True


def get_test(text):
# 处理标签
    while(text.find('>')>-1):
        # 处理标签，获取纯文本
        start = text.find('<')
        end = text.find('>')+1
        text = text[:start]+text[end:]

    return text


def spider_blogs(user_id, page):
    blogs = []
    contents_list = []
    url = "https://m.weibo.cn/api/container/getIndex?containerid=230413{}_-_WEIBO_SECOND_PROFILE_WEIBO&page_type=03" \
          "&page={}".format(user_id, page)
    data, success_flag = repeat_request(url)

    # 返回数据为空时，repeat
    wait_time = 0.5
    while not success_flag:
        print("Request Failed!!!\tWait {}s".format(wait_time))
        time.sleep(wait_time)
        data, success_flag = repeat_request(url)
        if wait_time >= 5:
            return [], True
        else:
            wait_time *= 2

    contents_list = data['data']['cards']
    end = False
    if page == 1:
        contents_list.pop(0)
        # contents_list.pop(1)
        contents_list[0] = contents_list[0]['card_group'][0]

    for content in contents_list:
        if content['mblog']['user'] is not None:
            text = get_test(content['mblog']['text'])
            blogs.append(text)

    return blogs, end


if __name__ == '__main__':
    # blogs_infos = {}
    user_ids = [3479691367]
    # blogs_infos[3479691367] = []
    for i in range(0, 2):
        with open('../data/relatives-depth{}.json'.format(i), 'r') as f:
            json_datas = json.load(f)
            for json_data in json_datas:
                for fan in json_data['fans_info']:
                    # blogs_infos[fan['fan_id']] = []
                    user_ids.append(fan['fan_id'])
                for follower in json_data['followers_info']:
                    # blogs_infos[follower['follower_id']] = []
                    user_ids.append(follower['follower_id'])

    # user_ids = list(blogs_infos.keys())
    # if user_ids.empty():
    #     with open('../data/blogs_info.json', 'w') as f:
    #         json.dump(blogs_infos, f)
    # else:
    cache_files = get_file_list('../data/cache/blogs')
    user_cache, last_data = read_json_files(cache_files)
    user_id_cache = set(user_cache.keys())
    del user_cache
    gc.collect()
    total = len(user_ids)
    for i, user_id in enumerate(user_ids):
        if str(user_id) in user_id_cache:
            print('{}/{}:\t{} in cache'.format(i, total, user_id))
            # user_blogs.append(user_cache[str(user_id)])
        else:
            page = 1
            print('{}/{}:\t{}'.format(i, total, user_id))
            user_blogs = []

            while True:
                blogs, end = spider_blogs(user_id, page)
                user_blogs += blogs
                print(blogs)
                if end:
                    break
                else:
                    page = page + 1

            last_data[user_id] = user_blogs
            if len(last_data) > 20:
                cache_files.append('../data/cache/blogs/blogs_user_cache{:0>3d}.json'.format(len(cache_files)))
                last_data = {}
                last_data[user_id] = user_blogs

            with open('../data/cache/blogs/blogs_user_cache{:0>3d}.json'.format
                          (len(cache_files) - 1), 'w') as cache_f:
                json.dump(last_data, cache_f)

    print('spider over\n')
    # with open('../data/blogs_info.json', 'w') as f:
    #     json.dump(blogs_infos, f)




