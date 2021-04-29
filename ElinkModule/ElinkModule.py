#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 3:09 下午
# @Author  : SPC
# @FileName: ElinkModule.py
# @Software: PyCharm
# @Desn    : 
from Rule import Interrogative_words_dict
from KnowledgeMethodModule.KnowledgeBase import KnowledgeBase
from RankModule.RankModel import RankModel
from MathMethod import jaccard, hint, editDistance
from BertModule.BertModel import BertModel
from Rule import punctuation,rawstr

class ElinkModule(object):
    kb: KnowledgeBase
    End2EndModel: BertModel
    FeatureModel: RankModel
    def __init__(
            self,
            kb: KnowledgeBase=None,
            End2EndModel: BertModel=None,
            FeatureModel: RankModel=None
    ):
        """
        :param kb: 对应的知识库操作对象
        :param mode: 排序模式，为'rank'时提取特征向量进行排序；为'bert'时，进行端到端的排序
        :param keep_num: 对应的知识库操作对象
        """
        super(ElinkModule,self).__init__()
        self.kb = kb
        self.End2EndModel = End2EndModel
        self.FeatureModel = FeatureModel
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
        return entity_list, value_list
    def getEntityFeatures(
            self,
            qid=0,
            label=0,
            question=None,
            mention=None,
            entity=None,
            indegree=0,
            outdegree=0,
            entity_sem_sim=0.0
    )->list:
        """
        :param qid: 问题编号
        :param label: 实际标签，正例是1，负例是0
        :param question: 问题
        :param mention: 实体提及
        :param entity: 实体
        :param indegree: 实体入度
        :param outdegree: 实体出度
        :return: 用于LambdaRank的实体特征
        """
        indegree = indegree / 1000000
        outdegree = outdegree / 1000000
        entity_popularity = indegree + outdegree
        jac_sim = jaccard(question, entity)
        hint_q_sim = hint(question, entity) / len(question)
        hint_e_sim = hint(question, entity) / len(entity)
        edit_sim = editDistance(question, entity)
        graph = self.kb.getGraph4Entity(entity, False)
        one_hop_path_sim = self.kb.ScoreOfOneHopPathOverlap(entity, graph, question, mention)
        two_hop_path_sim = self.kb.ScoreOfTwoHopPathOverlap(entity, graph, question, mention)
        # 12.28新增features
        # mention在问题中的位置
        men_pos = question.find(mention)
        # mention的流行度，即mention所对应的entity数量
        men_popularity = (
            len(self.kb.m2e_index.get(mention)) if self.kb.m2e_index.get(mention) else 0
        )
        # mention距离疑问词的距离，若没有找到对应的疑问词，则以mention到问题末尾的具体作为这一特征
        def FindQuestionWord(question):
            for qword in Interrogative_words_dict:
                if question.find(qword) != -1:
                    return question.find(qword), len(qword)
            return -1, -1
        qword_pos, qword_len = FindQuestionWord(question)
        if qword_pos >= 0:
            men_qword_dis = qword_pos - (men_pos + len(mention)) if men_pos < qword_pos else men_pos - (
                        qword_pos + qword_len)
        else:
            men_qword_dis = len(question) - men_pos - len(mention)
        # mention长度
        men_length = len(mention)
        features = [qid, label, indegree, outdegree, entity_popularity, jac_sim, hint_q_sim, hint_e_sim,
                    edit_sim, entity_sem_sim, one_hop_path_sim, two_hop_path_sim,
                    men_pos, men_popularity, men_qword_dis, men_length]
        return features
    def getEntitySequence(self, entity):
        graph = self.kb.getGraph4Entity(entity, True)
        onehop_relations = self.kb.getOneHopPredicates(graph, entity)
        sequence = entity.translate(rawstr)
        for relation in onehop_relations:
            sequence += relation.translate(rawstr)
        return sequence
    def RankEntityByFeatures(self,features:list)->list:
        """
        :param features: 是由多个list构成的二维list，其中每个子list代表一个entity对应的特征向量
        :return: 得分list，二维list，形状与features相同
        """
        score = self.FeatureModel.ScoreByModel(features)
        return score
    def RankEntityByEnd2End(self,question_entity_pairs)->list:
        """
        :param question_entity_pairs: 是由多个tuple构成的list，其中每个子tupel代表一个文本对
        :return: 得分list，二维list
        """
        score = self.End2EndModel.ScoreByModel(question_entity_pairs)
        return score
