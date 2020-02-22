# -*- coding: UTF-8 -*-
import csv
import operator
import os


def get_ave_score(in_file):
    """
    获取每个item的平均得分
    :param in_file: user rating file
    :return: a dict, key itemid, value ave_score
    """
    if not os.path.exists(in_file):
        return {}
    record = {}
    ave_score = {}
    with open(in_file, "r") as f:
        data = csv.reader(f)
        header = next(data)
        for item in data:
            if len(item) < 4:
                continue
            userId, movieId, rating = item[0], item[1], float(item[2])
            if movieId not in record:
                record[movieId] = [0, 0]
            record[movieId][0] += rating
            record[movieId][1] += 1
    for i in record:
        ave_score[i] = round(record[i][0] / record[i][1], 3)
    return ave_score


def get_item_cate(ave_score, in_file):
    """
    物品刻画，获取item在各个类别的占比 以及 各个类别下排名前topK的items(根据item的平均得分)
    :param ave_score: a dict, key itemid, value ave_score
    :param in_file: item info file
    :return:
        a dict key itemid, value a dict key cate,value ratio
        a dict key cate, value [itemid1,itemid2,...]
    """
    if not os.path.exists(in_file):
        return {}, {}
    item_cate = {}
    record = {}
    cate_item_sort = {}
    topK = 100
    with open(in_file, "r") as f:
        data = csv.reader(f)
        header = next(data)
        for item in data:
            if len(item) < 3:
                continue
            movieId, cate_str = item[0], item[-1]
            cate_list = cate_str.strip().split("|")
            ratio = round(1 / len(cate_list), 3)
            if movieId not in item_cate:
                item_cate[movieId] = {}
            for fix_cate in cate_list:
                item_cate[movieId][fix_cate] = ratio
    for i in item_cate:
        for cate in item_cate[i]:
            if cate not in record:
                record[cate] = {}
            itemid_rating_score = ave_score.get(i, 0)
            record[cate][i] = itemid_rating_score
    for cate in record:
        if cate not in cate_item_sort:
            cate_item_sort[cate] = []
        for item_id, _ in sorted(record[cate].items(), key=operator.itemgetter(1), reverse=True)[:topK]:
            cate_item_sort[cate].append(item_id)
    return item_cate, cate_item_sort


def get_max_timestamp(in_file):
    """
    获取用户评分文件中的最大时间戳，即 距离现在最近的时间
    time decay（时间衰减），即 不同时期的行为所占权重不同
    :param in_file:
    :return:
    """
    if not os.path.exists(in_file):
        return 0
    latest=0
    with open(in_file,"r") as f:
        data = csv.reader(f)
        header = next(data)
        for item in data:
            if len(item)<4:
                continue
            timestamp = int(item[3])
            if timestamp>latest:
                latest=timestamp
    return latest


if __name__ == '__main__':
    # ave_score = get_ave_score("../data/ratings.csv")
    # print(len(ave_score))
    # print(ave_score["31"])
    # item_cate, cate_item_sort = get_item_cate(ave_score, "../data/movies.csv")
    # print(item_cate["1"])
    # print(cate_item_sort["Children"])
    print(get_max_timestamp("../data/ratings.csv"))
