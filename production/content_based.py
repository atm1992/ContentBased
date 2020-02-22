# -*- coding: UTF-8 -*-
import csv
import operator
import os
import sys
import util.read as read


def get_up(item_cate, in_file):
    """
    用户刻画，获取用户最感兴趣的topK个类别及其兴趣强度
    up —— user profile
    :param item_cate: a dict, key itemid, value a dict key category, value ratio
    :param in_file: user ratings file
    :return: a dict, key userid, value [(category1,ratio1),(category2,ratio2)...]
    """
    if not os.path.exists(in_file):
        return {}
    score_thr = 4.0
    topK = 2
    record = {}
    up = {}
    with open(in_file, "r") as f:
        data = csv.reader(f)
        header = next(data)
        for item in data:
            if len(item) < 4:
                continue
            userId, movieId, rating, timestamp = item[0], item[1], float(item[2]), int(item[3])
            if rating < score_thr:
                continue
            if movieId not in item_cate:
                continue
            time_score = get_time_score(timestamp)
            if userId not in record:
                record[userId] = {}
            for fix_cate in item_cate[movieId]:
                if fix_cate not in record[userId]:
                    record[userId][fix_cate] = 0
                record[userId][fix_cate] += rating * time_score * item_cate[movieId][fix_cate]
    for user_id in record:
        if user_id not in up:
            up[user_id] = []
        total_score = 0
        for cate, score in sorted(record[user_id].items(), key=operator.itemgetter(1), reverse=True)[:topK]:
            up[user_id].append((cate, score))
            total_score += score
        # 归一化
        for i in range(len(up[user_id])):
            up[user_id][i] = (up[user_id][i][0], round(up[user_id][i][1] / total_score, 3))
    return up


def get_time_score(timestamp, in_file="../data/ratings.csv"):
    """
    time decay（时间衰减），即 不同时期的行为所占权重不同
    获取时间权重
    :param in_file: default is user ratings file
    :param timestamp: input timestamp, xxx seconds
    :return: time score
    """
    # max_timestamp = read.get_max_timestamp(in_file)
    max_timestamp = 1537799250
    # convert seconds to days
    total_sec = 24 * 60 * 60
    delta = (max_timestamp - timestamp) / total_sec / 100
    # delta 越小，得分越高，最高分为1
    return round(1 / (1 + delta), 3)


def recom(cate_item_sort, up, userid, topK=10):
    """
    基于内容的推荐
    :param cate_item_sort: 各个类别下排名前topK的items(根据item的平均得分)
    :param up: 用户刻画，用户最感兴趣的topK个类别及其兴趣强度
    :param userid: 向指定用户进行推荐
    :param topK: 推荐结果物品的个数
    :return: a dict, key userid, value [itemid1,itemid2,...]
    """
    if userid not in up:
        return {}
    recom_res = {}
    if userid not in recom_res:
        recom_res[userid] = []
    for cate, ratio in up[userid]:
        # 一个类别下召回的物品数，后面加1是避免各个类别下召回的物品数之和小于最终的topK
        num = int(topK * ratio) + 1
        if cate not in cate_item_sort:
            continue
        recom_list = cate_item_sort[cate][:num]
        recom_res[userid] += recom_list
    return recom_res


def run_main():
    ave_score = read.get_ave_score("../data/ratings.csv")
    item_cate, cate_item_sort = read.get_item_cate(ave_score, "../data/movies.csv")
    up = get_up(item_cate, "../data/ratings.csv")
    # 少了442这个user，因为该用户的所有评分都小于4.0，说明该用户看过的所有电影都不感兴趣，很难进行推荐
    print(len(up))
    print(up["1"])
    print(recom(cate_item_sort, up, "1"))


if __name__ == '__main__':
    run_main()
