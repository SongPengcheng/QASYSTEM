#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 3:54 下午
# @Author  : SPC
# @FileName: BertModule.py
# @Software: PyCharm
# @Desn    : 
import BertModule.LoadBertModel as LoadBertModel
class BertModule(object):
    def __init__(
            self,
            model_path:str=None
    ):
        super(BertModule,self).__init__()
        self.predictor, self.tokenizer = LoadBertModel.LoadModel(model_path)
    def ScoreByModel(self, text_pairs):
        return LoadBertModel.PredictByTextPairs(self.predictor, self.tokenizer, text_pairs)
