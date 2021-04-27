#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 9:33 上午
# @Author  : SPC
# @FileName: DataGenerate.py
# @Software: PyCharm
# @Desn    : 生成训练数据的相关方法

import json
import random

class ModelDataset(object):
    def BalanceAndShuffle(self, dataset, getLabel, pos_label, oversampling=True):
        """
        定义一个公共函数，用于对生成的原始数据集进行过采样（欠采样）
        :param getLabel: 获取数据集中数据的标签的函数
        :param pos_label: 数据集中的正例标签形式
        :param oversampling: bool型变量，用于确定是要进行过采样还是欠采样
        :return:
        """
        pos_ls = []
        neg_ls = []
        for data in dataset:
            label = getLabel(data)
            if label == pos_label:
                pos_ls.append(data)
            else:
                neg_ls.append(data)
        d_value = abs(len(pos_ls)-len(neg_ls))
        # 默认正例少于负例
        print(len(pos_ls),len(neg_ls))
        for i in range(d_value):
            if oversampling:
                repeated_pos_data = random.sample(pos_ls, 1)[0]
                dataset.append(repeated_pos_data)
        random.shuffle(dataset)
        return dataset

class NameEntityRecognize(object):
    """
    用于生成NER的训练数据，解析NER的结果数据
    """
    def GenerateTrainData(
            self,
            mention_file: str=None,
            question_file: str=None,
            target_file: str=None
    ):
        """
        :return: 生成用于进行序列标注模型训练的数据
        """
        with open(mention_file,"r",encoding="UTF-8") as fm, open(question_file,"r",encoding="UTF-8") as fq, open(target_file,"w",encoding="UTF-8") as ft:
            mlines = fm.readlines()
            qlines = fq.readlines()
            for qline,mline in zip(qlines,mlines):
                question = qline.strip()
                question_ls = list(question)
                label_ls = ["O" for _ in range(len(question_ls))]
                mls = mline.strip().split("|||")
                for mention in mls:
                    try:
                        start_pos = question.find(mention)
                        end_pos = start_pos + len(mention)
                        for idx in range(start_pos,end_pos):
                            if idx == start_pos:
                                label_ls[idx] = "B"
                            else:
                                label_ls[idx] = "I"
                    except Exception as e:
                        print(e)
                for q_token, l_token in zip(question_ls, label_ls):
                    ft.write(q_token+" "+l_token+"\n")
                ft.write("\n")
            print("Data Generate finished")

    def ExtractEntityFromResultFile(
            self,
            result_file: str=None,
            question_file: str=None,
            target_file: str=None
    ):
        with open(result_file,"r",encoding="UTF-8") as load_f,open(question_file,"r",encoding="UTF-8") as fq,open(target_file,"w",encoding="UTF-8") as ft:
            flines = load_f.readlines()
            qlines = fq.readlines()
            for line in flines:
                ner_data = json.loads(line.strip())
                qid = ner_data["id"]
                question = qlines[qid].strip()
                entities = ner_data["entities"]
                ner_results = []
                for entity_pos in entities:
                    start_pos = entity_pos[1]
                    end_pos = entity_pos[2]
                    mention = question[start_pos:end_pos+1]
                    ner_results.append(mention)
                ft.write("|||".join(ner_results)+"\n")


