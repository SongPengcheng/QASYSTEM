#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/25 10:27 上午
# @Author  : SPC
# @FileName: PathGenerate.py
# @Software: PyCharm
# @Desn    : 在进行问答时，为问题生成候选查询路径集合
import copy
from KnowledgeMethodModule.KnowledgeBase import KnowledgeBase
from PathGenerateModule.SearchQuery import Node, Path, QueryPath, PathInfo
from MathMethod import jaccard, hint, editDistance
from collections import defaultdict
punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}·，。：（）；’‘“”、？《》~ """
rawstr = str.maketrans({key: None for key in punctuation})

class PathGenerateModule(object):
    def __init__(
            self,
            knowledgebase:KnowledgeBase=None,
            entityinfos:list=None,
            question:str=None
    ):
        self.kb = knowledgebase
        self.entities = []
        self.ementions = defaultdict(str)
        self.escores = defaultdict(float)
        for c_entity in entityinfos:
            self.entities.append(c_entity.entity)
            self.ementions[c_entity.entity] = c_entity.mention
            self.escores[c_entity.entity] = c_entity.score
        self.question = question

    def MentionFilter(self, mention: str=None, question: str=None)->bool:
        return False

    def Filter4TwohopTwoEntity(
            self,
            entity: str=None,
            entity_mention: str=None,
            root: str=None,
            root_mention: str=None,
            predicate: str=None,
            root_predicate: str=None,
            question: str=None
    ):
        """
        :param entity: 待扩展的第二跳路径上的实体
        :param entity_mention: 待扩展的第二跳路径上的实体对应的指称
        :param root: 第一跳路径上的实体
        :param root_mention: 第一跳路径上的实体对应的指称
        :param predicate: 待扩展的第二跳路径上的谓词
        :param root_predicate: 第一跳路径上的谓词
        :param question: 对应的问题
        :return: bool值，对应着是否保留扩展结果
        """
        # 实体是否为实体链接环节的结果之一
        entity_flag = (entity in self.entities)
        # 实体非实体链接环节的结果，但实体的指称与问题高度重合
        mention_flag = self.MentionFilter(entity_mention, question)
        # 防止两跳路径一致
        path_flag = (entity == root and predicate == root_predicate)
        # 防止两跳实体的对应指称高度相似
        path_mention_flag = (
                (entity == root) or
                (entity_mention == root_mention) or
                (entity_mention in root_mention) or
                (root_mention in entity_mention)
        )
        # 防止出现相应的不常见谓词
        predicate_flag = (predicate != "<类型>")
        flag = (entity_flag or mention_flag) and not path_flag and not path_mention_flag and not predicate_flag
        return flag

    def Filter4ThreehopThreeEntity(
            self,
            entity: str=None,
            entity_mention: str=None,
            predicate: str=None,
            root_mention: str=None,
            tail_mention: str=None,
            question: str=None
    ):
        """
        :param entity: 待扩展的第三跳路径上的实体
        :param entity_mention:
        :param root_mention:
        :param tail_mention:
        :param question:
        :return:
        """
        entity_flag = (entity in self.entities)
        mention_flag = self.MentionFilter(entity_mention, question)
        path_mention_flag = (entity_mention not in root_mention and entity_mention not in tail_mention)
        predicate_flag = predicate != "<类型>"
        flag = entity_flag and mention_flag and path_mention_flag and predicate_flag

        return flag

    def getMention4Entity(self, entity:str=None)->str:
        mention = entity.translate(rawstr)
        if "<" in entity:
            mention_ls = self.kb.e2m_index[entity.replace("<", "").replace(">", "")]
            for tmp_mention, tmp_popularity in mention_ls:
                if tmp_mention in self.question:
                    mention = tmp_mention
                    break
        return mention

    def GetQuerysByTriples(self, all_triples, root):
        """
        :param all_triples: 所有的三元组组合,是一个二维列表
        :param root: 根节点实体，也就是需要当前的查询实体
        :param entities: 候选的邻居实体
        :param question: 问题，用于实现剪枝，剪枝策略：第二跳的谓词如果与问题没有交集则去掉
        :return: 无重复的候选查询路径
        """
        qdict = defaultdict(QueryPath)
        """
        为了保证不出现重复的情况，用一个字典结构记录查询图，键为"查询"，值为QueryPath对象
        """
        for triples in all_triples:
            if len(triples) == 1:
                querys = self.GetOneHopQueryPath(triples)
            if len(triples) == 2:
                querys = self.GetTwoHopQueryPath(triples)
            if querys:
                for q in querys:
                    if q.query_sequence not in qdict.keys():
                        qdict[q.query_sequence] = q
                    else:
                        for answer in q.ans:
                            qdict[q.query_sequence].ans.add(answer)
        return qdict

    def GetOneHopQueryPath(self, triples:list, root:str)->[QueryPath]:
        triple = triples[0]
        sub = triple[0]
        predicate = triple[1]
        obj = triple[2]
        score = self.escores[root]
        mention = self.ementions[root]
        node = Node(entity=root, mention=mention, entity_score=score)
        if root == sub:
            onehop_query = sub + "&&&" + predicate + "&&&?x"
            onehop_path = mention + predicate.replace("<", "").replace(">", "")
            path = Path(
                root=node,
                predicate=predicate,
                query_sequence=onehop_query,
                path_sequence=onehop_path
            )
            answer = obj
        elif root == obj:
            onehop_query = "?x&&&" + predicate + "&&&" + obj
            onehop_path = predicate.replace("<", "").replace(">", "") + mention
            path = Path(
                tail=node,
                predicate=predicate,
                query_sequence=onehop_query,
                path_sequence=onehop_path
            )
            answer = sub
        sq = QueryPath(
            onehop_path=path,
            ans={answer}
        )
        return [sq]

    def GetTwoHopQueryPath(self, triples:list, root:str):
        """
        :param triples: 所有与主题实体相关的三元组[(s,p,o),(s,p,o)]
        :return:
        """
        final_querys = []
        onehop_triple = triples[0]
        twohop_triple = triples[1]
        """
        首先扩展出一跳路径
        """
        onehop_sub = onehop_triple[0]
        onehop_predicate = onehop_triple[1]
        onehop_obj = onehop_triple[2]
        root_mention = self.ementions[root]
        root_score = self.escores[root]
        onehop_node = Node(
            entity=root,
            mention=root_mention,
            entity_score=root_score
        )
        if root == onehop_sub:
            conjunction = onehop_obj
            onehop_query_sequence = onehop_sub + "&&&" + onehop_predicate + "&&&?x"
            onehop_path_sequence = root_mention + onehop_predicate.replace("<", "").replace(">", "")
            onehop_path = Path(
                root=onehop_node,
                predicate=onehop_predicate,
                query_sequence=onehop_query_sequence,
                path_sequence=onehop_path_sequence
            )
        else:
            conjunction = onehop_sub
            onehop_query_sequence = "?x&&&" + onehop_predicate + "&&&" + onehop_obj
            onehop_path_sequence = onehop_predicate.replace("<", "").replace(">", "") + root_mention
            onehop_path = Path(
                tail=onehop_node,
                predicate=onehop_predicate,
                query_sequence=onehop_query_sequence,
                path_sequence=onehop_path_sequence
            )
        """
        然后在conjuction上扩展出二跳路径
        """
        twohop_sub = twohop_triple[0]
        twohop_predicate = twohop_triple[1]
        twohop_obj = twohop_triple[2]
        """
        对路径的结构进行判断，判断依据是链接实体在第二跳三元组中的位置
        """
        if conjunction == twohop_sub:
            # 获取两跳路径上实体的mention
            twohop_obj_mention = self.getMention4Entity(twohop_obj)
            """
            首先保留全部的单实体多跳路径
            """
            # 根据二跳谓词做一次剪枝
            if hint(self.question, twohop_predicate) != 0:
                twohop_query_sequence = "?x&&&" + twohop_predicate + "&&&?y"
                twohop_path_sequence = twohop_predicate.replace("<", "").replace(">", "")
                twohop_path = Path(
                    predicate=twohop_predicate,
                    query_sequence=twohop_query_sequence,
                    path_sequence=twohop_path_sequence
                )
                sq = QueryPath(
                    onehop_path=onehop_path,
                    twohop_path=twohop_path,
                    ans={twohop_obj}
                )
                final_querys.append(sq)
            """
            进而生成多实体多跳的情况
            """
            if self.Filter4TwohopTwoEntity(
                    twohop_obj,
                    twohop_obj_mention,
                    root,
                    root_mention,
                    twohop_predicate,
                    onehop_predicate,
                    self.question
            ):
                if twohop_obj in self.entities:
                    twohop_obj_mention = self.ementions[twohop_obj]
                    twohop_entity_score = self.escores[twohop_obj]
                else:
                    twohop_entity_score = root_score
                twohop_node = Node(
                    entity=twohop_obj,
                    mention=twohop_obj_mention,
                    entity_score=twohop_entity_score
                )
                twohop_query_sequence = "?x&&&" + twohop_predicate + "&&&" + twohop_obj
                twohop_path_sequence = twohop_predicate.replace("<", "").replace(">", "") + twohop_mention
                twohop_path = Path(
                    tail=twohop_node,
                    predicate=twohop_predicate,
                    query_sequence=twohop_query_sequence,
                    path_sequence=twohop_path_sequence
                )
                sq = QueryPath(
                    onehop_path=onehop_path,
                    twohop_path=twohop_path,
                    ans={conjunction}
                )
                final_querys.append(sq)
                self.GetThreeHopQueryPath(sq, final_querys)
        else:
            # 获取两跳路径上实体的mention
            twohop_sub_mention = self.getMention4Entity(twohop_sub)
            """
            首先保留全部的单实体多跳路径
            """
            if hint(self.question, twohop_predicate) != 0:
                twohop_query_sequence = "?y&&&" + twohop_predicate + "&&&?x"
                twohop_path_sequence = twohop_predicate.replace("<", "").replace(">", "")
                twohop_path = Path(
                    predicate=twohop_predicate,
                    query_sequence=twohop_query_sequence,
                    path_sequence=twohop_path_sequence
                )
                sq = QueryPath(
                    onehop_path=onehop_path,
                    twohop_path=twohop_path,
                    ans={twohop_sub}
                )
                final_querys.append(sq)
            """
            进而生成多实体多跳的情况
            """
            if self.Filter4TwohopTwoEntity(
                    twohop_sub,
                    twohop_sub_mention,
                    root,
                    root_mention,
                    twohop_predicate,
                    onehop_predicate,
                    self.question
            ):
                if twohop_sub in self.entities:
                    twohop_sub_mention = self.ementions[twohop_sub]
                    twohop_entity_score = self.escores[twohop_sub]
                else:
                    twohop_entity_score = root_score
                twohop_query_sequence = twohop_sub + "&&&" + twohop_predicate + "&&&?x"
                twohop_path_sequence = twohop_sub_mention + twohop_predicate.replace("<", "").replace(">", "")
                twohop_node = Node(
                    entity=twohop_sub,
                    mention=twohop_sub_mention,
                    entity_score=twohop_entity_score
                )
                twohop_path = Path(
                    root=twohop_node,
                    predicate=twohop_predicate,
                    query_sequence=twohop_query_sequence,
                    path_sequence=twohop_path_sequence
                )
                sq = QueryPath(
                    onehop_path=onehop_path,
                    twohop_path=twohop_path,
                    ans={conjunction}
                )
                final_querys.append(sq)
                self.GetThreeHopQueryPath(sq, final_querys)

        return final_querys

    def GetThreeHopQueryPath(self, sq: QueryPath=None, final_querys: list=None):
        """
        用于对两实体两跳路径进行扩展，在中间连接实体上扩展出第三跳
        :param sq: 记录查询路径信息
        :param final_querys: 存储全部候选查询路径
        :param pinfo: 记录路径中的实体信息
        :return: 增加三跳路径的final_querys
        """
        # 找到前两跳路径上的节点
        onehop_node = sq.onehop_path.root if sq.onehop_path.root else sq.onehop_path.tail
        twohop_node = sq.twohop_path.root if sq.twohop_path.root else sq.twohop_path.tail
        conjunction = sq.ans[0]
        cur_question = self.question.replace(onehop_node.mention, "").replace(twohop_node.mention, "")
        c_graph = self.kb.getGraph4Entity(conjunction,True)
        neighbours = set([y for x, y in c_graph.out_edges(conjunction)] + [x for x, y in c_graph.in_edges(conjunction)]) - set([onehop_node.entity, twohop_node.entity, conjunction])
        for neighbour in neighbours:
            try:
                threehop_predicate = c_graph.edges[conjunction, neighbour]["prop"][0]
                # 先生成两实体三体路径：
                if hint(threehop_predicate,cur_question)!=0 \
                        and threehop_predicate != sq.onehop_path.predicate \
                        and threehop_predicate != sq.twohop_path.predicate:
                    threehop_query_sequence = "?x&&&" + threehop_predicate + "&&&?y"
                    threehop_path_sequence = threehop_predicate.replace("<", "").replace(">", "")
                    threehop_path = Path(
                        predicate=threehop_predicate,
                        query_sequence=threehop_query_sequence,
                        path_sequence=threehop_path_sequence
                    )
                    new_sq = copy.copy(sq)
                    new_sq.threehop_path = threehop_path
                    new_sq.entity_score = new_sq.GenerateEntityScore()
                    new_sq.query_sequence, new_sq.path_sequence = new_sq.GenerateSequence()
                    new_sq.ans = {neighbour}
                    final_querys.append(new_sq)

                # 接下来扩展三实体三跳路径
                threehop_entity_mention = self.getMention4Entity(neighbour)
                if self.Filter4ThreehopThreeEntity(
                        neighbour,
                        threehop_entity_mention,
                        threehop_predicate,
                        onehop_node.mention,
                        twohop_node.mention,
                        cur_question
                ):
                    threehop_query_sequence = "?x&&&" + threehop_predicate + "&&&" + neighbour
                    threehop_path_sequence = threehop_entity_mention + threehop_predicate.replace("<", "").replace(">", "")
                    if neighbour in self.entities:
                        threehop_entity_score = self.escores[neighbour]
                    else:
                        threehop_entity_score = sq.entity_score
                    threehop_node = Node(
                        entity=neighbour,
                        mention=threehop_entity_mention,
                        entity_score=threehop_entity_score
                    )
                    threehop_path = Path(
                        tail=threehop_node,
                        predicate=threehop_predicate,
                        query_sequence=threehop_query_sequence,
                        path_sequence=threehop_path_sequence
                    )
                    new_sq = copy.copy(sq)
                    new_sq.threehop_path = threehop_path
                    new_sq.entity_score = new_sq.GenerateEntityScore()
                    new_sq.query_sequence, new_sq.path_sequence = new_sq.GenerateSequence()
                    new_sq.ans = {conjunction}
                    final_querys.append(new_sq)
            except:
                pass

            try:
                threehop_predicate = c_graph.edges[neighbour, conjunction]["prop"][0]
                # 先生成两实体三体路径：
                if hint(threehop_predicate,cur_question)!=0 \
                        and threehop_predicate != sq.onehop_path.predicate \
                        and threehop_predicate != sq.twohop_path.predicate:
                    threehop_query_sequence = "?y&&&" + threehop_predicate + "&&&?x"
                    threehop_path_sequence = threehop_predicate.replace("<", "").replace(">", "")
                    threehop_path = Path(
                        predicate=threehop_predicate,
                        query_sequence=threehop_query_sequence,
                        path_sequence=threehop_path_sequence
                    )
                    new_sq = copy.copy(sq)
                    new_sq.threehop_path = threehop_path
                    new_sq.entity_score = new_sq.GenerateEntityScore()
                    new_sq.query_sequence, new_sq.path_sequence = new_sq.GenerateSequence()
                    new_sq.ans = {neighbour}
                    final_querys.append(new_sq)
                # 接下来扩展三实体三跳路径
                threehop_entity_mention = self.getMention4Entity(neighbour)
                if self.Filter4ThreehopThreeEntity(
                        neighbour,
                        threehop_entity_mention,
                        threehop_predicate,
                        onehop_node.mention,
                        twohop_node.mention,
                        cur_question
                ):
                    threehop_query_sequence = neighbour + "&&&" + threehop_predicate + "&&&?x"
                    threehop_path_sequence = threehop_predicate.replace("<", "").replace(">", "") + neighbour_mention
                    if neighbour in self.entities:
                        threehop_entity_score = self.escores[neighbour]
                    else:
                        threehop_entity_score = sq.entity_score
                    threehop_node = Node(
                        entity=neighbour,
                        mention=threehop_entity_mention,
                        entity_score=threehop_entity_score
                    )
                    threehop_path = Path(
                        root=threehop_node,
                        predicate=threehop_predicate,
                        query_sequence=threehop_query_sequence,
                        path_sequence=threehop_path_sequence
                    )
                    new_sq = copy.copy(sq)
                    new_sq.threehop_path = threehop_path
                    new_sq.entity_score = new_sq.GenerateEntityScore()
                    new_sq.query_sequence, new_sq.path_sequence = new_sq.GenerateSequence()
                    new_sq.ans = {conjunction}
                    final_querys.append(new_sq)
            except:
                pass