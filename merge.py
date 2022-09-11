import os
import json
import time
from xml.dom import minidom
from bs4 import BeautifulSoup
from tokenizer import *
import pickle
from tfidf import*
import math


def print_indexer(index_dict):
    for token, posting in index_dict.items():
        print(f'token:{token}')
        for post in posting:
            print(post.docid)
        print('===================')


def store_indexer(indexer, file_name1):
    print('store')
    with open(file_name1, 'a+b') as info1:
        for key, value in indexer.items():
            temp = {key: value}
            pickle.dump(temp, info1)


def merge(file_num, n):  # n is total file number that we read in DEV folder
    merged = open("merged.json", "w")
    position = open('position.json', 'w')

    full = [False for i in range(file_num)]
    indicator = -1
    loaded_items = [0 for i in range(file_num)]

    all_indexer_file_pointer = []

    for i in range(file_num):
        file_temp = open(f'indexer_{i}.pickle', 'rb')
        all_indexer_file_pointer.append(file_temp)

    while True:
        for i in range(file_num):
            try:
                if (not full[i]) and loaded_items[i] == 0:
                    indicator = i
                    loaded_items[i] = pickle.load(all_indexer_file_pointer[i])
            except EOFError:
                loaded_items[indicator] = 0
                full[indicator] = True
        if all(full):
            break

        min_dict = merge_min(loaded_items)  #

        # if min_dict is None: # merge min returned nothing

        update_tfidf(min_dict, n)

        for key, value in min_dict.items():
            json.dump({key: merged.tell()}, position)
            position.write('\n')
            json.dump({key: [v.__dict__ for v in value]}, merged)
            merged.write('\n')

        min_token = list(min_dict.keys())[0]

        print("min token is : {}".format(min_token))
        for i in range(len(loaded_items)):
            token_dict = loaded_items[i]
            if (type(token_dict) is dict) and (list(token_dict.keys())[0] == min_token):
                loaded_items[i] = 0

    for pointer in all_indexer_file_pointer:
        pointer.close()


def merge_min(lt):
    # print('-----')
    # current_indexer = None
    minimum = '{'
    min_list = []
    for element in lt:
        if type(element) is int and element == 0:
            continue
        else:
            if list(element.keys())[0] < minimum:
                # current_indexer = lt.index(element)
                minimum = list(element.keys())[0]

    for element in lt:
        if type(element) is int and element == 0:
            continue
        else:
            if list(element.keys())[0] == minimum:
                min_list.append(element)
    if min_list:
        min_dict = min_list[0]
        token = list(min_dict.keys())[0]
        for single_dict in min_list[1:]:
            min_dict[token] += single_dict[token]
        return min_dict
    else:
        return None


# def sub_merge(selected_index):
#     print('submerge')
#     file_0 = open("indexer_0.pickle", 'rb')
#     file_1 = open("indexer_1.pickle", 'rb')
#     file_2 = open("indexer_2.pickle", 'rb')
#     full = [False, False, False]
#     indicator = -1
#     file = [file_0, file_1, file_2]
#     dict_output = {selected_index: []}
#     file_output = open("indexer.pickle", 'a+b')
#     while True:
#         if all(full):
#             break
#         for i in range(3):
#             if not full[i]:
#                 try:
#                     indicator = i
#                     temp = pickle.load(file[i])
#                     if list(temp.keys())[0] == selected_index:
#                         for posting in temp[selected_index]:
#                             dict_output[selected_index].append(posting)
#                 except EOFError:
#                     if indicator == 0:
#                         full[0] = True
#                     elif indicator == 1:
#                         full[1] = True
#                     elif indicator == 2:
#                         full[2] = True
#                     else:
#                         pass
#         indicator = -1
#     pickle.dump(dict_output, file_output)
#     file_0.close()
#     file_1.close()
#     file_2.close()
#     file_output.close()

if __name__ == "__main__":
    with open('docmap.pickle', 'rb') as info:
        doc_map = pickle.load(info)

    partial_indexer_num = doc_map["__total_indexer_num__"]
    total_file_num = doc_map["__total_file_num__"]
    start = time.time()
    merge(partial_indexer_num, total_file_num)
    end = time.time()
    print("merge costs {} seconds".format(end-start))
