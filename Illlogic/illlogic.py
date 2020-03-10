# -*- coding: utf-8 -*-
"""
hoge hoge logic module
"""
import numpy as np

__author__ = "bstrance"
__status__ = "Prototype"
__version__ = "0.0.1"
__date__ = "2020.3.6"

class illLogic(object):

    __table_size = 10
    on_mark = "■"
    off_mark = "□"
    __table = []
    __col_hint = np.empty(__table_size, dtype=str)
    __row_hint = np.empty(__table_size, dtype=str)

    def __init__(self, size=None):
        if not size:
            size = 10
        self.__table_size = size
        self.__table = self.create_rand_table(size)
        self.__col_hint = np.empty(size, dtype=str)
        self.__row_hint = np.empty(size, dtype=str)

    def set_table(self, table):
        self.__table = table
        self.__table_size = table.shape[0]

    def get_table_size(self):
        return self.__table_size

    def get_table(self):
        return self.__table

    def get_hint(self):
        return self.__col_hint, self.__row_hint

    def set_all_zero_table(self, table=None):
        if not table:
            table = self.__table
        return np.zeros_like(table)

    def create_rand_table(self, size=None):
        if not size:
            size = self.__table_size
        table = np.random.randint(0, 2, (size, size))
        #return self.add_hint(table)
        return table

    def create_hint_table(self, table=None):
        if not table:
            table = self.__table
        self.__col_hint = self.__gen_hint(table)
        self.__row_hint = self.__gen_hint(table.T)
        return self.__col_hint, self.__row_hint

    def __gen_hint(self, table):
        k = 0
        hint = []
        for i in table:
            label =[]
            label_temp = 0

            for cell in i:
                if cell == 0 and label_temp != 0:
                    label.append(label_temp)
                    label_temp = 0
                elif cell == 1:
                    label_temp += 1

            if label_temp != 0:
                label.append(label_temp)
            hint.append(label)
            k += 1
        return hint

    def num2cells(self, table=None):
        if not table:
            table = self.__table
        return np.where(table[:self.__table_size, :self.__table_size] == 1, self.on_mark, self.off_mark)

    def cells2num(self, table=None):
        if not table:
            table = self.__table
        return np.where(table[:self.__table_size, :self.__table_size] == self.on_mark, 1, 0)

q = illLogic(10)
#print(q.table)
print(q.create_hint_table())
print(q.num2cells())