#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 10:02 上午
# @Author  : SPC
# @FileName: NerMethod.py
# @Software: PyCharm
# @Desn    : 定义关于实体识别的相关方法
import re
from Rule import entity_stop

def getPossibleMentions(sequence, max_str):
    """
    :param sequence: 要进行匹配的句子
    :param max_str: 标记位，在暴力匹配的过程中，对存在包含关系的mentions是否只保留最长的一个
    :return: 通过硬匹配的方式获取所有可能的实体mention
    """
    mentions = []
    for i in range(len(sequence)):
        for j in range(i + 2, len(sequence) + 1):
            if sequence[i:j] in entity_stop:
                continue
            key = sequence[i:j]
            out = m2e_index[key]
            if out:
                mentions.append(key)
    if max_str:
        for i in mentions:
            for j in mentions:
                if i in j and i != j:
                    mentions.remove(i)
                    break
    return mentions

def getPossibleValues(sequence, max_str):
    """
    :param sequence: 要进行匹配的句子
    :param max_str: 标记位，在暴力匹配的过程中，对存在包含关系的values是否只保留最长的一个
    :return: 通过硬匹配的方式获取所有可能的属性值value
    """
    values = []
    for i in range(len(sequence)):
        for j in range(i + 2, len(sequence) + 1):
            if sequence[i:j] in entity_stop:
                continue
            key = sequence[i:j]
            if key in kb.v2e_idx_dict:
                values.append(sequence[i:j])
    if max_str:
        for i in values:
            for j in values:
                if i in j and i != j:
                    values.remove(i)
                    break
    return values

def getMentionFromHardMatch(sequence, flag):
    """
    :param sequence: 要进行硬匹配的问句
    :param flag: 标记位，bool值，是否只保留最长
    :return: 问句中所有可能的mention，value
    """
    mentions = getPossibleMentions(sequence, flag)
    values = getPossibleValues(sequence, flag)
    ans = list(set(mentions + values))
    return ans

def getMentionFromRules(sequence):
    """
    :param sequence: 要处理的问句
    :return: 根据规则进行实体识别的结果
    """
    rule1 = "《.*》"
    rule2 = '".*"'
    mlist = []
    question = sequence
    if "《" in question:
        startpos = re.search(rule1, question).start()
        endpos = re.search(rule1, question).end()
        mention = question[startpos + 1:endpos - 1]
        mlist.append(mention.translate(rawstr).lower())
    if '"' in question:
        startpos = re.search(rule2, question).start()
        endpos = re.search(rule2, question).end()
        mention = question[startpos + 1: endpos - 1]
        mlist.append(mention.translate(rawstr).lower())
    return mlist

def getMentionFromM2E(sequence):
    """
    :param sequence: 处理过的问题序列
    :return: 通过在mention2entity字典的全部key中检索与问题相关度最高的三个作为候选mention
    """

    max_match_key_ls = []
    for key in m2e_index.keys():
        score = jaccard(sequence, key)
        if len(max_match_key_ls) < 3:
            max_match_key_ls.append((key, score))
        else:
            min_item = min(max_match_key_ls, key=lambda x: x[1])
            if score > min_item[1]:
                max_match_key_ls.remove(min_item)
                max_match_key_ls.append((key, score))
    return max_match_key_ls

def CombineNerResult(bert_ner_list, search_ner_list, rule_ner_list):
    """
    :param bert_ner_list: 通过bert模型进行实体识别的结果
    :param search_ner_list: 通过硬匹配进行实体识别的结果
    :param rule_ner_list: 通过规则匹配进行实体识别的结果
    :return: 三种方式融合后实体识别的结果
    """
    ans = []
    for bert_ner in bert_ner_list:
        bert_ner = bert_ner.lower()
        if bert_ner in search_ner_list or len(bert_ner) == 1:
            ans.append(bert_ner)
        else:
            sim_word = []
            for search_ner in search_ner_list:
                sim = Levenshtein.ratio(bert_ner, search_ner)
                sim_word.append((search_ner, sim))
            sim_word = sorted(sim_word, key=lambda x: x[1], reverse=True)
            last_sim = sim_word[0][1]
            for word, sim in sim_word:
                if sim == last_sim:
                    ans.append(word)
                    tmp_word = bert_ner.replace(sim_word[0][0], "")
                    if tmp_word in search_ner_list:
                        ans.append(tmp_word)
    tmp = []
    for mentionans in ans:
        for searchmention in search_ner_list:
            if mentionans in searchmention:
                tmp.append(searchmention)
            # if searchmention.find(mentionans) == 0 or (searchmention.find(mentionans)+len(mentionans)) == len(searchmention):
            #    if searchmention.replace(mentionans,"") in search_ner_list:
            #        tmp.append(searchmention.replace(mentionans,""))
    ans.extend(tmp)
    for mentionans in ans:
        for string in replace_set:
            if re.match(string, mentionans):
                ans.append(mentionans.replace("检查", ""))
                break
        for string in re_set:
            if re.match(string, mentionans):
                ans.remove(mentionans)
                break

    if rule_ner_list:
        ans.extend(rule_ner_list)
    if not ans:
        ans = search_ner_list
    return ans


