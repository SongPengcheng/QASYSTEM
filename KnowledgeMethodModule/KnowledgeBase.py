#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 9:34 上午
# @Author  : SPC
# @FileName: KnowledgeBase.py
# @Software: PyCharm
# @Des     : 本项目采用读文件的方式对知识库内容进行检索，这里定义了检索知识库的一些基本操作
import pickle
from collections import defaultdict
from Resource import Resource
from MathMethod import jaccard, hint, editDistance
import networkx as nx
punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}·，。：（）；’‘“”、？《》~ """
rawstr = str.maketrans({key: None for key in punctuation})

class Entity(dict):
    def __init__(self, name, info_dict={}):
        self.name = name
        super(Entity, self).__init__()
        super(Entity, self).update(info_dict)
class KnowledgeBase(object):
    def __init__(self,kb_path,kb_v2e_path):
        """
        param: kb_path 知识库正向三元组路径
        param: kb_v2e_path 知识库反向三元组路径
        """
        self.kb_path = kb_path
        self.idx_dict = self.load_index()
        self.kb_fp = open(self.kb_path,"r",encoding="UTF-8")
        self.kb_v2e_path = kb_v2e_path
        self.v2e_idx_dict = self.load_v2e_index()
        self.kb_v2e_fp = open(self.kb_v2e_path,"r",encoding="UTF-8")
        self.sp = "\t"
    def load_index(self):
        """
        return: 加载正向三元组文件的索引，索引内容为(实体, 起始位置, 偏移量)
        """
        index_path = self.kb_path+".index.pkl"
        with open(index_path,"rb") as f:
            dict = pickle.load(f)
        return dict
    def load_v2e_index(self):
        """
        return: 加载反向三元组文件的索引，索引内容为(属性值, 起始位置, 偏移量)
        """
        index_path = self.kb_v2e_path + ".index.pkl"
        with open(index_path, "rb") as f:
            dict = pickle.load(f)
        return dict
    def query_by_name(self,name):
        """
        return: 根据实体名称找到知识库中与实体相关的全部三元组内容
        """
        start, length = self.idx_dict.get(name,(-1,-1))
        if start == -1:
            return None
        else:
            return self.read_entity((start,length))
    def read_entity(self,index):
        """
        return: 根据知识库的索引获取知识库的内容
        """
        start,length = index
        self.kb_fp.seek(start)
        text = self.kb_fp.read(length).strip()
        info_dict = defaultdict(list)
        name = ""
        for line in text.split('\n'):
            if (line in ['', ' ', '\n']):
                continue
            try:
                name, prop, value = [part.strip() for part in line.strip().split(self.sp)]
                info_dict[prop].append(value)
            except Exception as e:
                print(e)
                print('Error: %s' % (line))
                exit(-1)
        return Entity(name, info_dict)
    def query_by_v2e_name(self, name):
        """
        return: 根据属性值或尾实体找到知识库中相关的全部三元组内容
        """
        start, length = self.v2e_idx_dict.get(name, (-1, -1))
        if start == -1:
            return None
        else:
            return self.read_v2e_entity((start, length))
    def read_v2e_entity(self,index):
        """
        return: 由反向知识库的索引获取反向知识库的内容
        """
        start,length = index
        self.kb_v2e_fp.seek(start)
        text = self.kb_v2e_fp.read(length).strip()
        info_dict = defaultdict(list)
        name = ""
        for line in text.split('\n'):
            if (line in ['', ' ', '\n']):
                continue
            try:
                name, prop, value = [part.strip() for part in line.strip().split(self.sp)]
                info_dict[prop].append(value)
            except Exception as e:
                print(e)
                print('Error: %s' % (line))
                exit(-1)
        return Entity(name, info_dict)
    def count_by_name(self,name):
        """
        return: 根据索引计算实体（属性值）对应的三元组数量
        """
        start, length = self.idx_dict.get(name, (-1, -1))
        if start == -1:
            return 0
        else:
            return self.count_entity((start, length))
    def count_entity(self,index):
        """
        return: 根据名称计算实体（属性值）对应的三元组数量
        """
        start, length = index
        self.kb_fp.seek(start)
        text = self.kb_fp.read(length).strip()
        return len(text.split('\n'))
    def count_by_v2e_name(self, name):
        """
        return: 根据索引计算实体（属性值）对应的三元组数量
        """
        start, length = self.v2e_idx_dict.get(name, (-1, -1))
        if start == -1:
            return 0
        else:
            return self.count_v2e_entity((start, length))
    def count_v2e_entity(self,index):
        """
        return: 根据名称计算实体（属性值）对应的三元组数量
        """
        start, length = index
        self.kb_v2e_fp.seek(start)
        text = self.kb_v2e_fp.read(length).strip()
        return len(text.split('\n'))
    @staticmethod
    def load_dict(self, dict_path):
        """
        param: 索引文件路径
        return: 加载一些词典形式的索引文件，如mention2entity或entity2mention
        """
        dict_index = None
        with open(dict_path,"rb") as f:
            dict_index = pickle.load(f)
        return dict_index
    def getFather(self, entity):
        """
        :param entity: 查询实体
        :return: 实体全部的父亲节点，即指向entity的邻接节点
        """
        father = self.query_by_v2e_name(entity)
        return father
    # 找到子节点，即当前节点作为三元组x y z中的x
    def getSon(self, entity):
        """
        :param entity: 查询实体
        :return: 实体全部的子孙节点，即entity指向的邻接节点
        """
        son = self.query_by_name(entity)
        return son
    # 在生成图的过程中，为实体查找全部的邻居节点以及属性
    def getEdges4Entity(
            self,
            entity:str=None
    )->(list,list):
        """
        :param entity: 需要查询的实体
        :return: 实体关联的路径与邻接节点edges:[(s,p,o),(s,p,o)];neighbours:{entity1,entity2}
        """
        edges = set()
        neighbors = set()
        try:
            son = self.getSon(entity)
            for key in son.keys():
                for value in son.get(key):
                    subject = value.strip(".").strip()
                    edges.add((entity, subject, key))
                    neighbors.add(subject)
        except BaseException as e:
            print(e)
            pass
        if kb.count_by_v2e_name(entity) <= 8000:
            try:
                father = self.getFather(entity)
                for key in father.keys():
                    for value in father.get(key):
                        subject = value.strip(".").strip()
                        edges.add((subject, entity, key))
                        neighbors.add(subject)
            except BaseException as e:
                print(e)
                pass
        return list(edges), list(neighbors)
    # 为实体生成图
    def getGraph4Entity(
            self,
            entity:str=None,
            one_hop:bool=True
    )->nx.DiGraph:
        """
        :param entity: 实体
        :param one_hop: bool型标记位，true的时候生成一跳范围的图，false的时候生成两跳范围的图
        :return:
        """
        total_edges, neighbors = self.getEdges4Entity(entity)
        if not one_hop:
            for subject in neighbors:
                step_edges, step_neighbors = self.getEdges4Entity(subject)
                total_edges.extend(step_edges)
        graph = nx.DiGraph()
        for nodeX, nodeY, property in total_edges:
            graph.add_edges_from([(nodeX, nodeY, {"prop": property})])
        return graph
    # 从图上获取实体一跳范围内的路径
    def getOneHopPaths(
            self,
            graph:nx.DiGraph=None,
            root:str=None
    )->list:
        """
        :param graph: 知识图谱子图（即根节点一跳范围路径构成的子图）
        :param root: 子图根节点
        :return: 根节点在知识图谱中的全部一跳路径[[(s,p,o)],[(s,p,o)]]
        """
        neighbor = set([y for x, y in graph.out_edges(root)] + [x for x, y in graph.in_edges(root)]) - set([root])
        paths = []
        for row in neighbor:
            # 在知识库中，存在两个实体之间有多个属性相连接的情况，因此做了一些修改
            try:
                edgels = graph.edges[root, row]["prop"]
                for edge in edgels:
                    paths.append([(root, edge, row)])
            except KeyError:
                pass
            try:
                edgels = graph.edges[row, root]["prop"]
                for edge in edgels:
                    paths.append([(row, edge, root)])
            except KeyError:
                pass
        return paths
    # 从图上获取实体两跳范围内的路径
    def getTwoHopPaths(
            self,
            graph:nx.DiGraph=None,
            root:str=None
    )->list:
        """
        :param graph: 知识图谱子图（即根节点两跳范围路径构成的子图）
        :param root: 子图根节点
        :return: 根节点在知识图谱中的全部一跳路径[[(s1,p1,o1),(s2,p2,o2)],[(s1,p1,o1),(s2,p2,o2)]]
        """
        first = set([y for x, y in graph.out_edges(root)] + [x for x, y in graph.in_edges(root)]) - set([root])
        paths = []
        for row in first:
            try:
                first_edge_ls = graph.edges[root, row]["prop"]
                second = set(graph[row]) - set([root])
                for line in second:
                    try:
                        second_edge_ls = graph.edges[line, row]["prop"]
                        for first_edge in first_edge_ls:
                            for second_edge in second_edge_ls:
                                tmp_1 = (root, first_edge, row)
                                tmp_2 = (line, second_edge, row)
                                paths.append([tmp_1, tmp_2])
                    except KeyError:
                        pass
                    try:
                        second_edge_ls = graph.edges[row, line]["prop"]
                        for first_edge in first_edge_ls:
                            for second_edge in second_edge_ls:
                                tmp_1 = (root, first_edge, row)
                                tmp_2 = (row, second_edge, line)
                                paths.append([tmp_1, tmp_2])
                    except KeyError:
                        pass
            except KeyError:
                pass
            try:
                first_edge_ls = graph.edges[row, root]["prop"]
                second = set(graph[row]) - set([root])
                for line in second:
                    try:
                        second_edge_ls = graph.edges[line, row]["prop"]
                        for first_edge in first_edge_ls:
                            for second_edge in second_edge_ls:
                                tmp_1 = (row, first_edge, root)
                                tmp_2 = (line, second_edge, row)
                                paths.append([tmp_1, tmp_2])
                    except KeyError:
                        pass
                    try:
                        second_edge_ls = graph.edges[row, line]["prop"]
                        for first_edge in first_edge_ls:
                            for second_edge in second_edge_ls:
                                tmp_1 = (row, first_edge, root)
                                tmp_2 = (row, second_edge, line)
                                paths.append([tmp_1, tmp_2])
                    except KeyError:
                        pass
            except KeyError:
                pass
        return paths
    # 获取实体所有二跳路径与问题的jaccard相似度的最大值
    def ScoreOfOneHopPathOverlap(
            self,
            root: str = None,
            graph: nx.DiGraph = None,
            question: str = None,
            mention: str = None
    ) -> float:
        """
        :param root:
        :param graph:
        :param question:
        :param mention:
        :return: 计算实体root所关联的全部一跳路径与问题的jaccard相似度最大值
        """
        max_j = 0
        paths = self.getOneHopPaths(graph, root)
        # paths:[[(s, p, o)], [(s, p, o)]]
        for path in paths:
            sequence = (mention + path[0][1]).translate(rawstr)
            j = jaccard(sequence, question)
            if j > max_j:
                max_j = j
        return max_j
    # 获取实体所有二跳路径与问题的jaccard相似度的最大值
    def ScoreOfTwoHopPathOverlap(
            self,
            root:str=None,
            graph:nx.DiGraph=None,
            question:str=None,
            mention:str=None
    )->float:
        """
        :param root:
        :param graph:
        :param question:
        :param mention:
        :return: 计算实体root所关联的全部两跳路径与问题的jaccard相似度最大值
        """
        max_j = 0
        paths = self.getTwoHopPaths(graph, root)
        # paths:[[(s1,p1,o1),(s2,p2,o2)],[(s1,p1,o1),(s2,p2,o2)]]
        for path in paths:
            sequence = (mention + path[0][1] + path[1][1]).translate(rawstr)
            j = jaccard(sequence, question)
            if j > max_j:
                max_j = j
        return max_j
    # 从图上根据实体和谓词获取邻居
    def getNeighbourByEntityAndPredicate(
            self,
            graph:nx.DiGraph=None,
            root:str=None,
            predicate:str=None
    )->list:
        all_neighbors = set([y for x, y in graph.out_edges(root)] + [x for x, y in graph.in_edges(root)]) - set([root])
        neighbour = []
        for row in all_neighbors:
            try:
                edgels = graph.edges[root, row]["prop"]
                for edge in edgels:
                    if edge == predicate:
                        neighbour.append(row)
            except KeyError:
                edgels = graph.edges[row, root]["prop"]
                for edge in edgels:
                    if edge == predicate:
                        neighbour.append(row)
        return neighbour

if __name__ == '__main__':
    rs = Resource()
    kb_path = rs.triple_path
    kb_v2e_path = rs.triple_v2e_path
    kb = KnowledgeBase(kb_path,kb_v2e_path)
    print(kb.query_by_v2e_name("张煐原名"))


