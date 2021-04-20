#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/20 9:25 上午
# @Author  : SPC
# @FileName: Evaluate.py
# @Software: PyCharm
# @Desn    :

import argparse
def precision_score(true_list,pred_list):
    intersection_num = 0
    for i,pred_word in enumerate(pred_list):
        if pred_word in true_list:
            intersection_num += 1
    if len(pred_list) != 0:
        precision_score = intersection_num/len(pred_list)
    else:
        precision_score = 0
    return precision_score
def recall_score(true_list,pred_list):
    intersection_num = 0
    for i,pred_word in enumerate(pred_list):
        if pred_word in true_list:
            intersection_num += 1
    if len(true_list) != 0:
        recall_score = intersection_num/len(true_list)
    else:
        recall_score = 0
    return recall_score
def f1_score(true_list,pred_list):
    p_score = precision_score(true_list,pred_list)
    r_score = recall_score(true_list,pred_list)
    if p_score+r_score == 0:
        return 0
    else:
        f1_score = p_score*r_score*2/(p_score+r_score)
        return f1_score
def evauate(true_file,pred_file,split_mark):
    true_lines = open(true_file, "r", encoding="UTF-8").readlines()
    pred_lines = open(pred_file, "r", encoding="UTF-8").readlines()
    num = 0
    p_score = 0
    r_score = 0
    f_score = 0
    for i, true_line in enumerate(true_lines):
        true_list = list(set(true_line.strip("|||").strip("\n").split(split_mark)))
        pred_list = list(set(pred_lines[i].strip("|||").strip("\n").split(split_mark)))
        if recall_score(true_list, pred_list) < 1 or precision_score(true_list, pred_list) < 1:
            print(i)
        p_score += precision_score(true_list, pred_list)
        r_score += recall_score(true_list, pred_list)
        f_score += f1_score(true_list, pred_list)
        num += 1
    print("macro acc:"+str(p_score/num))
    print("macro rec:"+str(r_score/num))
    print("macro  f1:"+str(f_score/num))
def main():
    parser = argparse.ArgumentParser(description="Demo of argparse")
    parser.add_argument('--true_file', type=str, default="")
    parser.add_argument('--pred_file', type=str, default="")
    parser.add_argument("--split_mark", type=str, default="\t")
    args = parser.parse_args()
    evauate(args.true_file,args.pred_file,args.split_mark)
if __name__ == '__main__':
    main()


