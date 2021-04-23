#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 4:53 下午
# @Author  : SPC
# @FileName: RankModel.py
# @Software: PyCharm
# @Desn    : 

import pickle
import torch
import numpy as np

class RankModel(object):
    def __init__(self, model_path:str=None):
        self.model_path = model_path
        self.model = self.LoadModel()
    def LoadModel(self):
        return None
    def ScoreByModel(self,data):
        test_data = np.array(data)
        test_X = test_data[:, 2:].tolist()
        test_X = np.array(test_X)
        y_pred = self.model.predict(test_X)
        results = y_pred.tolist()
        return results

class RankModelKeras(RankModel):
    def __init__(self, model_path:str=None):
        self.model_path = model_path
        self.model = self.LoadModel()
    def LoadModel(self):
        with open(self.model_path, "rb") as fs:
            model = pickle.load(fs)
            return model

class RankModelTorch(object):
    def __init__(self, model_path:str=None):
        self.model_path = model_path
        self.model = self.LoadModel()
    def LoadModel(self):
        return torch.load(self.model_path)