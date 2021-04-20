#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 9:34 上午
# @Author  : SPC
# @FileName: KnowledgeMethod.py
# @Software: PyCharm
# @Des     : 本项目采用读文件的方式对知识库内容进行检索，这里定义了检索知识库的一些基本操作
import sys
import os
o_path = os.getcwd()
sys.path.append(o_path)
import pickle
from collections import defaultdict
from Resource import Resource
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

if __name__ == '__main__':
    rs = Resource()
    kb_path = rs.triple_path
    kb_v2e_path = rs.triple_v2e_path
    kb = KnowledgeBase(kb_path,kb_v2e_path)
    print(kb.query_by_v2e_name("张煐原名"))



