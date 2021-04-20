#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 9:27 上午
# @Author  : SPC
# @FileName: Rule.py
# @Software: PyCharm
# @Des     : 用于制定相关的规则

import re

SYNONYM_MAP = {
    '丈夫': '丈夫配偶',
    '老公': '丈夫配偶',
    '妻子': '妻子配偶',
    '夫人': '夫人妻子配偶',
    '媳妇': '妻子配偶',
    '老家': '老家籍贯',
    '故乡': '故乡家乡籍贯出生地',
    '家乡': '故乡家乡籍贯出生地',
    '英文': '外文英文',
    '的工作': '职业',
    '西班牙语': '外文西班牙语',
    '贡献': '贡献主要成就',
    '功绩': '功绩主要成就',
    '事迹': '事迹主要成就',
    '丰功伟绩': '丰功伟绩主要成就',
    '来源': '来源出处',
    '外号': '外号别名别称',
    '在金庸小说《天龙八部》中': ''
}
Interrogative_words_dict = [
    "为什么", "怎么样", "怎么着",
    "怎么", "怎的", "怎样", "如何", "哪些", "哪里", "哪儿", "什么", "几时", "多少",
    "谁", "何", "几", "怎", "哪"
]


def ChangeDataForm(sequence: str):
    """
    将问题中的年月日统一形式
    :param sequence:
    :return:
    """
    time_pattern = re.compile("(\d{2,4}年\d{1,2}月\d{1,2}日|\d{2,4}年\d{1,2}月|\d{1,2}月\d{1,2}日)")
    result = re.search(time_pattern, sequence)
    if result:
        sub_seq = list(sequence[result.start():result.end()])
        y_pos = -1
        for i in range(len(sub_seq)):
            if sub_seq[i] == "年":
                y_pos = i
                sub_seq[i] = ""
                if y_pos == 2:
                    year = int(sub_seq[0] + sub_seq[1])
                    if year < 20:
                        sub_seq[0] = "20" + sub_seq[0]
                    else:
                        sub_seq[0] = "19" + sub_seq[0]
            if sub_seq[i] == "月":
                m_pos = i
                sub_seq[i] = ""
                if m_pos - y_pos == 2:
                    sub_seq[m_pos - 1] = "0" + sub_seq[m_pos - 1]
            if sub_seq[i] == "日":
                d_pos = i
                sub_seq[i] = ""
                if d_pos - m_pos == 2:
                    sub_seq[d_pos - 1] = "0" + sub_seq[d_pos - 1]
        sequence = sequence[0:result.start()] + "".join(sub_seq) + sequence[result.end():]
    return sequence


def synonym(sequence: str):
    for key in SYNONYM_MAP.keys():
        if sequence.find(key):
            sequence = sequence.replace(key, SYNONYM_MAP[key])
    return sequence


def QueryPruneBySamePredicate(sequence: str, query: str):
    """
    查找到的query中可能会将谓词识别两遍，需要进行特殊处理
    :return:
    """
    triples = query.split("|||")
    if len(triples) == 1:
        return True
    onehop_triples_ls = triples[0].strip().split("&&&")
    twohop_triples_ls = triples[1].strip().split("&&&")
    onehop_predicate = onehop_triples_ls[1]
    twohop_predicate = twohop_triples_ls[1]
    if onehop_predicate == twohop_predicate and "?" in twohop_triples_ls[0] and "?" in twohop_triples_ls[2]:
        if "同" in sequence:
            return True
        else:
            return False
    return True


def ExamQuery(query):
    qlist = query.strip().split("|||")
    flag = True
    if len(qlist) > 1:
        for triple in qlist:
            ls = triple.split("&&&")
            if ls[1] == "<涉及疾病>" or ls[1] == "<涉及检查>" or ls[1] == "<涉及症状>":
                if "?" in ls[0]:
                    flag &= True
                else:
                    flag &= False
            else:
                return True
    return flag


if __name__ == '__main__':
    res = QueryPruneBySamePredicate("生活如此多娇是哪个公司的口号", "?x&&&<公司口号>&&&生活如此多娇|||?x&&&<公司口号>&&&?y")
    print(res)



