import pickle
import math


def load_indexer(file_name):
    with open(file_name, 'rb') as info:
        indexer = pickle.load(info)
        return indexer


def calculate_tf_idf(tf, df, total_file_num):
    idf = math.log(total_file_num/df, 10)
    tf_weight = 1 + math.log(tf, 10)
    tfidf_weight = tf_weight * idf
    return round(tfidf_weight, 4)  # round to 4 decimal places


def update_tfidf(single_token_dict, total_file_num):
    for token, postings in single_token_dict.items():
        df = len(postings)
        for posting in postings:
            tf = posting.tfidf
            itf = posting.important_weight
            posting.tfidf = calculate_tf_idf(tf, df, total_file_num)
            if posting.important_weight > 0:
                posting.important_weight = calculate_tf_idf(itf, df, total_file_num)
            # print("The tf-idf of {} is {}, iw is {}.".format(token, posting.tfidf, posting.important_weight))
    return single_token_dict

# def update_tfidf_for_each_term(indexer):
#     total_file_num = indexer["__total_file_num__"]
#     for token, postings in indexer.items():
#         try:
#             df = len(postings)
#             for posting in postings:
#                 tf = posting.tfidf
#                 itf = posting.important_weight
#                 posting.tfidf = calculate_tf_idf(tf, df, total_file_num)
#                 if posting.important_weight > 0:
#                     posting.important_weight = calculate_tf_idf(itf, df, total_file_num)
#                     print("The tf-idf of {} is {}, iw is {}.".format(token, posting.tfidf, posting.important_weight))
#         except TypeError:  # This is because we add a "__total_file_num__" term and the key is only an int
#             continue
#
#     return indexer

# def get_information(file):
#     indexer = load_indexer(file)


if __name__ == "__main__":
    indexer = load_indexer("indexer.pickle")
    new = update_tfidf_for_each_term(indexer)
    with open("new_indexer.pickle", 'wb') as info1:
        pickle.dump(new, info1)


