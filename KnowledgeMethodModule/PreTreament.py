#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/5/13 3:56 下午
# @Author  : SPC
# @FileName: PreTreament.py
# @Software: PyCharm
# @Desn    : 对知识库进行预处理，生成对应的索引文件
import pickle
import re
from collections import defaultdict

punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}·，。：（）；’‘“”、？《》~ """
rawstr = str.maketrans({key: None for key in punctuation})

class BuildIndex(object):
    def __init__(self,kb_path):
        #定义资源文件根路径
        self.kb_path = kb_path
        #定义知识库三元组文件路径
        self.tri_path = self.kb_path+"pkubase-complete/pkubase-complete.txt"
        #定制知识库三元组反向索引路径
        self.tri_v2e_path = self.kb_path+"pkubase-complete/pkubase-complete-v2e.txt"
        #定义知识库指称表路径
        self.m2e_path = self.kb_path+"pkubase-mention2ent/pkubase-mention2ent.txt"
        #定义知识库反向指称表路径
        self.e2m_path = self.kb_path+"pkubase-mention2ent/pkubase-ent2mention.txt"
    def OrgnizeKB(self,source_file):
        """
        在实际使用过程中发现，知识库排序混乱，需要进行重新组织
        :return:
        """
        fr = open(source_file,"r",encoding="UTF-8")
        dic = defaultdict(list)
        kblines = fr.readlines()
        for line in kblines:
            ls = line.strip().split("\t")
            entity = ls[0]
            dic[entity].append(line)
        fr.close()
        ft = open(source_file,"w",encoding="UTF-8")
        for key in dic.keys():
            for line in dic[key]:
                ft.write(line)
    def RebuildM2E(self):
        fr = open(self.tri_path, "r", encoding="UTF-8")
        entity_set = set()
        kblines = fr.readlines()
        for line in kblines:
            ls = line.strip().split("\t")
            entity = ls[0]
            entity_set.add(entity)
        fm = open(self.m2e_path, "r", encoding="UTF-8")
        m_entity_set = set()
        mlines = fm.readlines()
        for line in mlines:
            try:
                ls = line.strip().split("\t")
                entity = "<"+ls[1]+">"
                m_entity_set.add(entity)
            except BaseException as e:
                print(line)
        fm.close()
        fm = open(self.m2e_path, "a", encoding="UTF-8")
        for candidate in entity_set:
            if candidate not in m_entity_set:
                print(candidate)
                fm.write(candidate.replace("<","").replace(">","")+"\t"+candidate.replace("<","").replace(">","")+"\t"+"10000"+"\n")
    def ConstructE2MFile(self):
        """
        构建文件，实现由entity确定mention，用于后续进行数据反标
        :return:
        """
        with open(self.m2e_path,"r",encoding="UTF-8") as fs,open(self.e2m_path,"w",encoding="UTF-8") as ft:
            dict = defaultdict(set)
            for i,line in enumerate(fs.readlines()):
                u_line = line
                sp = '\t'
                try:
                    mention,entity,popularity = [part.strip() for part in u_line.strip().split(sp)]
                    add_line = '%s\t%s\t%s' % (entity,mention,popularity)
                    index = entity
                    dict[index].add(add_line)
                except Exception as e:
                    print(e)
                    pass
            for key in dict:
                for l in dict.get(key):
                    ft.write(l + "\n")

    def ConstructV2ETriplesFile(self):
        """
        构建反向三元组文件，用于进一步构建知识库反向索引
        :return:
        """
        with open(self.tri_path,"r",encoding="UTF-8") as fr,open(self.tri_v2e_path,"w",encoding="UTF-8") as fw:
            dict = defaultdict(set)
            for i, line in enumerate(fr):
                u_line = line
                sp = '\t'
                try:
                    entity, prop, value = [part.strip() for part in u_line.strip().split(sp)]
                    add_line = '%s\t%s\t%s' % (value.strip(".").strip(), prop, entity)
                    index = value.strip(".").strip()
                    if not re.match("<.*>", index):
                        index = index.translate(rawstr).lower()
                    dict[index].add(add_line)
                except Exception as e:
                    print(e)
                    pass
            for key in dict:
                for l in dict.get(key):
                    fw.write(l + "\n")

    def build_m2e_index(self):
        """
        定义mention2entity的索引文件
        :return:
        """
        m2e_index = defaultdict(set)
        # 根据mention2entity表构建索引词典
        fr = open(self.m2e_path,"r",encoding="UTF-8")
        for i, line in enumerate(fr):
            try:
                u_line = line
                sp = '\t'
                mention, entity, freq = [part.strip() for part in u_line.strip().split(sp)]
                # 为mention2entity做索引的时候，去了特殊字符，也统一了字母为小写
                index = mention.translate(rawstr).lower()
                m2e_index[index].add("<"+entity+">")
            except Exception as e:
                print("ERROR in line:" + line)
                pass
        fr.close()
        # 由于三元组文件中有一些实体没有出现在mention2entity表中，因此需要额外处理
        fs = open(self.tri_path,"r",encoding="UTF-8")
        for i, line in enumerate(fs):
            try:
                t_line = line
                sp = '\t'
                sub, pre, obj = [part.strip() for part in t_line.strip().split(sp)]
                sub_index = sub.strip(".").strip().strip("<").strip(">").split("_")[0].translate(rawstr).lower()
                m2e_index[sub_index].add(sub.strip(".").strip())
                if "<" in obj and ">" in obj:
                    obj_index = obj.strip(".").strip().strip("<").strip(">").split("_")[0].translate(rawstr).lower()
                    m2e_index[obj_index].add(obj.strip(".").strip())
                else:
                    obj_index = obj.translate(rawstr).lower()
                    m2e_index[obj_index].add(obj)
            except Exception as e:
                print("ERROR in line:" + line)
                pass
        fw = open(self.m2e_path + ".index.pkl", "wb")
        pickle.dump(m2e_index, fw)
        print("mention2entity index has been created in "+self.m2e_path+".index.pkl")

    def build_e2m_index(self):
        """
        定义ent2mention的索引文件
        :return:
        """
        with open(self.e2m_path,"r",encoding="UTF-8") as fr,open(self.e2m_path+".index.pkl","wb") as fw:
            e2m_index = defaultdict(list)
            for i, line in enumerate(fr):
                try:
                    u_line = line
                    sp = '\t'
                    entity, mention, popularity = [part.strip() for part in u_line.strip().split(sp)]
                    index = entity
                    e2m_index[index].append((mention,popularity))
                except Exception as e:
                    print("ERROR in line:" + line)
                    pass
            pickle.dump(e2m_index, fw)
            print("entity2mention index has been created in "+self.e2m_path+".index.pkl")

    def build_value_file(self,source_file, target_file):
        """
        统计知识库中所有的value值
        :return:
        """
        with open(source_file, "r", encoding="UTF-8") as fr, open(target_file, "w", encoding="UTF-8") as ft:
            kb_lines = fr.readlines()
            for line in kb_lines:
                kb_ls = line.strip().split("\t")
                value = kb_ls[2]
                if "<" not in value and ">" not in value:
                    ft.write(value+"\n")
            print("value file has been created in " + target_file)
    def build_kb_index(self,source_file):
        """
        定义三元组文件的索引文件
        :return:
        """
        with open(source_file, "r", encoding="UTF-8") as fr, open(source_file + ".index.pkl", "wb") as fw:
            last_entity = ''
            offset = 0
            length = 0
            byte_len = 0
            dict = {}
            for i, line in enumerate(fr):
                u_line = line
                sp = '\t'
                try:
                    entity, prop, value = [part.strip() for part in u_line.strip().split(sp)]
                    current_entity = entity
                    if not re.match("<.*>", current_entity):
                        current_entity = current_entity.translate(rawstr).lower()
                    if current_entity != last_entity and last_entity != '':
                        if not re.match("<.*>", last_entity):
                            last_entity = last_entity.translate(rawstr).lower()
                        dict[last_entity] = (offset, length)
                        # w_line = '%s\t%d\t%d\n' % (last_entity, offset, length)
                        # fw.write(w_line)
                        # Update
                        offset += byte_len
                        length = 0
                        byte_len = 0
                    last_entity = current_entity
                except Exception as e:
                    print('Error: line %s' % (line))
                    print(e)
                    pass
                length += len(line)
                byte_len += len(line.encode('utf-8'))
                if (i + 1) % 100000 == 0:
                    print(i + 1)
            if not re.match("<.*>", last_entity):
                last_entity = last_entity.translate(rawstr).lower()
            dict[last_entity] = (offset, length)
            pickle.dump(dict, fw)
            print("knowledge index has been created in " + self.tri_path + ".index.pkl")


if __name__ == '__main__':
    BI = BuildIndex("data/Knowledge/")
    #BI.build_value_file(BI.tri_path, BI.kb_path+"pkubase-complete/pkubase-values.txt")
    #BI.build_m2e_index()
    BI.build_kb_index(BI.tri_path)
    BI.ConstructV2ETriplesFile()
    BI.build_kb_index(BI.tri_v2e_path)
    #BI.build_e2m_index()



