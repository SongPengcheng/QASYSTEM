#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/5/6 9:11 上午
# @Author  : SPC
# @FileName: Lattice.py
# @Software: PyCharm
# @Desn    : 
import jieba
def segment(sequence):
    print("/".join(jieba.lcut(sequence)))  # 精简模式，返回一个列表类型的结果
    #print("/".join(jieba.lcut(sequence, cut_all=True)))  # 全模式，使用 'cut_all=True' 指定
    #print("/".join(jieba.lcut_for_search(sequence)))  # 搜索引擎模式
    ls = jieba.lcut(sequence)
    ans = []
    for idx, seg in enumerate(ls):
        if idx == 0:
            ans.append((seg,0))
        else:
            ans.append((seg,ans[idx-1][1]+len(ls[idx-1])))
    print(ans)
segment("商朝在哪场战役中走向覆灭")


"""fs = open("data/Task/Dev/dev_questions.txt","r",encoding="UTF-8")
for line in fs.readlines():
    segment(line.strip())"""
def fun(seg_list:list,men_list:list,sequence:str):
    new_list = []
    for mention, m_start_pos in men_list:
        m_end_pos = m_start_pos + len(mention) - 1
        for segment, s_start_pos in seg_list:
            s_end_pos = s_start_pos + len(segment) - 1
            if s_end_pos < m_start_pos:
                new_list.append((segment,s_start_pos))
                continue
            if s_start_pos > m_end_pos:
                new_list.append((segment,s_start_pos))
                continue
            if s_start_pos > m_start_pos and s_end_pos < m_end_pos:
                continue
            if s_start_pos <= m_start_pos and s_end_pos >= s_start_pos:
                if s_start_pos < m_start_pos:
                    new_list.append((sequence[s_start_pos:m_start_pos], s_start_pos))
            if s_start_pos <= m_end_pos and s_end_pos >= m_end_pos:
                if s_end_pos > m_end_pos:
                    new_list.append((sequence[m_end_pos+1:s_end_pos+1], m_end_pos+1))
        new_list.append((mention,m_start_pos))
    return new_list

seg_list = [("请问",0),("流行性",2),("感冒",5),("有",7),("哪些",8),("症状",10)]
mention_list = [("行性感冒有哪",3)]
ans = fun(seg_list,mention_list,"请问流行性感冒有哪些症状")
ans = sorted(ans,key=lambda x:x[1],reverse=False)
print(ans)