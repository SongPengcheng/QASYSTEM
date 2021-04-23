#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/23 10:01 上午
# @Author  : SPC
# @FileName: LambdaRankNN-Torch.py
# @Software: PyCharm
# @Desn    : 


import sys
import os
import math
from tqdm import tqdm
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pickle
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
class LambdaRankDataset(Dataset):
    def __init__(self, x1, x2, y, weight):
        self.x1 = x1
        self.x2 = x2
        self.y = y
        self.weight = weight
    def __len__(self):
        return len(self.y)
    def __getitem__(self, item):
        return self.x1[item],self.x2[item],self.y[item],self.weight[item]

class FNN(nn.Module):
    def __init__(self, input_size, hidden_size_one, hidden_size_two, output_size):
        super(FNN,self).__init__()
        self.hidden_layer_one = nn.Linear(input_size, hidden_size_one)
        self.hidden_layer_two = nn.Linear(hidden_size_one,hidden_size_two)
        self.hidden_layer_three = nn.Linear(hidden_size_two,output_size)
    def forward(self, x_1, x_2):
        h_1_x1 = torch.relu(self.hidden_layer_one(x_1))
        h_1_x2 = torch.relu(self.hidden_layer_one(x_2))
        h_2_x1 = torch.relu(self.hidden_layer_two(h_1_x1))
        h_2_x2 = torch.relu(self.hidden_layer_two(h_1_x2))
        h_3_x1 = torch.relu(self.hidden_layer_three(h_2_x1))
        h_3_x2 = torch.relu(self.hidden_layer_three(h_2_x2))
        output = torch.sigmoid(h_3_x1-h_3_x2)
        return output
    def function(self,X):
        h1 = torch.relu(self.hidden_layer_one(X))
        h2 = torch.relu(self.hidden_layer_two(h1))
        output = torch.relu(self.hidden_layer_three(h2))
        return output

class RankerNN(nn.Module):
    def __init__(self, input_size, hidden_size_one, hidden_size_two, output_size):
        super(RankerNN,self).__init__()
        self.model = FNN(input_size, hidden_size_one, hidden_size_two, output_size).cuda()

    @staticmethod
    def _CalcDCG(labels):
        sumdcg = 0.0
        for i in range(len(labels)):
            rel = labels[i]
            if rel != 0:
                sumdcg += ((2 ** rel) - 1) / math.log2(i + 2)
        return sumdcg

    def _fetch_qid_data(self, y, qid, eval_at=None):
        """Fetch indices, relevances, idcg and dcg for each query id.
        :param y: array, shape (n_samples,)
        :param qid: array, shape (n_samples,)
        :param eval_at: integer, The rank position to evaluate dcg and idcg
        :return:
        qid2indices : array, shape (n_unique_qid,), Start index for each qid.
        qid2rel : array, shape (n_unique_qid,),  A list of target labels (relevances) for each qid.
        qid2idcg: array, shape (n_unique_qid,), Calculated idcg@eval_at for each qid.
        qid2dcg: array, shape (n_unique_qid,), Calculated dcg@eval_at for each qid.
        """
        qid_unique, qid2indices, qid_inverse_indices = np.unique(qid, return_index=True, return_inverse=True)
        # get item releveance for each query id
        qid2rel = [[] for _ in range(len(qid_unique))]
        for i, qid_unique_index in enumerate(qid_inverse_indices):
            qid2rel[qid_unique_index].append(y[i])
        # get dcg, idcg for each query id @eval_at
        if eval_at:
            qid2dcg = [self._CalcDCG(qid2rel[i][:eval_at]) for i in range(len(qid_unique))]
            qid2idcg = [self._CalcDCG(sorted(qid2rel[i], reverse=True)[:eval_at]) for i in range(len(qid_unique))]
        else:
            qid2dcg = [self._CalcDCG(qid2rel[i]) for i in range(len(qid_unique))]
            qid2idcg = [self._CalcDCG(sorted(qid2rel[i], reverse=True)) for i in range(len(qid_unique))]
        return qid2indices, qid2rel, qid2idcg, qid2dcg

    def _transform_pairwise(self, X, Y, qid):
        """
        :param X: array, shape(n_samples,)
        :param y: array, shape(n_samples,)
        :param qid: array, shape(n_samples,)
        :return:
        X1_trans shape(k,n_features),
        X2_tans shape(k,n_features),
        Y_trans shape(k,),
        weight shape(k,n_features)
        """
        return None, None, None, None

    def fit(self, x, y, qid, batch_size=32, epoch_size=1):
        """
        :param X: array, shape(n_samples,) from numpy
        :param y: array, shape(n_samples,) from numpy
        :param qid: array, shape(n_samples,) from numpy
        """
        X1_trans, X2_trans, y_trans, weight = self._transform_pairwise(x, y, qid)
        X1_trans = torch.from_numpy(X1_trans).float().cuda()
        X2_trans = torch.from_numpy(X2_trans).float().cuda()
        y_trans = torch.from_numpy(y_trans).float().cuda()
        weight = torch.from_numpy(weight).float().cuda()
        dataset = LambdaRankDataset(X1_trans, X2_trans, y_trans, weight)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        for epoch in range(epoch_size):
            print("epoch "+str(epoch)+"\n")
            iterator = tqdm(dataloader, maxinterval=10,
                            mininterval=2, ncols=80,
                            bar_format='{l_bar}|{bar}| {n_fmt}/{total_fmt} [{rate_fmt}{postfix}|{elapsed}<{remaining}]',
                            nrows=10, smoothing=0.01)
            for x1, x2, y_tmp, w in iterator:
                optimizer.zero_grad()
                output = self.model(x1, x2)
                y_tmp = y_tmp.view(-1,1)
                w = w.view(-1,1)
                criteran = nn.BCELoss(w)
                loss = criteran(output,y_tmp)
                iterator.set_postfix(loss=loss.item())
                iterator.update(1)
                loss.backward()
                optimizer.step()
        self.evaluate(x, y, qid)

    def predict(self,X):
        X = torch.from_numpy(X).float().cuda()
        y = self.model.function(X).cpu()
        return y.detach().numpy()

    def evaluate(self, X, y, qid, eval_at=None):
        """Predict and evaluate ndcg@eval_at.
        Parameters
        ----------
        X : array, shape (n_samples, n_features)
            Features.
        y : array, shape (n_samples,)
            Target labels.
        qid: array, shape (n_samples,)
            Query id that represents the grouping of samples.
        eval_at: integer
            The rank postion to evaluate NDCG.
        Returns
        -------
        ndcg@eval_at: float
        """
        y_pred = self.predict(X)
        tmp = np.array(np.hstack([y.reshape(-1, 1), y_pred.reshape(-1, 1), qid.reshape(-1, 1)]))
        tmp = tmp[np.lexsort((-tmp[:, 1], tmp[:, 2]))]
        y_sorted = tmp[:, 0]
        qid_sorted = tmp[:, 2]
        ndcg = self._EvalNDCG(y_sorted, qid_sorted, eval_at)
        if eval_at:
            print('ndcg@' + str(eval_at) + ': ' + str(ndcg))
        else:
            print('ndcg: ' + str(ndcg))

    def _EvalNDCG(self, y, qid, eval_at=None):
        """Evaluate ndcg@eval_at.
        Calculated ndcg@n is consistent with ndcg@n- in xgboost.
        """
        _, _, qid2idcg, qid2dcg = self._fetch_qid_data(y, qid, eval_at)
        sumndcg = 0
        count = 0.0
        for qid_unique_idx in range(len(qid2idcg)):
            count += 1
            if qid2idcg[qid_unique_idx] == 0:
                continue
            idcg = qid2idcg[qid_unique_idx]
            dcg = qid2dcg[qid_unique_idx]
            sumndcg += dcg / idcg
        return sumndcg / count

class LambdaRankNN(RankerNN):
    def __init__(self, input_size, hidden_size_one, hidden_size_two, output_size):
        super(LambdaRankNN,self).__init__(input_size,hidden_size_one,hidden_size_two,output_size)

    def _transform_pairwise(self, X, y, qid):
        """Transform data into lambdarank pairs with balanced labels for binary classification.
        :param X: array, shape (n_samples, n_features), set for features
        :param y: array, shape (n_samples,), set for target labels
        :param qid: array, shape (n_samples,), Query id that represents the grouping of samples.
        :return: k is the number of data pairs
        X1_trans : array, shape (k, n_feaures) Features of pair 1
        X2_trans : array, shape (k, n_feaures) Features of pair 2
        weight: array, shape (k, n_faetures) Sample weight lambda.
        y_trans : array, shape (k,) Output class labels, where classes have values {0, 1}
        """
        qid2indices, qid2rel, qid2idcg, _ = self._fetch_qid_data(y, qid)
        X1 = []
        X2 = []
        weight = []
        Y = []
        for qid_unique_idx in range(len(qid2indices)):
            if qid2idcg[qid_unique_idx] == 0:
                continue
            IDCG = 1.0 / qid2idcg[qid_unique_idx]
            rel_list = qid2rel[qid_unique_idx]
            qid_start_idx = qid2indices[qid_unique_idx]
            for pos_idx in range(len(rel_list)):
                for neg_idx in range(len(rel_list)):
                    if rel_list[pos_idx] <= rel_list[neg_idx]:
                        continue
                    # calculate lambda
                    pos_loginv = 1.0 / math.log2(pos_idx + 2)
                    neg_loginv = 1.0 / math.log2(neg_idx + 2)
                    pos_label = rel_list[pos_idx]
                    neg_label = rel_list[neg_idx]
                    original = ((1 << pos_label) - 1) * pos_loginv + ((1 << neg_label) - 1) * neg_loginv
                    changed = ((1 << neg_label) - 1) * pos_loginv + ((1 << pos_label) - 1) * neg_loginv
                    delta = (original - changed) * IDCG
                    if delta < 0:
                        delta = -delta
                    # balanced class
                    if 1 != (-1) ** (qid_unique_idx + pos_idx + neg_idx):
                        X1.append(X[qid_start_idx + pos_idx])
                        X2.append(X[qid_start_idx + neg_idx])
                        weight.append(delta)
                        Y.append(1)
                    else:
                        X1.append(X[qid_start_idx + neg_idx])
                        X2.append(X[qid_start_idx + pos_idx])
                        weight.append(delta)
                        Y.append(0)
        return np.asarray(X1), np.asarray(X2), np.asarray(Y), np.asarray(weight)



