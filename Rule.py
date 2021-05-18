#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/7/3 9:23 下午
# @Author  : SPC
# @FileName: Rule.py
# @Software: PyCharm
# @Des     ：用于制定相关的规则

import re
SYNONYM_MAP = {
    '持股': '持股比例',
    '多少股份': '持股比例',
    '是哪国人': '国籍',
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
    '外号': '别名别称',
    '英文': '外文，英文',
    '西班牙语': '外文，西班牙语',
    '贡献': '贡献，主要成就',
    '功绩': '功绩，主要成就',
    '丰功伟绩': '丰功伟绩，主要成就',
    '来源': '来源，出处',
    '在金庸小说《天龙八部》中': '',
    '谁写的':'作者',
    '谁拍的':'导演',
    '年纪':'年纪，年龄，岁数',
    '岁数':'年纪，年龄，岁数',
    '是中药还是西药':'类型',
    '指的是':'原指本名',
    '可交易品种':'上市品种'
}
Interrogative_words_dict =[
    "为什么","怎么样","怎么着",
    "怎么","怎的","怎样","如何","哪些","哪里","哪儿","什么","几时","多少",
    "谁","何","几","怎","哪"
]
def ChangeDataForm(sequence:str):
    """
    将问题中的年月日统一形式
    :param sequence:
    :return:
    """
    time_pattern = re.compile("(\d{2,4}年\d{1,2}月\d{1,2}日|\d{2,4}年\d{1,2}月|\d{1,2}月\d{1,2}日)")
    result = re.search(time_pattern,sequence)
    if result:
        sub_seq = list(sequence[result.start():result.end()])
        y_pos = -1
        for i in range(len(sub_seq)):
            if sub_seq[i]=="年":
                y_pos = i
                sub_seq[i] = ""
                if y_pos == 2:
                    year = int(sub_seq[0]+sub_seq[1])
                    if year < 20:
                        sub_seq[0] = "20"+sub_seq[0]
                    else:
                        sub_seq[0] = "19" + sub_seq[0]
            if sub_seq[i]=="月":
                m_pos = i
                sub_seq[i] = ""
                if m_pos - y_pos == 2:
                    sub_seq[m_pos-1] = "0" + sub_seq[m_pos-1]
            if sub_seq[i]=="日":
                d_pos = i
                sub_seq[i] = ""
                if d_pos - m_pos == 2:
                    sub_seq[d_pos - 1] = "0" + sub_seq[d_pos - 1]
        sequence = sequence[0:result.start()]+"".join(sub_seq)+sequence[result.end():]
    return sequence
def synonym(sequence:str):
    for key in SYNONYM_MAP.keys():
        if sequence.find(key):
            sequence = sequence.replace(key,SYNONYM_MAP[key])
    return sequence


def QueryPruneStrategy(sequence:str,query:str):

    def QueryPruneBySamePredicate():
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
        if onehop_predicate==twohop_predicate and "?" in twohop_triples_ls[0] and "?" in twohop_triples_ls[2]:
            if "同" in sequence:
                return True
            else:
                return False
        return True

    def ExamQuery():
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

    def ExamMedicineType():
        restr = "(属于|是)什么药"
        pattern = re.compile(restr)
        result = re.search(pattern,sequence)
        if result:
            if "<药品类型>" in query:
                return False
        return True

    def ExamThreehopQuery():
        triples = query.strip().split("|||")
        if len(triples) < 3:
            return True
        triple = triples[2]
        sub,pre,obj = triple.split("&&&")
        if "?" in sub and "?" in obj:
            predicate = pre.strip("<").strip(">")
            restr = "哪(.*)"+predicate
            pattern = re.compile(restr)
            result = re.search(pattern,sequence)
            if result:
                return False
            return True

    result_flag = QueryPruneBySamePredicate() and ExamQuery() and ExamMedicineType() and ExamThreehopQuery()
    return result_flag

if __name__ == '__main__':
    resule = QueryPruneStrategy('思想自由兼容并包是哪个学校的学术传统','?x&&&<学术传统>&&&思想自由|||?x&&&<学术传统>&&&"兼容并包"|||?y&&&<学校>&&&?x')
    print(resule)
