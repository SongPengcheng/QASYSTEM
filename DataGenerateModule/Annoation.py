#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 9:30 上午
# @Author  : SPC
# @FileName: Annoation.py
# @Software: PyCharm
# @Desn    : 

# @Des     : 对CCKS提供的原始数据（question, sparql, answer）进行标注
import sys
import os
o_path = os.getcwd()
sys.path.append(o_path)
import re
import Resource as rs
import pickle
import random
from Rule import punctuation,rawstr
punctuation2 = r"""!"#$%&'()*+,-./:;=@[\]^_`{|}·，。：（）；’‘“”、？《》~ """
rawstr2 = str.maketrans({key: None for key in punctuation2})

def get_max_common_substring(str1, str2):
    """
    获取两个字符串的最大公共子串
    :param str1:
    :param str2:
    :return: str1与str2的最大公共子串
    """
    lstr1 = len(str1)
    lstr2 = len(str2)
    record = [[0 for i in range(lstr2 + 1)] for j in range(lstr1 + 1)]  # 多一位
    maxNum = 0  # 最长匹配长度
    p = 0  # 匹配的起始位

    for i in range(lstr1):
        for j in range(lstr2):
            if str1[i] == str2[j]:
                # 相同则累加
                record[i + 1][j + 1] = record[i][j] + 1
                if record[i + 1][j + 1] > maxNum:
                    # 获取最大匹配长度
                    maxNum = record[i + 1][j + 1]
                    # 记录最大匹配长度的终止位置
                    p = i + 1
    return str1[p - maxNum:p]


def DatasetGenerate(source_file):
    """
    用于处理训练数据，获取每条数据对应的问题，SPARQL语句，答案
    :param source_file: 需要进行处理的文件
    :return: 返回文件中每条数据的问题，查询，答案
    """
    qlist = []
    slist = []
    alist = []
    with open(source_file, "r", encoding="UTF-8") as tfile:
        fr = tfile.readlines()
        flag = 1
        for i, l in enumerate(fr):
            if re.match("q[0-9]*:", l):
                endpos = re.search("q[0-9]*:", l).end()
                question = l[endpos:].strip('\n')
                qlist.append(question)
            elif re.match("select", l) or re.match("SELECT", l):
                slist.append(l)
            elif l == "\n":
                continue
            else:
                alist.append(l)
    return qlist, slist, alist


def getTrainMentionByCommon(qlist, slist, target_file):
    """
    通过sparql语句与问题的最大公共子串进行反向标注
    :param qlist:
    :param slist:
    :param target_file:
    :return:
    """
    ft = open(target_file, "w", encoding="UTF-8")
    for (question, sqal) in zip(qlist, slist):
        question = question.translate(rawstr)
        common = []
        start_pos = sqal.index("{")
        end_pos = sqal.index("}")
        triples = sqal[start_pos + 1:end_pos].split(".")
        for i in range(len(triples) - 1):
            if triples[i] != " ":
                sequence = triples[i]
                if re.search("_（.*）", sequence):
                    s = re.search("_（.*）", sequence).start()
                    e = re.search("_（.*）", sequence).end()
                    sub = sequence[s:e]
                    sequence = sequence.replace(sub, "")
                str = sequence.translate(rawstr2).replace("<", " <").replace(">", "> ").replace("  ", " ").strip()
                items = str.split(" ")
                try:
                    if "?" not in items[0]:
                        common_str = get_max_common_substring(question, items[0].strip("<").strip(">"))
                        common.append(common_str)
                    if "?" not in items[2]:
                        common_str = get_max_common_substring(question, items[2].strip("<").strip(">"))
                        common.append(common_str)
                except:
                    continue
        ft.write("\t".join(common))
        ft.write("\n")
    ft.close()


def getTrainMentionByE2MFromFile(question_file, entity_file, target_file):
    resource = rs.Resource()
    ent2mention_idx_path = resource.e2m_idx_path
    f = open(ent2mention_idx_path, "rb")
    e2m_index = pickle.load(f)
    freader = lambda x: open(x, "r", encoding="UTF-8")
    fwriter = lambda x: open(x, "w", encoding="UTF-8")
    fq = freader(question_file)
    fe = freader(entity_file)
    ft = fwriter(target_file)
    qlines = fq.readlines()
    elines = fe.readlines()
    for qline, eline in zip(qlines, elines):
        question = qline.strip()
        entities = eline.strip().split("|||")
        common = []
        for entity in entities:

            if "<" in entity:
                two_obj_mention_ls = e2m_index[entity.replace("<", "").replace(">", "")]
                for tmp_mention, tmp_popularity in two_obj_mention_ls:
                    if tmp_mention in question:
                        common.append(tmp_mention)
            else:
                mention = entity.strip('"')
                if mention.translate(rawstr).lower() in question:
                    common.append(mention.translate(rawstr).lower())
            common = list(set(common))
            for i in common:
                for j in common:
                    if i in j and i != j:
                        common.remove(i)
                        break
        ft.write("|||".join(common) + "\n")


def getTrainMentionByE2M(qlist, slist, target_file):
    """
    通过构建entity2mention表来进行反向标注
    :param qlist:
    :param slist:
    :param target_file:
    :return:
    """
    resource = rs.Resource()
    ent2mention_idx_path = resource.e2m_idx_path
    with open(ent2mention_idx_path, "rb") as f, open(target_file, "w", encoding="UTF-8") as ft:
        # with open(target_file, "w", encoding="UTF-8") as ft:
        e2m_index = pickle.load(f)
        for (question, sqal) in zip(qlist, slist):
            common = []
            question = question.translate(rawstr).lower()  # 统一问题中英文字母的大小写
            start_pos = sqal.index("{")
            end_pos = sqal.index("}")
            triples = sqal[start_pos + 1:end_pos].split(". ")
            for i in range(len(triples) - 1):
                if triples[i] != " ":
                    sequence = triples[i].strip()
                    if "filter regex" in sequence:
                        start = sequence.find(",") + 1
                        mention = sequence[start:].strip().replace('"', '').replace("'", "").replace("(", "").replace(
                            ")", "").translate(rawstr).lower()
                        if mention in question:
                            common.append(mention)
                    else:
                        items = sequence.split(" ")
                        try:
                            if "?" not in items[0]:
                                if "<" in items[0]:
                                    entity = items[0].strip("<").strip(">")
                                    mention_list = e2m_index.get(entity)
                                    for mention, popularity in mention_list:
                                        if mention.translate(rawstr).lower() in question:
                                            common.append(mention.translate(rawstr).lower())
                                else:
                                    mention = items[0].strip('"')
                                    if mention.translate(rawstr).lower() in question:
                                        common.append(mention.translate(rawstr).lower())
                            if "?" not in items[2]:
                                if "<" in items[2]:
                                    entity = items[2].strip("<").strip(">")
                                    mention_list = e2m_index.get(entity)
                                    for mention, popularity in mention_list:
                                        if mention.translate(rawstr).lower() in question:
                                            common.append(mention.translate(rawstr).lower())
                                else:
                                    mention = items[2].strip('"')
                                    if mention.translate(rawstr).lower() in question:
                                        common.append(mention.translate(rawstr).lower())
                        except:
                            print(question)
            common = list(set(common))
            for i in common:
                for j in common:
                    if i in j and i != j:
                        common.remove(i)
                        break
            ft.write("\t".join(common))
            ft.write("\n")


def DevideData():
    """
    将原始的训练数据拆分成9：1的训练集与验证集
    :return:
    """
    # 加载原始数据文件
    source_file = "data/Task/Train/task1-4_train_2020.txt"
    fs = open(source_file, "r", encoding="UTF-8")
    slines = fs.readlines()
    # 加载训练数据文件
    trainfile = "data/Task/Train/task_train_2020.txt"
    ftrain = open(trainfile, "w", encoding="UTF-8")
    # 加载验证数据文件
    devfile = "data/Task/Dev/task_dev_2020.txt"
    fdev = open(devfile, "w", encoding="UTF-8")
    datalist = []
    tmp = ""
    for i, l in enumerate(slines):
        if l == "\n":
            datalist.append(tmp)
            tmp = ""
        else:
            tmp += l
    rls = random.sample(range(0, 3999), 400)
    for i, string in enumerate(datalist):
        if i in rls:
            fdev.write(string + "\n")
        else:
            ftrain.write(string + "\n")
    fs.close()
    ftrain.close()
    fdev.close()


def NERAnnoation(qfile, mfile, tfile):
    """
    对用于实体识别的数据进行标注
    :param qfile: 问题文件
    :param mfile: 实体提及文件
    :param tfile: 目标文件
    :return:
    """
    fq = open(qfile, "r", encoding="UTF-8")
    qlines = fq.readlines()
    fm = open(mfile, "r", encoding="UTF-8")
    mlines = fm.readlines()
    ft = open(tfile, "w", encoding="UTF-8")
    for i, qline in enumerate(qlines):
        question = qline.strip()
        mlist = mlines[i].strip().split("|||")
        qset = list(question)
        label_list = list("O" * len(qset))
        for j, label_word in enumerate(mlist):
            # print(question,label_word)
            label_word = label_word.lower()
            s = question.index(label_word)
            e = s + len(label_word)
            for k in range(s, e):
                if k == s:
                    label_list[k] = "B-LOC"
                else:
                    label_list[k] = "I-LOC"
        for (word, label) in zip(qset, label_list):
            ft.write(word + " " + label + "\n")
        ft.write("\n")


def NERTestData():
    """
    初始标注TEST数据的NER
    :return:
    """
    resource = rs.Resource()
    sourcefile = resource.test_question_file
    targetfile = resource.test_ner_file
    with open(sourcefile, "r", encoding="UTF-8") as fs, open(targetfile, "w", encoding="UTF-8") as ft:
        qlines = fs.readlines()
        for line in qlines:
            question = line.strip()
            qset = list(question)
            label_list = list("O" * len(qset))
            for (word, label) in zip(qset, label_list):
                ft.write(word + " " + label + "\n")
            ft.write("\n")


def getTrainEntity(sourcefile, targetfile):
    qlist, slist, alist = DatasetGenerate(sourcefile)
    ft = open(targetfile, "w", encoding="UTF-8")
    for (question, sqal) in zip(qlist, slist):
        question = question.translate(rawstr).lower()  # 统一问题中英文字母的大小写
        start_pos = sqal.index("{")
        end_pos = sqal.index("}")
        triples = sqal[start_pos + 1:end_pos].split(". ")
        els = []
        for i in range(len(triples) - 1):
            if triples[i] != " ":
                sequence = triples[i].strip()
                if "filter regex" in sequence:
                    start = sequence.find(",") + 1
                    value = sequence[start:].strip().replace('"', '').replace("'", "").replace("(", "").replace(")",
                                                                                                                "").translate(
                        rawstr).lower()
                    els.append(value)
                else:
                    items = sequence.split(" ")
                    try:
                        if "?" not in items[0]:
                            if "<" in items[0]:
                                entity = items[0]
                            else:
                                entity = items[0].replace('"', "")
                            els.append(entity)
                        if "?" not in items[2]:
                            if "<" in items[2]:
                                entity = items[2]
                            else:
                                entity = items[2].replace('"', "")
                            els.append(entity)
                    except:
                        print(question)
        ft.write("|||".join(els) + "\n")


def getTrainProperty(source_file, target_file):
    qlist, slist, alist = DatasetGenerate(source_file)
    ft = open(target_file, "w", encoding="UTF-8")
    for sqal in slist:
        common = []
        start_pos = sqal.index("{")
        end_pos = sqal.index("}")
        triples = sqal[start_pos + 1:end_pos].split(".")
        for i in range(len(triples) - 1):
            if triples[i] != " ":
                sequence = triples[i].strip().split(" ")
                items = sequence
                try:
                    if "?" not in items[1]:
                        common.append(items[1])
                except:
                    continue
        ft.write("|||".join(common))
        ft.write("\n")


def GetAnswers(sourcefile, targetfile):
    with open(sourcefile, "r", encoding="UTF-8") as fs, open(targetfile, "w", encoding="UTF-8") as ft:
        qlist, slist, alist = DatasetGenerate(sourcefile)
        for line in alist:
            ls = line.strip().split("\t")
            print(ls)
            ft.write("\t".join(ls) + "\n")


def PathAnnoation(source_file, target_file):
    qlist, slist, alist = DatasetGenerate(source_file)
    ft = open(target_file, "w", encoding="UTF-8")
    for (question, sqal) in zip(qlist, slist):
        start_pos = sqal.index("{")
        end_pos = sqal.index("}")
        triples = sqal[start_pos + 1:end_pos].split(".")
        path = []
        for tri in triples:
            if tri != " ":
                sequence = tri.strip()
                items = sequence.split(" ")
                try:
                    predicate = items[1]
                    # path.append(predicate+"("+items[0]+","+items[2]+")")
                    path.append(items[0] + "&&&" + predicate + "&&&" + items[2])
                except:
                    print(question.strip())
        triples_num = len(path)
        # ft.write("|||".join(path)+"\t"+str(triples_num)+"\n")
        ft.write("|||".join(path) + "\n")


def GetSQL(sourcefile, targetfile):
    qlist, slist, alist = DatasetGenerate(sourcefile)
    ft = open(targetfile, "w", encoding="UTF-8")
    for sql in slist:
        ft.write(sql)


if __name__ == '__main__':
    resource = rs.Resource()
    print(resource.dev_entity_4dev_file)
    print(get_max_common_substring("中华人民共和国", "中华民国"))




