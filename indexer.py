import json
from bs4 import BeautifulSoup
import os
from Posting import Posting
from tokenizer import *
import pickle
from nltk.stem import PorterStemmer
import math
import lxml
import lxml.html
from merge import merge


def create_indexer():
    indexer = {}
    doc_map = {}
    file_num = 0
    indicator = 0
    file_indicator = 0
    ps = PorterStemmer()
    for root, dirs, files in os.walk("./DEV"):
        for file in files:
            try:
                with open(os.path.join(root, file), 'r') as f:
                    file_data = json.load(f)

                url = file_data["url"]
                doc_map[file_num] = url

                soup = BeautifulSoup(file_data["content"], "lxml")

                print("parsing url:", url)
                if not bool(soup.find()):
                    continue

                for script in soup.find_all('script', src=False):
                    script.decompose()

                for script in soup.find_all('style', src=False):
                    script.decompose()

                content = ' '.join(soup.stripped_strings)

                try:
                    title = soup.title.string  # get the title of the soup content
                    important_text = title + " " + title + " " + title
                    # multiply by 3 to make it more important in frequency

                except:
                    important_text = ''  # If no title string in soup, we return the important text as empty

                for b in soup.find_all('b'):  # find bold string
                    if b.string:
                        important_text = important_text + " " + b.string
                for strong in soup.find_all('strong'):  # strong string
                    if strong.string:
                        important_text = important_text + " " + strong.string

                # get the content in tags h1, h2, h3
                for h1 in soup.find_all('h1'):
                    if h1.string:
                        important_text = important_text + " " + h1.string
                for h2 in soup.find_all('h2'):
                    if h2.string:
                        important_text = important_text + " " + h2.string
                for h3 in soup.find_all('h3'):
                    if h3.string:
                        important_text = important_text + " " + h3.string

                important_tokens = my_tokenize(important_text)

                tokens = my_tokenize(content)

                if len(tokens) > 300000 or len(tokens) < 50:
                    continue

                stemming = [ps.stem(token) for token in tokens]

                important_stemming = [ps.stem(token) for token in important_tokens]

                frequency_list = compute_word_frequencies(stemming)

                important_freq_list = compute_word_frequencies(important_stemming)

                for token, frequency in frequency_list.items():
                    docid = file_num
                    important_weight = important_freq_list.get(token, 0)
                    new_posting = Posting(docid, frequency, important_weight)
                    if token not in indexer:
                        indexer[token] = []
                    indexer[token].append(new_posting)

                file_num += 1
                indicator += 1
                # print(indicator)
                if indicator == 10000:  # if the current file number is greater than 10000
                    sorted_indexer = dict(sorted(indexer.items()))
                    store_indexer(sorted_indexer, f'indexer_{file_indicator}.pickle')
                    indicator = 0
                    file_indicator += 1
                    indexer.clear()
            except Exception as e:
                print(e)
                continue
    sorted_indexer = dict(sorted(indexer.items()))
    store_indexer(sorted_indexer, f'indexer_{file_indicator}.pickle')
    indexer.clear()
    doc_map[
        "__total_file_num__"] = file_num  # since "__" is not alphanumeric, this key should be unique
    doc_map["__total_indexer_num__"] = file_indicator+1

    with open('docmap.pickle', 'wb') as info2:
        pickle.dump(doc_map, info2)
    doc_map.clear()


def store_whole_indexer(indexer, file_name1):
    with open(file_name1, 'wb') as info:
        pickle.dump(indexer, info)


# Store indexer by tokens so we can get only the needed query later
def store_indexer(indexer, file_name1):
    # print('store')
    with open(file_name1, 'ab+') as info1:
        for key, value in indexer.items():
            temp = {key: value}
            pickle.dump(temp, info1)


if __name__ == "__main__":
    create_indexer()
