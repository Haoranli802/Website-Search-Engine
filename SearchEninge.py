import pickle
import sys
import time
import json
import os
from nltk.stem.porter import PorterStemmer


def search(merge_index_file, doc_map_file, token_position_file):
    position_dict = {}
    with open(doc_map_file, 'rb') as info2:
        doc_map = pickle.load(info2)
    with open(token_position_file, 'r') as info1:
        for line in info1:
            position_dict.update(json.loads(line))
    indexer_file = open(merge_index_file, 'r')

    ps = PorterStemmer()
    while True:
        keyword = input('Enter the query that you want to search(or enter "_q" to quit): \n')
        searched = keyword
        start_time = time.time()
        if keyword.strip().lower() == '_q':  # we set "_q" or "_Q" as the quit command of our search engine
            sys.exit(0)

        if len(keyword) == 0:  # If the input is empty, we just continue the search engine
            continue
        else:
            # rs = []
            # strip the whitespaces on both side
            keyword = keyword.lstrip().rstrip().lower()
            kws = keyword.split(' ')
            try:
                if len(kws) > 1:  # parse the condition that the input has more than one tokens
                    whole_result_doc = []
                    results = []
                    for kw in kws:
                        kw = ps.stem(kw)  # get the stemming word
                        position = position_dict[kw]
                        indexer_file.seek(position)
                        temp_dict = json.loads(indexer_file.readline())
                        print(list(temp_dict.keys())[0])

                        posting_docs = list(temp_dict.values())[0]

                        results += posting_docs

                        doc_id_list = []
                        for posting in posting_docs:
                            doc_id_list.append(posting['docid'])

                        if len(doc_id_list) > 0:  # append in the whole result list when there is result searched
                            whole_result_doc.append(doc_id_list)

                    whole_result_doc.sort(key=len)  # start from smallest set to process faster
                    doc_intersect = whole_result_doc[0]

                    # get the biggest intersection between the result documents for each keyword input
                    for doc in whole_result_doc[1:]:
                        intersect = list(set(doc_intersect).intersection(doc))
                        doc_intersect = intersect
                    # keep only the docs whose tfidf is bigger than 0
                    # Now our tfidf is frequency so every tfidf is > 0, but this one might be used later
                    relation_threshold = 0  # leave a variable here to use if we want to have results
                                            # that is related enough
                    final_result = [posting for posting in results if posting['tfidf'] > relation_threshold]

                else:  # Only one token is entered
                    kw = ps.stem(keyword)
                    position = position_dict[kw]
                    indexer_file.seek(position)
                    temp_dict = json.loads(indexer_file.readline())
                    print(list(temp_dict.keys())[0])

                    results = list(temp_dict.values())[0]
                    # keep only the docs whose tfidf is bigger than 0
                    final_result = [posting for posting in results if posting['tfidf'] > 0]
            except KeyError:  # key error means that one of the keywords is not in the indexer
                no_result(searched)
                continue
            # sort the result based on the tfidf an the important weight score

            normalization_for_iw = 3
            # This value is used for normalize the important weight.
            # # The bigger it is, the smaller the impact of important weight will be
            sorted_result = sorted(final_result, key=lambda x: x['tfidf'] + x['important_weight'] /
                                                               normalization_for_iw, reverse=True)
            # postings = sorted_result[:50]  # get the first 50 result

            postings = sorted_result[:5]

            if len(postings) == 0:
                print('No result found')
                continue  # start next search
            urls = []
            for posting in postings:
                doc_id = posting['docid']  # get the doc id
                url = doc_map[doc_id]
                urls.append(url)
                print("the tfidf is: {}, important weight is: {}".format(posting['tfidf'], posting['important_weight']))
            # urls = list(set(urls))  # eliminate the repeated urls
            for url in urls:  # get the top 5 url
                print(url)

            end_time = time.time()
            response_time = end_time - start_time
            print("The response time is {:.4f} ms.".format(response_time * 1000))


def no_result(searched):
    print("Your search - {} - did not match any documents".format(searched))
    print("Suggestions:")
    print("    1. Make sure all words are spelled correctly.")
    print("    2. Try different keywords.")
    print("    3. Try more general keywords.\n")


if __name__ == '__main__':
    search('merged.json', 'docmap.pickle', 'position.json')
