#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/26 10:21 上午
# @Author  : SPC
# @FileName: test.py
# @Software: PyCharm
# @Desn    : 
twohop_obj in entities and not (twohop_obj == root and twohop_predicate == onehop_predicate) and not (two_obj_mention == root_mention and twohop_obj != root) and twohop_predicate != "<类型>":


def Filter(self, entity, entity_mention, root, root_mention, predicate, root_predicate):
    flag = entity in self.entities and \
        not (entity == root and predicate == root_predicate) and \
        not ((entity == root) or (entity_mention == root_mention) or (entity_mention in root_mention) or (root_mention in entity_mention)) and \
        not (entity == root and entity_mention == root_mention) and \
        predicate != "<类型>"
    return flag
