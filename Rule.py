#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 9:27 上午
# @Author  : SPC
# @FileName: Rule.py
# @Software: PyCharm
# @Des     : 用于制定相关的规则

import re
#同义词词典
SYNONYM_MAP = {
    '丈夫': '丈夫，老公，配偶',
    '老公': '丈夫，老公，配偶',
    '妻子': '老婆，夫人，妻子，配偶',
    '夫人': '老婆，夫人，妻子，配偶',
    '媳妇': '老婆，夫人，妻子，配偶',
    '老婆': '老婆，夫人，妻子，配偶',
    '老家': '故乡，籍贯，出生地，老家',
    '故乡': '故乡，籍贯，出生地，老家',
    '家乡': '故乡，籍贯，出生地，老家',
    '哪里人': '故乡，籍贯，出生地，老家',
    '本名': '本名，原名，中文名，别名',
    '原名': '本名，原名，中文名，别名',
    '英文': '外文，英文',
    '西班牙语': '外文，西班牙语',
    '贡献': '贡献，主要成就',
    '功绩': '功绩，主要成就',
    '丰功伟绩': '丰功伟绩，主要成就',
    '来源': '来源，出处',
    '在金庸小说《天龙八部》中': '',
    '谁写的':'作者',
    '谁拍的':'导演',
    '朝代':'国籍',
    '作者':'代表作品',
    '年纪':'年纪，年龄，岁数',
    '岁数':'年纪，年龄，岁数'
}
#疑问词列表
Interrogative_words_dict =[
    "为什么","怎么样","怎么着",
    "怎么","怎的","怎样","如何","哪些","哪里","哪儿","什么","几时","多少",
    "谁","何","几","怎","哪"
]
placeholder = ["哪些", "哪个", "哪年", "哪里", "哪所", "哪一年", "哪种", "哪一个", \
               "是谁", "谁是", "是什么", "是多少", "是哪", \
               "什么时候", "叫什么", "于什么", "什么",
               "何时", \
               "怎么样", \
               "由谁", \
               "有怎样的", "有多", "有什么", "多少", \
               "为", "在", "哪", "是", "有", "的"]
#停用词列表
entity_stop = ["多少", "是什么", "是谁的", "是谁", "何时", "什么", "哪个", "个时", "中的", "有什么", "有哪些", "哪里", "那些", "《", "》", '"q60"', \
               '告诉我', '那位', '那里', '请问', '请推荐', '向我推荐', '请列举', '列举', '生活中', '请给出', '给出', '请列出', '列出', '你知道', \
               '我想', '给我一些', '给我', '现在都有', '我想看', '你们', '我们', '它们', '他们', '我国', '你', '我', '它', '他', '共同', \
               '做出了', '应该', '如果', '会在', '一共', '总共', '从', '看上去', '归类为', '记得', '一员', '历史上', '听说', \
               "多少", "是什么", "是谁的", "是谁", "何时", "什么", "哪个", "个时", "中的", "有什么", "有哪些", \
               "哪里", "那里", "大学", "作者", "毕业", "来自", "电影", "的", "你读过", "你知道", "游戏", \
               "站点", "网站", "就是", '时候', '生人', '那个', "在哪", "国家", '以及', '各自', "了", "大", "他的", \
               "家的", "知道", "国家的", "我们", "你们", "民族", "有", "出", "著", \
               "它", "是"]  # 作家

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



