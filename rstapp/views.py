from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from pandas.api.types import is_numeric_dtype

import pandas as pd
import xlwt
from xlwt import Workbook
from itertools import combinations
import pandas as pd
import numpy as np
from .FuncAni_2 import *
import time
from datetime import datetime
from .models import *
import pytz

# storage variables used
dict_col = {}   # stores cardinal nos. of element values column-wise as well as unique data-wise
elemen_list = []    # stores elementary list numbers of conditional attributes
cris_list = []  # stores crisp set numbers of decision attribute
list_col = []   # stores names of columns
list_combi = []     # stores combinations of columns as tuples
elem_indiscern_2_list = []  # stores List of all indiscernible combinations taking double conditional attributes
elem_list = []  # stores elementary set numbers of conditional attributes
dict_low = {}   # stores lower bound set
dict_upp = {}   # stores upper bound set
dict_accu = {}  # stores accuracy of parameters
dict_SI = {}    # stores stability index of parameters
dict_boun = {}  # stores boundary region of each combinations
dict_out = {}   # stores outside region of each combinations
elem_dict = {}  # stores elementary list and dict numbers of conditional attributes
elemen_dict = {}    # stores elementary dict numbers of conditional attributes
dict_indiscern_2 = {}   # stores elementary list for double conditional attributes

finalop = {}
headings = ['Timestamp', 'Decision Value', 'n(LA)',  'n(UA)', 'Accuracy', 'Stability Index']
for i in range(len(headings)):
    finalop[headings[i]] = []

# Create your views here.
def index(request):
    headings = ['Timestamp', 'Decision Value', 'n(LA)',  'n(UA)', 'Accuracy', 'Stability Index']

    if request.method == 'POST':
        if 'file' in request.POST:
            finalop.clear()
            for i in range(len(headings)):
                finalop[headings[i]] = []

            file = request.FILES['myfile']
            df = pd.read_csv(file)
            print(df)

            last_outputs.objects.all().delete()

            index = df.index
            columns = df.columns
            values = df.values
            num_col = df.shape[1]
            num_row = df.shape[0]


            obj_elem_set = set()    # stores serial number of each object as set elements
            for i in range(1, df.shape[0]+1):
                obj_elem_set.add(i)
            
            # storage variables used
            dict_col = {}   # stores cardinal nos. of element values column-wise as well as unique data-wise
            elemen_list = []    # stores elementary list numbers of conditional attributes
            cris_list = []  # stores crisp set numbers of decision attribute
            list_col = []   # stores names of columns
            list_combi = []     # stores combinations of columns as tuples
            elem_indiscern_2_list = []  # stores List of all indiscernible combinations taking double conditional attributes
            elem_list = []  # stores elementary set numbers of conditional attributes
            dict_low = {}   # stores lower bound set
            dict_upp = {}   # stores upper bound set
            dict_accu = {}  # stores accuracy of parameters
            dict_SI = {}    # stores stability index of parameters
            dict_boun = {}  # stores boundary region of each combinations
            dict_out = {}   # stores outside region of each combinations
            elem_dict = {}  # stores elementary list and dict numbers of conditional attributes
            elemen_dict = {}    # stores elementary dict numbers of conditional attributes
            dict_indiscern_2 = {}   # stores elementary list for double conditional attributes
            dict_nla = {}   # stores cardinal no. of Lower Approximation set
            dict_nua = {}   # stores cardinal no. of Upper Approximation set

            for column in columns:  # stores names of columns
                list_col.append(column)
            list_col.pop()  # don't include decision attribute (last column)

            len_combi = num_col - 1
            col_combi = combinations(list_col, len_combi)   # stores combinations of columns taken 'len_combi' at a time
            list_combi = list(col_combi)    # stores combinations of columns as tuples


            # PandasAgeWalkFunc class object created
            obj_item = RST_Parameter_Calc(df)

            # obtain complete serial numbers of all unique conditional and decision attributes as a dictionary
            dict_col = obj_item.col_item_split()

            # obtain elementary set and crisp set
            elem_dict = obj_item.elem_list(dict_col)
            elemen_list = elem_dict['Elem List']
            cris_list = elemen_list.pop()
            elemen_dict = elem_dict['Elem Dict']
            rem_key = columns[-1]
            elemen_dict.pop(rem_key)


            # print("Elementary List for Single-Conditional Attributes: \n" + str(elemen_list) + "\n")
            # print("Crisp List: " + str(cris_list) + "\n")
            # print("Elementary Dictionary: " + str(elemen_dict) + "\n")

            # Returns elementary list for multiple conditional attributes
            dict_indiscern_2 = obj_item.column_combinations(elemen_dict, list_combi)
            # print("List of all indiscernible combinations taking multiple conditional attributes is as follows: ")
            # print(str(dict_indiscern_2) + "\n")

            for val in dict_indiscern_2.values():
                elem_indiscern_2_list.append(val)
            # print("Elementary List for Multi-Conditional Attributes: \n" + str(elem_indiscern_2_list) + "\n")
            elem_list = elem_indiscern_2_list   # for multiple conditional attributes

            dec_items = sorted(list(set(df[columns[-1]].unique())))
            len_dec = len(dec_items)

            # print("Lower and Upper Approximations are given below: ")
            for i in range(0, len_dec): # calculating the RST Parameters
                dec_val = dec_items[i]
                # print("RST LA, UA for Decision Attribute Value: " + str(dec_val))
                dict_low = obj_item.low_approx(dec_val, dict_col, elem_list, list_combi)    # obtain lower approximation
                dict_upp = obj_item.upp_approx(dec_val, dict_col, elem_list, list_combi)    # obtain upper approximation
                # print("Lower Approximation: " + str(dict_low) + "\n")
                # print("Upper Approximation: " + str(dict_upp) + "\n")
                for key in dict_low.keys():  # length of either dict_low or dict_upp; both are equal to no. of CAs taken at a time
                    dict_nla[dec_val] = len(dict_low[key])    # no. of elements in la
                    dict_nua[dec_val] = len(dict_upp[key])    # no. of elements in ua
                dict_accu[dec_val] = obj_item.get_accu(dict_low, dict_upp)  # obtain accuracy parameter using accuracy = nLa/nUa
                dict_SI[dec_val] = obj_item.get_SI(dict_low, dict_upp, len(obj_elem_set))  # obtain stability index(SI) parameter using SI = (n_la + n_ua + 1)/(n + 1) - 0.5
                dict_boun[dec_val] = obj_item.get_boundary(dict_low, dict_upp)  # get boundary region
                dict_out[dec_val] = obj_item.get_outside_region(obj_elem_set, dict_upp) # get outside region

            for key in dict_accu.keys():
                dict_accu[key] = round(dict_accu[key],2)

            for key in dict_SI.keys():
                dict_SI[key] = round(dict_SI[key],2)

            print("Accuracy of the parameters for each decision attribute is given below: ")
            print(str(dict_accu) + "\n")
            print("Stability Index(SI) of the parameters for each decision attribute is given below: ")
            print(str(dict_SI) + "\n")


            list_of_all_outputs = [dict_nla,dict_nua,dict_accu,dict_SI]
            x = last_outputs(args=list_of_all_outputs)
            x.save()

            new_row = []
            for i in range(0, len_dec):
                now = datetime.now()    # current date and time
                date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
                dec_val = dec_items[i]
                new_row = [date_time, dec_val, dict_nla[dec_val], dict_nua[dec_val], dict_accu[dec_val], dict_SI[dec_val]]
                for i in range(len(new_row)):
                    finalop[headings[i]].append(new_row[i])
                
            print(finalop)

        elif 'dwld-rst' in request.POST:
            if (len(finalop['Timestamp'])!=0):
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="Output_File.xls"'
                wb = Workbook()
                sheet1 = wb.add_sheet('Sheet 1')
                for i in range(0,len(headings)):
                    sheet1.write(0, i, headings[i])
                row = 1
                for i in range(len(finalop[headings[i]])):
                    for j in range(len(headings)):
                        sheet1.write(row,j,str(finalop[headings[j]][i]))
                    row = row + 1
                wb.save(response)
                return response
            else:
                return HttpResponse("<h1>Upload a file first!</h1>")



        elif 'missing-attribute-file' in request.POST:
            print("Missing file uploaded")
            file = request.FILES['missing-file']
            df = pd.read_csv(file)
            df2 = df.copy()

            for column in df2:
                if is_numeric_dtype(df2[column]) :
                    df2[column] = df2[column].replace(np.nan,-1)
                else:
                    df2[column],unique = pd.factorize(df2[column],sort = True)

            real = df.to_numpy()
            num_row, num_col = df2.shape

            arr = df2.to_numpy()             #converting to a numpy array for better single-element access
            copy_arr =  np.copy(arr)
            exclude_row = []
            exclude_col = [] #keep track of the rows with missing attributes
            special = -1

            for i in range(0,num_row):      
                for j in range(0,num_col):
                    if copy_arr[i][j]==special:         #-1 stands for a missing value 
                        exclude_row.append(i)
                        exclude_col.append(j)

            max_min_diff = []
            for i in range(0,num_col):
                t_min = 1000 
                t_max = 0
                for j in range(0,num_row):        
                    if copy_arr[j][i]==special:
                        continue
                    if copy_arr[j][i]>t_max:           
                        t_max = copy_arr[j][i]
                        
                    if copy_arr[j][i]<t_min:
                        t_min = copy_arr[j][i]
                max_min_diff.append(t_max - t_min)#code works fine till here

            print(max_min_diff)

            for i in range(len(exclude_col)):
                target = 0 
                col_pos = 0 
                final_distance = 1000
                for j in range(0,num_row):
                    distance = 0.0
                    if(j==exclude_row[i]):  #Exclude the missing attribute row 
                        continue
                    for k in range(0,num_col):
                        if (copy_arr[j][k] == -1 ):
                            distance += 1 ;   # Adding 1 in exceptional case(i.e. case with missing attribute in other row)
                        else:
                            distance = distance + abs( float(copy_arr[j][k] - copy_arr[exclude_row[i]][k])/float(max_min_diff[k]) )
                            # Finding distance 
                        
                    if(distance < final_distance and (copy_arr[j][exclude_col[i]]!= -1)):
                        final_distance = distance
                        target = j
                
                        
                real[exclude_row[i]][exclude_col[i]] = real[target][exclude_col[i]]
                print(target)
                print(real[exclude_row[i]][exclude_col[i]])
                arr[exclude_row[i]][exclude_col[i]] = copy_arr[target][exclude_col[i]]
              #  dup = dup[1:] 
               # print(dup)
                
            t1 = list(range(0,num_row))     #converting from numpy back to a dataframe
            temp = pd.DataFrame(real,t1,df.columns)
            temp2 = pd.DataFrame(arr,t1,df.columns)


            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="Missing_Attribute_Solution.xls"'
            wb = Workbook()
            sheet1 = wb.add_sheet('Sheet 1')
            headings = temp.columns.values.tolist()
            for i in range(0,len(headings)):
                sheet1.write(0, i, headings[i])
            row = 1
            # for i in range(len(finalop[headings[i]])):
            #     for j in range(len(headings)):
            #         sheet1.write(row,j,str(finalop[headings[j]][i]))
            #     row = row + 1
            headings = temp.columns.values.tolist()
            rows = df.shape[0]
            cols = df.shape[1]
            
            for i in range(rows):
                for j in range(cols):
                    sheet1.write(row,j,str(temp.loc[i,headings[j]]))
                row = row + 1
            wb.save(response)
            return response

        
    if (len(last_outputs.objects.all()) > 0):
        display_outputs = last_outputs.objects.last().args
    else:
        display_outputs = []

    return render(request, 'rstapp/index.html',
        {
        'display_outputs':display_outputs,
        }
    )

def using_ajax(request):
    if 'threshold_button' in request.POST:
        threshold.objects.all().delete()
        t = request.POST['threshold_input']
        a = threshold(value=t)
        a.save()

    elif 'link_button' in request.POST:
        github.objects.all().delete()
        stability_index.objects.all().delete()
        dates.objects.all().delete()

        l = request.POST['link_input']
        a = github(link=l)
        a.save()

    current_link = github.objects.last().link
    
    return render(request, 'rstapp/ajax_page.html',{
        'current_link':current_link
        })

def ajaxjson(request):
    # url = "https://raw.githubusercontent.com/prasad2309/input_dataset/main/temp.csv"
    url = str(github.objects.last().link)
    print(url)
    try:
        df = pd.read_csv(url)
        print("Read file successfully")
    except:
        return HttpResponse("<h1>Enter a valid file link!</h1>")
    
    index = df.index
    columns = df.columns
    values = df.values
    num_col = df.shape[1]
    num_row = df.shape[0]


    obj_elem_set = set()    # stores serial number of each object as set elements
    for i in range(1, df.shape[0]+1):
        obj_elem_set.add(i)
    
    dict_col = {}   # stores cardinal nos. of element values column-wise as well as unique data-wise
    elemen_list = []    # stores elementary list numbers of conditional attributes
    cris_list = []  # stores crisp set numbers of decision attribute
    list_col = []   # stores names of columns
    list_combi = []     # stores combinations of columns as tuples
    elem_indiscern_2_list = []  # stores List of all indiscernible combinations taking double conditional attributes
    elem_list = []  # stores elementary set numbers of conditional attributes
    dict_low = {}   # stores lower bound set
    dict_upp = {}   # stores upper bound set
    dict_accu = {}  # stores accuracy of parameters
    dict_SI = {}    # stores stability index of parameters
    dict_boun = {}  # stores boundary region of each combinations
    dict_out = {}   # stores outside region of each combinations
    elem_dict = {}  # stores elementary list and dict numbers of conditional attributes
    elemen_dict = {}    # stores elementary dict numbers of conditional attributes
    dict_indiscern_2 = {}   # stores elementary list for double conditional attributes
    dict_nla = {}   # stores cardinal no. of Lower Approximation set
    dict_nua = {}   # stores cardinal no. of Upper Approximation set

    for column in columns:  # stores names of columns
        list_col.append(column)
    list_col.pop()  # don't include decision attribute (last column)

    len_combi = num_col - 1
    col_combi = combinations(list_col, len_combi)   # stores combinations of columns taken 'len_combi' at a time
    list_combi = list(col_combi)    # stores combinations of columns as tuples


    # PandasAgeWalkFunc class object created
    obj_item = RST_Parameter_Calc(df)

    # obtain complete serial numbers of all unique conditional and decision attributes as a dictionary
    dict_col = obj_item.col_item_split()
    # print(dict_col)

    # obtain elementary set and crisp set
    elem_dict = obj_item.elem_list(dict_col)
    elemen_list = elem_dict['Elem List']
    cris_list = elemen_list.pop()
    elemen_dict = elem_dict['Elem Dict']
    rem_key = columns[-1]
    elemen_dict.pop(rem_key)

    dict_indiscern_2 = obj_item.column_combinations(elemen_dict, list_combi)

    for val in dict_indiscern_2.values():
        elem_indiscern_2_list.append(val)
    elem_list = elem_indiscern_2_list   # for multiple conditional attributes

    dec_items = sorted(list(set(df[columns[-1]].unique())))
    len_dec = len(dec_items)

    for i in range(0, len_dec): # calculating the RST Parameters
        dec_val = dec_items[i]
        # print("RST LA, UA for Decision Attribute Value: " + str(dec_val))
        dict_low = obj_item.low_approx(dec_val, dict_col, elem_list, list_combi)    # obtain lower approximation
        dict_upp = obj_item.upp_approx(dec_val, dict_col, elem_list, list_combi)    # obtain upper approximation
        # print("Lower Approximation: " + str(dict_low) + "\n")
        # print("Upper Approximation: " + str(dict_upp) + "\n")
        for key in dict_low.keys():  # length of either dict_low or dict_upp; both are equal to no. of CAs taken at a time
            dict_nla[dec_val] = len(dict_low[key])    # no. of elements in la
            dict_nua[dec_val] = len(dict_upp[key])    # no. of elements in ua
        dict_accu[dec_val] = obj_item.get_accu(dict_low, dict_upp)  # obtain accuracy parameter using accuracy = nLa/nUa
        dict_SI[dec_val] = obj_item.get_SI(dict_low, dict_upp, len(obj_elem_set))  # obtain stability index(SI) parameter using SI = (n_la + n_ua + 1)/(n + 1) - 0.5
        dict_boun[dec_val] = obj_item.get_boundary(dict_low, dict_upp)  # get boundary region
        dict_out[dec_val] = obj_item.get_outside_region(obj_elem_set, dict_upp) # get outside region

    print("Accuracy of the parameters for each decision attribute is given below: ")
    print(str(dict_accu) + "\n")
    print("Stability Index(SI) of the parameters for each decision attribute is given below: ")
    print(str(dict_SI) + "\n")

    a = stability_index(args=dict_SI)
    a.save()

    list_of_all_outputs = [dict_nla,dict_nua,dict_accu,dict_SI]
    x = last_outputs(args=list_of_all_outputs)
    x.save()

    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    d = dates(date = date_time)
    d.save()

    new_row = []
    for i in range(0, len_dec):
        now = datetime.now()    # current date and time
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
        dec_val = dec_items[i]
        new_row = [date_time, dec_val, dict_nla[dec_val], dict_nua[dec_val], dict_accu[dec_val], dict_SI[dec_val]]
        for i in range(len(new_row)):
            finalop[headings[i]].append(new_row[i])
            
    query_results1 = stability_index.objects.all()

    thresh = 0.0
    if(threshold.objects.last()):
        thresh = threshold.objects.last().value

    chart_data = [];
    decision_attributes = []

    if(len(query_results1) != 0):
        decision_attributes = list((query_results1[0].args).keys())

        print(type(decision_attributes[0]))

        if(isinstance(decision_attributes[0],np.int64)):
            for i in range(len(decision_attributes)):
                decision_attributes[i] = int(decision_attributes[i])


        k = list((query_results1[0].args).keys())
        for key in k:
            temp = []
            for i in range(len(query_results1)):
                temp.append((query_results1[i].args)[key])
            chart_data.append(temp)

    query_results2 = list(dates.objects.all())
    chart_dates = []
    for item in query_results2:
        chart_dates.append(item.date)

    return JsonResponse({'chart_data':chart_data,'chart_dates':chart_dates,'decision_attributes':decision_attributes,'thresh':thresh})

def usage(request):
    return render(request, 'rstapp/usage.html')

    



