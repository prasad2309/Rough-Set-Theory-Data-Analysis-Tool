import pandas as pd
from itertools import combinations


class RST_Parameter_Calc:

    global dict_combo, dict_col_all, list_keys, dict_col, col_items, index, columns, values, num_rows, num_cols, dict_boundary, dict_outside, col_combi, list_col, dict_lenwise
    col_items = []
    list_keys = []
    col_combi = []
    list_col = []
    dict_keys = {}
    dict_col_all = {}
    dict_boundary = {}
    dict_outside = {}
    dict_lenwise = {}

    def __init__(self, data): # two underscores on either side of __init__
        self.data = data

    def col_item_split(self):

        columns = self.data.columns
        num_rows = self.data.shape[0]

        for column in columns:
            dict_keys = {}
            col_items = sorted(list(set(self.data[column].unique())))   # Forms a list of each unique entry
            # print(col_items)
            # print()
            ser = pd.Series(self.data[column])  # Converts each column entry and its elements into a series
            # print(ser)
            # print()
            for i in range(0, len(col_items)):  # calculates elementary set for single conditional attribute/each column
                list_keys = []
                for j in range(0, num_rows):
                    if ser[j] == col_items[i]:  # compares each entry in a column with each unique column entry
                        list_keys.append((j + 1))   # forms a list of indiscernible entries
                        # print(ser[j] + ', ' + col_items[i])
                        # print(list_keys)
                dict_keys[col_items[i]] = set(list_keys)    # stores elementary sets of the current entry for single CA
            dict_col_all[column] = dict_keys  # stores each column's elementary sets for single cond. attr.
            # print(dict_keys)
            # print()
            # print(dict_col_all)
            # print()

        return dict_col_all

    def elem_list(self, dict_col_all):

        list_all = []
        dict_elem = {}
        dict_combi = {}
        columns = self.data.columns

        for key, value in dict_col_all.items():
            list_col = []
            # print(value)
            # print()
            for val in value.values():  # value itself is a dictionary; accessing value's values
                list_col.append(val)    # stores serial nos. of elementary sets for each unique column entry
                # print(val)
                # print()
            list_all.append(list_col)   # stores lists of serial nos. per unique column entries
            dict_elem[key] = list_col

        dict_combi['Elem Dict'] = dict_elem
        dict_combi['Elem List'] = list_all
        return dict_combi

    def low_approx(self, dec_value, dict_col_all, ele_list, list_col):   # lower approximation calculation

        columns = self.data.columns
        dict_low_approx = {}
        low_apr = set()
        num_cols = self.data.shape[1]
        i = 0
        ctr = 0  # used to check null set condition
        flag = False  # used to check null set condition
        test = dict_col_all[columns[num_cols - 1]]  # stores the decision attribute entries
        sup_set = test[dec_value]  # contains serial nos. set of decision value to be tested

        for elem in ele_list:  # iterate through each column element list
            for se in elem:  # iterate through unique serial nos. list
                if se.issubset(sup_set):    # check for condition of la
                    flag = True
                    ctr += 1
                    if flag:
                        low_apr.update(se)
                        flag = False
            dict_low_approx[list_col[i]] = set(list(low_apr))   # stores la for each cond. attr.
            if not flag and ctr == 0:  # to check and return for null_set condition
                dict_low_approx[list_col[i]] = {}
            low_apr.clear()
            low_apr = set()
            i += 1
            # print(dict_low_approx)

        return dict_low_approx

    def upp_approx(self, dec_value, dict_col_all, ele_list, list_col):   # upper approximations calculation

        columns = self.data.columns
        dict_upp_approx = {}
        num_cols = self.data.shape[1]
        i = 0
        test = dict_col_all[columns[num_cols - 1]]  # stores either of the values of the decision value to be tested
        sup_set = test[dec_value]  # contains cardinal nos. set of decision value
        upp_apr = sup_set.copy()    # since ua comprises of at least chosen decision value's serial nos.

        for elem in ele_list:  # iterate through each column element list
            for se in elem:  # iterate through unique serial nos. list
                if not se.isdisjoint(sup_set):  # check for condition of ua
                    upp_apr.update(se)
            dict_upp_approx[list_col[i]] = set(list(upp_apr))   # stores ua for each cond. attr.
            upp_apr.clear()
            upp_apr = sup_set.copy()
            i += 1

        return dict_upp_approx

    def get_accu(self, dict_la, dict_ua):   # Computes accuracy

        # dict_accuracy = {}
        n_la = 0
        n_ua = 0
        acc = 0.0

        for key in dict_la.keys():  # length of either dict_la or dict_ua; both are equal to no. of CAs taken at a time
            n_la = len(dict_la[key])    # no. of elements in la
            n_ua = len(dict_ua[key])    # no. of elements in ua
            acc = n_la/n_ua             # calculates accuracy for each CAs taken at a time
            # dict_accuracy[key] = acc
            # print(key + " : " + str(n_la) + " / " + str(n_ua) + " = " + str(acc))
            # print(str(n_la) + "\t" + str(n_ua) + "\n") 

        return acc
    
    def get_SI(self, dict_la, dict_ua, n): # computes Stability Index(SI)

        # dict_SI = {}
        n_la = 0
        n_ua = 0
        stab_ind = 0.0

        for key in dict_la.keys():  # length of either dict_la or dict_ua; both are equal to no. of CAs taken at a time
            n_la = len(dict_la[key])    # no. of elements in la
            n_ua = len(dict_ua[key])    # no. of elements in ua
            stab_ind = (n_la + n_ua + 1)/(n + 1) - 0.5            # calculates SI for each CAs taken at a time
            # dict_SI[key] = acc
            # print(key + " : " + str(n_la) + " / " + str(n_ua) + " = " + str(acc))
            print(str(n_la) + "\t" + str(n_ua) + "\t" + str(n) + "\n") 

        return stab_ind

    def get_boundary(self, dict_la, dict_ua):

        temp_set = set()
        for key in dict_la.keys():
            temp_set = dict_ua[key].difference(dict_la[key])  # boundary region = ua - la

        return temp_set

    def get_outside_region(self, elem_set, dict_ua):

        temp_set = set()
        for key in dict_ua.keys():
            temp_set = elem_set.difference(dict_ua[key])    # outside region = U - ua

        return temp_set

    def column_combinations(self, elem_dict, list_col_combi):

        dict_intersect = {}
        list_intersect = []
        temp_list = []
        list_swap = []
        columns = self.data.columns
        num_cols = self.data.shape[1]
        for column in columns:
            list_col.append(column)
        list_col.pop()

        list_A = list_col_combi[0]
        # print(list_A)
        # print()
        list_swap = elem_dict[list_A[0]]
        # print(list_swap)
        # print()
        for elem in range(1, num_cols-1):  # for each column in a combination tuple
            temp_list = elem_dict[list_A[elem]]
            # print(temp_list)
            for se in list_swap:
                for s in temp_list:
                    temp_set = se
                    temp_set = temp_set.intersection(s)
                    if temp_set != set():
                        list_intersect.append(temp_set)
            list_swap = list_intersect
            list_intersect = []

        dict_intersect['Multi-Elementary Set'] = list_swap

        return dict_intersect



