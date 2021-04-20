#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 10:26 上午
# @Author  : SPC
# @FileName: MathMethod.py
# @Software: PyCharm
# @Desn    : 定义相关的基础数学方法

import Levenshtein

def jaccard(seqa, seqb):
    """
    :param seqa:
    :param seqb:
    :return: 计算seqa和seqb的jaccard相似度作为字面相似度
    """
    seqa = set(list(seqa.upper()))
    seqb = set(list(seqb.upper()))
    aa = seqa.intersection(seqb)
    bb = seqa.union(seqb)
    # return (len(aa)-1)/len(bb)
    return len(aa) / len(bb)

def hint(seqa, seqb):
    """
    :param seqa:
    :param seqb:
    :return: 计算seqa和seqb交集的长度
    """
    seqa = set(list(seqa.upper()))
    seqb = set(list(seqb.upper()))
    aa = seqa.intersection(seqb)
    return len(aa)

def editDistance(seqa, seqb):
    """
    :param seqa:
    :param seqb:
    :return: 计算seqa和seqb的编辑距离
    """
    return Levenshtein.ratio(seqa, seqb)


