import re
import sys


def my_tokenize(content) -> list:
    re_pattern = re.compile(r"[a-z0-9]+")
    token_lst = re_pattern.findall(content.lower())
    # stop_words = set(tokenize_file("stopwords.txt"))
    # filtered_token = [t for t in token_lst if t not in stop_words]
    return token_lst


def tokenize_file(text_file_path):
    re_pattern = re.compile("[a-z0-9]+")
    token_lst = []
    try:
        with open(text_file_path, "r", encoding="utf-8") as file_lines:
            for line in file_lines:
                line = line.lower()
                token_lst += re_pattern.findall(line)
    except IOError as ioe:
        print(ioe)
        sys.exit(1)
    return list(token_lst)


def compute_word_frequencies(token_lst: list) -> dict:
    token_dict = {}
    for token in token_lst:
        if token in token_dict.keys():
            token_dict[token] += 1

        else:
            token_dict[token] = 1

    return token_dict


def print_token_dict(token_dict):
    sort_dict = sorted(token_dict.items(), key=lambda item: item[1], reverse=True)
    for k, v in sort_dict:
        print("{0} => {1}".format(k, v))


def url_hash(url):
    hash_value = 5381
    for c in url:
        hash_value = hash_value*33 + ord(c)

    return hash_value
