#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 3:09 下午
# @Author  : SPC
# @FileName: ElinkModule.py
# @Software: PyCharm
# @Desn    : 

from KnowledgeMethodModule.KnowledgeBase import KnowledgeBase
class ElinkModule(object):
    def __init__(
            self,
            kb:KnowledgeBase=None,
            mode:str=None,
            keep_num:int=4
    ):
        """
        :param kb: 对应的知识库操作对象
        :param mode: 排序模式，为'rank'时提取特征向量进行排序；为'bert'时，进行端到端的排序
        :param keep_num: 对应的知识库操作对象
        """
        super(ElinkModule,self).__init__()
        self.kb = kb

    def getEntityFromMention(
            self,
            qid:int=0,
            mention:str=None
    )->(list,list):
        """
        :param qid: 问题编号
        :param mention: 实体提及，是一个词
        :return:根据实体识别得到的mention来从知识库中抽取候选实体[qid,mention,entity,outdegree,indegree]
        """
        entity_list = {}
        value_list = {}
        entities = self.kb.m2e_index[mention]
        print(entities)
        if entities:
            for entity in entities:
                if "<" in entity and ">" in entity:
                    entity_list[entity] = []
                    entity_list[entity].append(qid)
                    entity_list[entity].append(mention)
                    entity_list[entity].append(entity)
                    # entity_list[entity].append(popularity)
                    entity_list[entity].append(self.kb.count_by_name(entity))  # 出度
                    entity_list[entity].append(self.kb.count_by_v2e_name(entity))  # 入度
        value = mention
        if value in self.kb.v2e_idx_dict.keys():
            value_list[value] = []
            value_list[value].append(qid)
            value_list[value].append(mention)
            value_list[value].append(value)
            # value_list[value].append("1")
            value_list[value].append(0)  # 出度
            value_list[value].append(self.kb.count_by_v2e_name(value))  # 入度
        # 由于知识库对于一些医疗领域的实体没有给出对应的mention，所以要特殊处理一步
        """test_entity = "<"+mention+">"
        if test_entity not in entity_list.keys():
            try:
                entity_list[test_entity] = []
                entity_list[test_entity].append(qid)
                entity_list[test_entity].append(mention)
                entity_list[test_entity].append(test_entity)
                #entity_list[test_entity].append("1")
                entity_list[test_entity].append(kb.count_by_name(test_entity))  # 出度
                entity_list[test_entity].append(kb.count_by_v2e_name(test_entity))  # 入度
            except:
                pass"""
        return entity_list, value_list