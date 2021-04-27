#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/26 9:20 上午
# @Author  : SPC
# @FileName: SearchQuery.py
# @Software: PyCharm
# @Desn    : 定义查询图类

class SearchQuery(object):
    def __init__(self,query,path,entity_score,predicate_list,mention_list,enum,ans):
        self.query = query
        self.path = path
        self.escore = entity_score
        self.plist = predicate_list
        self.mlist = mention_list#用来记录问题中出现的全部实体的mention，在后续属性映射时，可以用来mask掉实体
        self.pscore = 0
        self.enum = enum
        self.ans = ans
        self.pr_score = 0
        self.state = 0

class PathInfo(object):
    def __init__(
            self,
            root_entity:str=None,
            root_mention:str=None,
            tail_entity:str=None,
            tail_mention:str=None,
            conjunction:str=None,
            onehop_predicate:str=None,
            twohop_predicate:str=None
    ):
        """
        专门用来存储双实体双跳路径信息的对象。目的是为了辅助扩展三跳路径。
        :param root_entity: 根实体
        :param root_mention: 根实体指称
        :param tail_entity: 尾实体
        :param tail_mention: 尾实体指称
        :param conjuction: 连接实体，即需要在这个节点上尝试扩展三跳路径
        """
        self.root_entity = root_entity
        self.root_mention = root_mention
        self.tail_entity = tail_entity
        self.tail_mention = tail_mention
        self.conjunction = conjunction
        self.onehop_predicate = onehop_predicate
        self.twohop_predicate = twohop_predicate

class Node(object):
    def __init__(
            self,
            entity: str = None,
            mention: str = None,
            entity_score: float = 0
    ):
        """
        :param entity: 实体
        :param mention: 实体对应的指称
        :param entity_score: 实体在实体链接环节的得分
        """
        self.entity = entity
        self.mention = mention
        self.entity_score = entity_score

class Path(object):
    def __init__(
            self,
            root:Node=None,
            predicate:str=None,
            tail:Node=None,
            query_sequence:str=None,
            path_sequence:str=None
    ):
        """
        :param root: 三元组头实体
        :param predicate: 三元组谓词
        :param tail: 三元组尾实体
        :param query: 三元组对应的查询
        :param path: 三元组构成的路径
        """
        self.root = root
        self.predicate = predicate
        self.tail = tail
        self.query_sequence = query_sequence
        self.path_sequence = path_sequence
        self.predicate_score = 0

class QueryPath(object):
    onehop_path: Path = None
    twohop_path: Path = None
    threehop_path: Path = None
    ans: set = None
    query_sequence: str = None
    path_sequence: str = None
    entity_score: float = 0.0
    predicate_score: float = 0.0
    path_score: float = 0.0
    trans_state:int = 0
    def __init__(
            self,
            onehop_path:Path=None,
            twohop_path:Path=None,
            threehop_path:Path=None,
            ans:set=None,
    ):
        self.onehop_path = onehop_path
        self.twohop_path = twohop_path
        self.threehop_path = threehop_path
        self.ans = ans
        self.query_sequence, self.path_sequence = self.GenerateSequence()
        self.entity_score = self

    def GenerateSequence(self)->(str, str):
        query_sequence = ""
        path_sequence = ""
        for path in [self.onehop_path, self.twohop_path, self.threehop_path]:
            if path:
                query_sequence += path.query_sequence
                path_sequence += path.path_sequence
        return query_sequence, path_sequence

    def GenerateEntityScore(self)->float:
        score = 0.0
        for path in [self.onehop_path, self.twohop_path, self.threehop_path]:
            for node in [path.root, path.tail]:
                if node:
                    score += node.entity_score
        return score

    def GeneratePredicateScore(self)->float:
        score = 0.0

        return score


