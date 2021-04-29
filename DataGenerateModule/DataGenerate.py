#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 9:33 上午
# @Author  : SPC
# @FileName: DataGenerate.py
# @Software: PyCharm
# @Desn    : 生成训练数据的相关方法

import json
import random
import numpy as np
from KnowledgeMethodModule.KnowledgeBase import KnowledgeBase
from NerModule.NerMedule import NerModule
from ElinkModule.ElinkModule import ElinkModule
from collections import defaultdict
from Rule import punctuation,rawstr
import BertModule.LoadBertModel as LoadBertModel
import argparse
import Resource as rs

class Public(object):
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

class EntityLink(object):
    """
    生成用于实体链接的训练数据
    """
    def __init__(
            self,
            knowledgebase: KnowledgeBase=None,
            mentionfile: str=None,
            questionfile: str=None,
            targetfile: str=None
    ):
        self.kb = knowledgebase
        self.mentionfile = mentionfile
        self.questionfile = questionfile
        self.targetfile = targetfile
        self.mentionlist = self.LoadMentionList()
        self.ner = NerModule(kb=self.kb)
        self.elink = ElinkModule(kb=self.kb)
    def LoadMentionList(self):
        """
        :return: 加载标准的mention列表
        """
        with open(self.mentionfile,"r",encoding="UTF-8") as fs:
            mlines = fs.readlines()
            mls = []
            for line in mlines:
                ls = line.strip().split("|||")
                mls.append(ls)
            return mls
    def ImportNoiseOfMention(self):
        """
        :return: 为标准的mention列表引入噪声
        """
        with open(self.questionfile,"r",encoding="UTF-8") as fq:
            qlines = fq.readlines()
            new_mentionlist = []
            for i,line in enumerate(qlines):
                ls = self.mentionlist[i]
                question = line.strip()
                max_str = True
                total_mention = self.ner.getPossibleMentions(question,max_str)
                total_value = self.ner.getPossibleValues(question,max_str)
                total_mention.extend(total_value)
                random.shuffle(total_mention)
                for j in range(min(3,len(total_mention))):
                    if total_mention[j] not in ls:
                        ls.append(total_mention[j])
                new_mentionlist.append(ls)
            return new_mentionlist
    def GenerateDataSet4Train(self,entity_file):
        """
        :param entity_file: 记录标准entity的文件
        :return: 带有正例与负例entity的txt文件
        """
        with open(self.targetfile,"w",encoding="UTF-8") as ft,open(entity_file,"r",encoding="UTF-8") as f_entity:
            total_mls = self.ImportNoiseOfMention()
            elines = f_entity.readlines()
            standard_entities_ls = []
            for line in elines:
                ls = line.strip().split("|||")
                standard_entities_ls.append(ls)
            for qid,mls in enumerate(total_mls):
                standard_entities = standard_entities_ls[qid]
                for mention in mls:
                    el, vl = self.elink.getEntityFromMention(qid + 1, mention)
                    for key in el.keys():
                        #这里相当于对实体的一个标注
                        if key in standard_entities:
                            el[key].append("1")
                        else:
                            el[key].append("0")
                        ft.write("\t".join(el[key]) + "\n")
                    for key in vl.keys():
                        if key in standard_entities:
                            vl[key].append("1")
                        else:
                            vl[key].append("0")
                        ft.write("\t".join(vl[key]) + "\n")

    def GenerateJsonDataSet(self,entity_file):
        """
        :param entity_file: 记录标准entity的文件
        :return: 生成带有正例与负例entity的json文件
        """
        with open(self.targetfile,"w",encoding="UTF-8") as ft,open(entity_file,"r",encoding="UTF-8") as f_entity:
            total_mls = self.mentionlist
            elines = f_entity.readlines()
            standard_entities_ls = []
            total_dict = defaultdict(list)
            for line in elines:
                ls = line.strip().split("|||")
                standard_entities_ls.append(ls)
            for qid,mls in enumerate(total_mls):
                standard_entities = standard_entities_ls[qid]
                for mention in mls:
                    el, vl = self.elink.getEntityFromMention(qid + 1, mention)
                    for key in el.keys():
                        #这里相当于对实体的一个标注
                        if key in standard_entities:
                            label = 1
                        else:
                            label = 0
                        tmp_dict = {"mention": el[key][1], "entity": el[key][2], "outdegree": el[key][3],
                                    "indegree": el[key][4], "label": label}
                        total_dict[qid].append(tmp_dict)

                    for key in vl.keys():
                        if key in standard_entities:
                            label = 1
                        else:
                            label = 0
                        tmp_dict = {"mention": vl[key][1], "entity": vl[key][2], "outdegree": vl[key][3],
                                    "indegree": vl[key][4], "label": label}
                        total_dict[qid].append(tmp_dict)
            json.dump(total_dict, ft, ensure_ascii=False, indent=4)
            print("Entity Link dataset has been generated!")

class EntityClassifier(object):
    """
    用于训练实体分类器，数据形式为(question, entity, label)，
    如果实体与问题属于同一类标为1，否则标为0
    """
    def __init__(
            self,
            sourcefile: str=None,
            targetfile: str=None,
            questionfile: str=None,
            trainflag: bool=True
    ):
        """
        :param sourcefile: EntityLink模块生成的正负例entity文件
        :param targetfile: 生成的目标训练文件
        :param questionfile: 数据集问题文件
        :param trainflag: 判断是否要生成训练数据
        """
        self.questionfile = questionfile
        self.sourcefile = sourcefile
        self.targetfile = targetfile
        self.trainflag = trainflag
    def GenerateDataSetByTxt(self):
        """
        :return: 从txt形式的正负例文件生成训练数据集
        """
        with open(self.sourcefile,"r",encoding="UTF-8") as fs,open(self.targetfile,"w",encoding="UTF-8") as ft:
            lines = fs.readlines()
            with open(self.questionfile,"r",encoding="UTF-8") as fq:
                qlines = fq.readlines()
                for line in lines:
                    ls = line.strip().split("\t")
                    qid = int(ls[0])-1
                    print(qid)
                    if self.trainflag:
                        label = ls[-1]
                    else:
                        label = "0"
                    entity = ls[2].translate(rawstr)
                    question = qlines[qid].strip()
                    ans = [question,entity,label]
                    ft.write(" ".join(ans)+"\n")

    def GenerateDataSetByJson(self):
        """
        :return: 从json形式的正负例文件中生成训练数据集
        """
        with open(self.sourcefile,"r",encoding="UTF-8") as fs, open(self.targetfile,"w",encoding="UTF-8") as ft, open(self.questionfile,"r",encoding="UTF-8") as fq:
            print(self.targetfile)
            if self.trainflag:
                fe = open("data/Task/Train/train_entities.txt","r",encoding="UTF-8")
            else:
                fe = open("data/Task/Dev/dev_entities.txt","r",encoding="UTF-8")
            elines = fe.readlines()
            elink_dict = json.load(fs)
            qlines = fq.readlines()
            dataset = []
            for qid in elink_dict.keys():
                question = qlines[int(qid)].strip()
                els = elines[int(qid)].strip().split("|||")
                els = [entity.translate(rawstr) for entity in els]
                for tmp_dict in elink_dict[qid]:
                    if tmp_dict["entity"].translate(rawstr) in els:
                        label = "1"
                    else:
                        label = "0"
                    ans = [question, tmp_dict["entity"].translate(rawstr), label]
                    dataset.append(ans)
            # 如果是做训练数据集，那么就要进行过采样和shuffle
            if self.trainflag:
                pu = Public()
                dataset = pu.BalanceAndShuffle(dataset, lambda x:x[-1], "1", oversampling=True)
            for data in dataset:
                ft.write("\t".join(data)+"\n")

class EntityRank(object):
    """
    生成用于候选实体排序的数据
    """
    def __init__(
            self,
            source_file: str=None,
            question_file: str=None,
            target_file: str=None,
            knowledgebase: KnowledgeBase=None
    ):
        self.sourcefile = source_file
        self.questionfile = question_file
        self.targetfile = target_file
        self.kb = knowledgebase
        self.elink = ElinkModule(kb=self.kb)

    def UpdateJsonDataset(self):
        """
        更新训练数据，验证数据中的实体问题相关度得分
        """
        model_path = "model/NewEntityClassifier"
        predictor, tokenizer = LoadBertModel.LoadModel(model_path)
        fs = open(self.sourcefile,"r",encoding="UTF-8")
        total_dict = json.load(fs)
        fq = open(self.questionfile,"r",encoding="UTF-8")
        qlines = fq.readlines()
        for key in total_dict.keys():
            qid = int(key)
            question = qlines[qid].strip()
            text_pairs = []
            for tmp_dict in total_dict[key]:
                entity = tmp_dict["entity"].translate(rawstr)
                text_pairs.append((question,entity))
            sem_scores = LoadBertModel.PredictByTextPairs(predictor,tokenizer,text_pairs)
            for idx,tmp_dict in enumerate(total_dict[key]):
                tmp_dict["semsim"] = sem_scores[idx]
        fs.close()
        ft = open(self.sourcefile,"w",encoding="UTF-8")
        json.dump(total_dict, ft, ensure_ascii=False, indent=4)
        ft.close()

    def GenerateData4EntityRank(self):
        with open(self.sourcefile,"r",encoding="UTF-8") as fs, open(self.questionfile,"r",encoding="UTF-8") as fq:
            qlines = fq.readlines()
            total_dict = json.load(fs)
            total_features = []
            for key in total_dict.keys():
                print(key)
                qid = int(key)
                question = qlines[qid].strip()
                for tmp_dict in total_dict[key]:
                    label = tmp_dict["label"]
                    mention = tmp_dict["mention"]
                    entity = tmp_dict["entity"]
                    indegree = tmp_dict["indegree"]
                    outdegree = tmp_dict["outdegree"]
                    entity_sem_sim = tmp_dict["semsim"]
                    features = self.elink.getEntityFeatures(
                        qid=qid,
                        label=int(label),
                        question=question,
                        mention=mention,
                        entity=entity,
                        indegree=int(indegree),
                        outdegree=int(outdegree),
                        entity_sem_sim=float(entity_sem_sim)
                    )
                    total_features.append(features)
            total_features = np.array(total_features)
            np.save(self.targetfile, total_features)

    def GenerateData4EntityRankWithRelation(self,target_file,train_flag):
        with open(self.sourcefile,"r",encoding="UTF-8") as fs, open(self.questionfile,"r",encoding="UTF-8") as fq, open(target_file, "w", encoding="UTF-8") as ft:
            qlines = fq.readlines()
            total_dict = json.load(fs)
            total_features = []
            dataset = []
            for key in total_dict.keys():
                print(key)
                qid = int(key)
                question = qlines[qid].strip()
                for tmp_dict in total_dict[key]:
                    entity = tmp_dict["entity"]
                    label = tmp_dict["label"]
                    graph = self.kb.getGraph4Entity(entity,True)
                    onehop_relations = self.kb.getOneHopPredicates(graph,entity)
                    tmp = entity.translate(rawstr)
                    for relation in onehop_relations:
                        tmp += relation.translate(rawstr)
                    dataset.append([question,tmp,str(label)])
            if train_flag:
                pu = Public()
                dataset = pu.BalanceAndShuffle(dataset, lambda x:x[-1], "1", oversampling=True)
            for data in dataset:
                ft.write("\t".join(data)+"\n")

    def UpdateJsonDatasetAfterRank(self, feature_file, pred_file):
        fs = open(self.sourcefile, "r", encoding="UTF-8")
        fp = open(pred_file,"r",encoding="UTF-8")
        scores = [float(score.strip()) for score in fp.readlines()]
        #features = np.load(feature_file)
        total_dict = json.load(fs)
        idx = -1
        for key in total_dict.keys():
            for tmp_dict in total_dict[key]:
                idx += 1
                #tmp_dict["onehop_path_score"] = features[idx][-2]
                #tmp_dict["twohop_path_score"] = features[idx][-1]
                tmp_dict["entity_score"] = scores[idx]
        fs.close()
        ft = open(self.sourcefile, "w", encoding="UTF-8")
        json.dump(total_dict, ft, ensure_ascii=False, indent=4)


def GenerateDataset4NER(train_flag:int=1):
    resource = rs.Resource()
    if train_flag == 1:
        mentionfile = resource.train_mention_file
        questionfile = resource.train_question_file
        targetfile = resource.train_ner_file
        TNER = NameEntityRecognize(
            mention_file=mentionfile,
            question_file=questionfile,
            target_file=targetfile
        )
        TNER.GenerateTrainData()
    elif train_flag == 0:
        mentionfile = resource.dev_mention_file
        questionfile = resource.dev_question_file
        targetfile = resource.dev_ner_file
        DNER = NameEntityRecognize(
            mention_file=mentionfile,
            question_file=questionfile,
            target_file=targetfile
        )
        DNER.GenerateTrainData()

def GenerateDataset4EntityLink(train_flag):
    resource = rs.Resource()
    if train_flag:
        # mentionfile = resource.train_mention_file
        mentionfile = "data/Task/Train/train_hardmatch_ner_result_all.txt"
        questionfile = resource.train_question_file
        # targetfile = resource.train_entity_4train_file
        targetfile = "data/Task/Train/train_elink.json"
        entityfile = resource.train_entity_file
    else:
        # mentionfile = resource.dev_mention_file
        mentionfile = "data/Task/Dev/dev_combine_all_ner_results_with_ir.txt"
        questionfile = resource.dev_question_file
        # targetfile = resource.dev_entity_4dev_file
        targetfile = "data/Task/Dev/dev_elink.json"
        entityfile = resource.dev_entity_file
    EL = EntityLink(mentionfile, questionfile, targetfile)
    EL.GenerateJsonDataSet4Train(entityfile)


def GenerateDataset4EntityClassify(train_flag):
    resource = rs.Resource()
    if train_flag:
        # train_sourcefile = resource.train_entity_4train_file
        # train_sourcefile = resource.train_entity_filter_4train_file
        train_sourcefile = "data/Task/Train/train_elink.json"
        train_questionfile = resource.train_question_file
        train_targetfile = resource.entityclassifier_train_path
        EC = EntityClassifier(train_sourcefile, train_targetfile, train_questionfile, 1)
        EC.GenerateDataSetByJson()
        # dev_sourcefile = resource.dev_entity_4dev_file
        # dev_sourcefile = resource.dev_entity_filter_4dev_file
        dev_sourcefile = "data/Task/Dev/dev_elink.json"
        dev_questionfile = resource.dev_question_file
        dev_targetfile = resource.entityclassifier_dev_path
        EC = EntityClassifier(dev_sourcefile, dev_targetfile, dev_questionfile, 0)
        EC.GenerateDataSetByJson()
    else:
        test_sourcefile = resource.test_entity_4test_file
        test_questionfile = resource.test_question_file
        test_targetfile = resource.entityclassifier_test_path
        EC = EntityClassifier(test_sourcefile, test_targetfile, test_questionfile, 0)
        EC.GenerateDataSetByJson()


def GenerateDataset4EntityRank(train_flag):
    resource = rs.Resource()
    # if train_flag:
    # train_sourcefile = resource.train_entity_4train_file
    train_sourcefile = "data/Task/Train/train_elink.json"
    train_targetfile = resource.entityrank_train_path
    train_questionfile = resource.train_question_file
    # train_labelfile = resource.entityclassifier_train_result
    ER = EntityRank(train_sourcefile, train_questionfile, train_targetfile)
    ER.UpdateJsonDatasetAfterRank(feature_file=None,
                                  pred_file="data/ModelDataset/EntityRank/WithRelation/train_results.txt")
    # ER.UpdateJsonDataset()
    # ER.GenerateData4EntityRankWithRelation("data/ModelDataset/EntityRank/WithRelation/train.txt",False)
    # else:
    # dev_sourcefile = resource.dev_entity_4dev_file
    # dev_sourcefile = "data/Task/Dev/dev_elink.json"
    # dev_targetfile = resource.entityrank_dev_path
    # dev_questionfile = resource.dev_question_file
    # dev_labelfile = resource.entityclassifier_dev_result
    # ER = EntityRank(dev_sourcefile, dev_questionfile, dev_targetfile)
    # ER.UpdateJsonDatasetAfterRank()
    # ER.UpdateJsonDataset()
    # ER.GenerateData4EntityRank()
    # ER.GenerateData4EntityRankWithRelation("data/ModelDataset/EntityRank/WithRelation/dev.txt",False)
    """else:
        test_sourcefile = resource.test_entity_4test_file
        test_targetfile = resource.entityrank_test_path
        test_quesitonfile = resource.test_question_file
        test_labelfile = resource.entityclassifier_test_result
        ER = EntityRank(test_sourcefile,test_quesitonfile,test_labelfile,test_targetfile)
        ER.GenerateData4EntityRank()"""


def GenerateDataset4PredicateClassifier(train_flag):
    resource = rs.Resource()
    if train_flag:
        flag = True
        # train_entity_file = resource.train_entity_4train_file
        train_entity_file = "data/Task/Train/train_elink.json"
        # train_entity_filter_file = resource.train_entity_filter_4train_file
        train_question_file = resource.train_question_file
        train_standard_predicate_file = resource.train_predicate_file
        # train_predicate_file = resource.train_predicate_4train_file
        train_predicate_file = "data/Task/Train/train_predicates.json"
        train_target_file = "data/ModelDataset/PredicateClassifier/WithMention/train.txt"  # resource.predicateclass_train_path
        PC = NewPredicateClassifier(train_entity_file, train_standard_predicate_file,
                                    train_predicate_file, train_question_file, train_target_file, flag)
        # PC.EntityFilter()
        # PC.GetPredicateJsonFile(True,2)
        # PC.GenerateQRDataset(True)
        PC.GenerateQERDataset(True, False)

        # dev_entity_file = resource.dev_entity_4dev_file
        dev_entity_file = "data/Task/Dev/dev_elink.json"
        # dev_entity_filter_file = resource.dev_entity_filter_4dev_file
        dev_question_file = resource.dev_question_file
        dev_standard_predicate_file = resource.dev_predicate_file
        # dev_predicate_file = resource.dev_predicate_4dev_file
        dev_predicate_file = "data/Task/Dev/dev_predicates.json"
        dev_target_file = "data/ModelDataset/PredicateClassifier/WithMention/dev.txt"  # resource.predicateclass_dev_path
        PC = NewPredicateClassifier(dev_entity_file, dev_standard_predicate_file, dev_predicate_file,
                                    dev_question_file, dev_target_file, flag)
        # PC.EntityFilter()
        # PC.GetPredicateJsonFile(False,2)

        # PC.GenerateQRDataset(False)
        PC.GenerateQERDataset(False, False)

    else:
        flag = False
        test_entity_file = resource.entitylink_result
        test_entity_filter_file = resource.entitylink_result
        test_question_file = resource.test_question_file
        test_standard_predicate_file = ""
        test_predicate_file = resource.test_predicate_4test_file
        test_target_file = "with_mention/test.txt"  # resource.predicateclass_test_path
        PC = PredicateClassifier(test_entity_file, test_entity_filter_file, test_standard_predicate_file,
                                 test_predicate_file,
                                 test_question_file, test_target_file, flag)
        PC.GetDataset4PredicateClassifier()


def GetPath(train_flag):
    resource = rs.Resource()
    if train_flag == 1:
        entity_file = "data/Task/Train/train_elink.json"  # resource.train_entity_filter_4train_file
        target_file = "data/Task/Train/train_path_4train_04_14.txt"  # resource.train_path_4train
        path_file = resource.train_path_file
        question_file = resource.train_question_file
        pr = PathRank(entity_file, target_file, path_file, question_file)
        pr.GeneratePathByStandard()

        """entity_file = "data/Task/Dev/dev_elink.json"#resource.dev_entity_filter_4dev_file
        target_file = "data/Task/Dev/dev_path_4dev_04_14.txt"#resource.dev_path_4dev
        path_file = resource.dev_path_file
        question_file = resource.dev_question_file
        pr = PathRank(entity_file, target_file,path_file,question_file)
        pr.GeneratePathByStandard()"""


def GetNerResult():
    resource = rs.Resource()
    result_file = "/home/pcsong/BERT-NER-Pytorch/outputs/cner_output_span/bert/test_predict.json"
    question_file = resource.dev_question_file
    ner = NameEntityRecognize(result_file=result_file, question_file=question_file,
                              target_file="data/Task/Dev/dev_spanbert_results.txt")
    ner.ExtractEntityFromResultFile()


def GetPathRankFeatures(train_flag):
    resource = rs.Resource()
    if train_flag == 1:
        entity_file = "data/Task/Train/train_elink.json"  # resource.train_entity_filter_4train_file
        path_file = "data/Task/Train/train_path_4train_04_14.txt"  # "data/Task/Train/train_path_4train_07_09.txt"
        question_file = resource.train_question_file
        target_file = "data/ModelDataset/PathRank/0309/train_0414.npy"  # resource.pathrank_train_path
        task = "train"
        dir = "data/Task/Train/"
        prf = PathRankFeatures(entity_file, path_file, task, dir, question_file, target_file)
        # prf.GenerateNewPathFile()
        # prf.GeneratePairsForModel()
        # prf.GetFeatures()
        # prf.GetQuestionPathPairs4Pairwise("data/ModelDataset/PathRank/qp_pairs/binary_class/train_0420_pairwise.txt",True)
        # prf.GetQuestionPathPairs("data/ModelDataset/PathRank/qp_pairs/Pairwise/train_0419_pointwise.txt",True)
        # prf.GetDevFinal()
        prf.GetNewFeatures()
    if train_flag == 2:
        entity_file = "data/Task/Dev/dev_elink.json"  # resource.dev_entity_filter_4dev_file
        path_file = "data/Task/Dev/dev_path_4dev_03_10.txt"  # resource.dev_path_4dev
        question_file = resource.dev_question_file
        target_file = "data/ModelDataset/PathRank/0309/dev_new.npy"  # resource.pathrank_dev_path
        task = "dev"
        dir = "data/Task/Dev/"
        prf = PathRankFeatures(entity_file, path_file, task, dir, question_file, target_file)
        # prf.GenerateNewPathFile()
        # prf.GeneratePairsForModel()
        # prf.GetFeatures()
        prf.GetQuestionPathPairs("data/ModelDataset/PathRank/qp_pairs/binary_class/dev_0414.txt", True)
        # prf.GetDevFinal()
        # prf.GetNewFeatures(without_mention=True)
def main():
    parser = argparse.ArgumentParser(description="Demo of argparse")
    parser.add_argument('--task', type=str, default="")
    parser.add_argument('--train', type=int, default=1)
    args = parser.parse_args()
    if args.task == "entitylink":
        GenerateDataset4EntityLink(args.train)
    elif args.task == "entityclassifier":
        GenerateDataset4EntityClassify(args.train)
    elif args.task == "entityrank":
        GenerateDataset4EntityRank(args.train)
    elif args.task == "predicateclassifier":
        GenerateDataset4PredicateClassifier(args.train)
    elif args.task == "getpath":
        GetPath(args.train)
    elif args.task == "getnerresult":
        GetNerResult()
    elif args.task == "pathrank":
        GetPathRankFeatures(1)
        #GetPathRankFeatures(2)
    elif args.task == "ner":
        GenerateDataset4NER()
if __name__ == '__main__':
    main()