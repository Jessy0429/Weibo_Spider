import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import jieba
import json
import re
from spider_fans import get_file_list
from tqdm import tqdm


cache_files = get_file_list(rootPath + '/data/cache/blogs')

last_words = [""]
with open(rootPath + '/data/weibo_contents_cut.txt', 'w') as txt_f:
    for file_path in cache_files:
        with open(file_path, 'r') as json_f:
            data = json.load(json_f)
            for contents in data.values():
                for content in contents:
                    if content != '转发微博':
                        # print(content)
                        words = jieba.cut(content)
                        words_removed = []
                        for word in words:
                            word = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])","",word)
                            if len(word) > 0:
                                words_removed.append(word)
                        if len(words_removed) > 0:
                            if words_removed[0] != last_words[0] and words_removed[-1] != last_words[-1]:
                                txt_f.write(' '.join(words_removed) + '\n')
                                last_words = words_removed
                            # else:
                            #     print('-'*80)
                            #     print(last_words)
                            #     print(words_removed)
                        # print(words_removed)


# print(list(jieba.cut('绒绒线马甲通用主体编织方法~分袖2为了满足5分钟内的要求，变速后声音好奇怪呀  快来围观我的精彩微视频！＞＞ #小影微视频#（通过#小影#创作）')))
            
