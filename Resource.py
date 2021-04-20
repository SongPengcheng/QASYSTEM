#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 9:29 上午
# @Author  : SPC
# @FileName: Resource.py
# @Software: PyCharm
# @Des     : 对一些文件的路径进行预定义


class Resource(object):
    def __init__(self):
        #定义数据的根路径
        self.data_path = "data/"
        #定义知识库路径
        self.kb_path = self.data_path+"Knowledge/"
        #定义知识库三元组文件路径
        self.triple_path = self.kb_path+"pkubase-complete/pkubase-complete.txt"
        #定义知识库三元组索引路径
        self.triple_idx_path = self.triple_path+".index.pkl"
        #定义知识库反向三元组文件路径
        self.triple_v2e_path = self.kb_path + "pkubase-complete/pkubase-complete-v2e.txt"
        #定义知识库反向三元组索引文件路径
        self.triple_v2e_idx_path = self.triple_v2e_path+".index.pkl"
        #定义mention2entity文件路径
        self.m2e_path = self.kb_path+"pkubase-mention2ent/pkubase-mention2ent.txt"
        #定义mention2entity索引文件路径
        self.m2e_idx_path = self.m2e_path+".index.pkl"
        #定义entity2mention文件路径
        self.e2m_path = self.kb_path+"pkubase-mention2ent/pkubase-ent2mention.txt"
        #定义entity2mention索引文件路径
        self.e2m_idx_path = self.e2m_path+".index.pkl"
        #定义任务数据路径
        self.task_path = self.data_path+"Task/"
        #定义训练数据问题文件路径
        self.train_question_file = self.task_path+"Train/train_questions.txt"
        #定义训练数据mention文件路径
        self.train_mention_file = self.task_path + "Train/train_mentions.txt"
        # 定义训练数据NER文件路径
        self.train_ner_file = self.task_path + "Train/train_ner.txt"
        # 定义用于进行实体链接的实体训练数据的正例
        self.train_entity_file = self.task_path + "Train/train_entities.txt"
        # 定义用于进行谓词匹配的实体训练数据的正例
        self.train_predicate_file = self.task_path + "Train/train_predicates.txt"
        # 定义用于进行谓词匹配的带噪声的训练数据
        self.train_predicate_4train_file = self.task_path + "Train/train_predicates_4train.txt"
        # 定义用于进行实体链接的实体训练数据
        self.train_entity_4train_file = self.task_path+"Train/train_entity_4train.txt"
        # 定义文件，对训练数据的实体进行筛选，以减小后续生成的谓词匹配训练数据的数据规模
        self.train_entity_filter_4train_file = self.task_path + "Train/train_entity_filter_4train.txt"
        # 定义存放标准查询的文件路径
        self.train_path_file = self.task_path + "Train/train_path_file.txt"
        # 定义存放查询路径的文件路径
        self.train_path_4train = self.task_path + "Train/train_path_4train.txt"
        # 定义验证问题文件路径
        self.dev_question_file = self.task_path + "Dev/dev_questions.txt"
        # 定义验证数据mention文件路径
        self.dev_mention_file = self.task_path + "Dev/dev_mentions.txt"
        # 定义验证数据NER文件路径
        self.dev_ner_file = self.task_path + "Dev/dev_ner.txt"
        # 定义用于进行实体链接的实体验证数据的正例
        self.dev_entity_file = self.task_path + "Dev/dev_entities.txt"
        # 定义用于进行谓词匹配的实体验证数据的正例
        self.dev_predicate_file = self.task_path + "Dev/dev_predicates.txt"
        # 定义用于进行谓词匹配的带噪声的验证数据集
        self.dev_predicate_4dev_file = self.task_path + "Dev/dev_predicate_4dev.txt"
        # 定义用于进行实体链接的实体验证数据
        self.dev_entity_4dev_file = self.task_path + "Dev/dev_entity_4dev.txt"
        # 定义文件，对训练数据的实体进行筛选，以减小后续生成的谓词匹配训练数据的数据规模
        self.dev_entity_filter_4dev_file = self.task_path + "Dev/dev_entity_filter_4dev.txt"
        # 定义存放标准查询的文件路径
        self.dev_path_file = self.task_path + "Dev/dev_path_file.txt"
        # 定义存放查询路径的文件路径
        self.dev_path_4dev = self.task_path + "Dev/dev_path_4dev.txt"
        # 定义测试数据问题文件路径
        self.test_question_file = self.task_path + "Test/test_questions.txt"
        # 定义测试数据NER文件路径
        self.test_ner_file = self.task_path + "Test/test_ner.txt"
        # 定义测试数据标注结果文件路径
        self.test_ner_label_file = self.task_path + "Test/ner_labels.txt"
        # 定义测试数据NER结果文件路径
        self.test_ner_result_file = self.task_path + "Test/ner_result.txt"
        # 定义测试数据硬匹配结果文件路径
        self.test_hard_match_result_file = self.task_path + "Test/hard_match_result.txt"
        # 定义测试数据规则匹配结果文件路径
        self.test_rule_match_result_file = self.task_path + "Test/rule_match_result.txt"
        # 定义测试数据实体识别的结果
        self.test_combine_ner_result_file = self.task_path+"Test/combine_ner_result.txt"
        # 定义测试数据全部实体链接的结果
        self.test_entity_4test_file = self.task_path + "Test/elink.txt"
        # 定义测试数据全部谓词匹配的结果
        self.test_predicate_4test_file = self.task_path + "Test/test_predicate_4test.txt"
        # 定义候选一跳路径的存储文件
        self.test_onehop_candidate_file = self.task_path + "Test/test_onehop_candidate_file.txt"

        # 定义存放模型数据集的路径
        self.modeldata_path = self.data_path + "ModelDataset/"
        # 定义用于实体&问题分类的数据集路径
        self.entityclassifier_path = self.modeldata_path+"EntityClassifier/"
        # 定义用于实体&问题分类的训练数据路径
        self.entityclassifier_train_path = self.entityclassifier_path + "train.txt"
        # 定义用于实体&问题分类的训练数据路径
        self.entityclassifier_train_result = self.entityclassifier_path + "train_result.txt"
        # 定义用于实体&问题分类的验证数据路径
        self.entityclassifier_dev_path = self.entityclassifier_path + "dev.txt"
        # 定义用于实体&问题分类的验证数据路径
        self.entityclassifier_dev_result = self.entityclassifier_path + "dev_result.txt"
        # 定义用于实体&问题分类的测试数据路径
        self.entityclassifier_test_path = self.entityclassifier_path + "test.txt"
        # 定义用于实体&问题分类的测试数据路径
        self.entityclassifier_test_result = self.entityclassifier_path + "test_result.txt"

        #定义用于实体链接结果排序的路径
        self.entityrank_path = self.modeldata_path + "EntityRank/"
        # 定义用于实体链接结果排序的训练数据路径
        self.entityrank_train_path = self.entityrank_path + "train.npy"
        # 定义用于实体链接结果排序的验证数据路径
        self.entityrank_dev_path = self.entityrank_path + "dev.npy"
        # 定义用于实体链接结果排序的测试数据路径
        self.entityrank_test_path = self.entityrank_path + "test.npy"
        # 定义实体链接候选实体排序结果
        self.entityrank_result = self.entityrank_path + "test_entityrank_result.txt"
        # 定义实体链接结果
        self.entitylink_result = self.task_path + "Test/elink_result.txt"

        # 定义用于实体识别的数据集路径
        self.mentionrecognize_path = self.modeldata_path + "MentionRecognize/"
        # 定义用于实体识别的训练数据路径
        self.mentionrecognize_train_path = self.mentionrecognize_path + "train.txt"
        # 定义用于实体识别的验证数据路径
        self.mentionrecognize_dev_path = self.mentionrecognize_path + "dev.txt"
        # 定义用于实体识别的测试数据路径
        self.mentionrecognize_test_path = self.mentionrecognize_path + "test.txt"

        # 定义用于谓词分类的数据集路径
        self.predicateclass_path = self.modeldata_path + "PredicateClassifier/"
        # 定义用于谓词分类的训练数据集路径
        self.predicateclass_train_path = self.predicateclass_path + "train.txt"
        # 定义用于谓词分类的验证数据集路径
        self.predicateclass_dev_path = self.predicateclass_path + "dev.txt"
        # 定义用于谓词分类的测试数据集路径
        self.predicateclass_test_path = self.predicateclass_path + "test.txt"
        # 定义谓词分类的结果数据及路径
        self.predicateclass_test_result = self.predicateclass_path + "test_results_2.tsv"

        #定义用于路径排序的数据集路径
        self.pathrank_path = self.modeldata_path + "PathRank/"
        self.pathrank_train_path = self.pathrank_path + "train.npy"
        self.pathrank_dev_path = self.pathrank_path + "dev.npy"
        self.pathrank_test_path = self.pathrank_path + "test.npy"






