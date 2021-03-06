import math
import nltk
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import gc
from collections import Counter
from nltk.tag import pos_tag


class keywordfunction:
    def __init__(self, StringBox):
        self._StringBox = StringBox
        nltk.download('averaged_perceptron_tagger')

    def WordRank(self, x):
        self._x = x



    def MakeKeyword(self):
        # corpus 전체 말뭉치
        corpus = []
        text_num = []
        number = 0
        for i in self._StringBox:
            corpus.append(i.replace("\n", " "))
            text_num.append(number)
            number += 1

        num_docs = len(corpus)

        v = CountVectorizer(ngram_range=(1, 2), binary=True, stop_words='english', min_df=1)
        vf = v.fit_transform(corpus)

        terms = v.get_feature_names()
        freqs = np.asarray(vf.sum(axis=0).ravel())[0]
        idfs = [math.log10(num_docs / f) for f in freqs]
        custom_weight1 = np.array([1 + math.log10(f) for f in freqs])

        keywords1 = []
        interval = 100
        cur_index = 0

        while cur_index < len(corpus):
            v = CountVectorizer(ngram_range=(1, 2), stop_words='english', vocabulary=terms, min_df=1)
            vf = v.fit_transform(corpus[cur_index:cur_index + interval])
            a = vf.toarray()

            #word 의 weight 계산
            for data in a:
                zero_weight = []
                word_weight = np.copy((np.log10(data + 1) * idfs * custom_weight1))
                for i, weight in enumerate(word_weight):
                    if weight == 0:
                        zero_weight.append(i)

                #weight이 '0'인 단어들 제거
                new_word_weight = np.delete(word_weight, zero_weight)

                #for i, k in enumerate(sorted(new_word_weight)):
                #    print(terms[i])
                #    print(k)

                #TOP20만 출력
                x = word_weight.argsort()[-20:][::-1]
                keywords1.append(x)


            del v
            del vf
            del a
            gc.collect()
            cur_index += interval
        # 메모리문제때문에 키워드 100간격씩 추출하고 메모리 해제

        x1 = np.array(keywords1).flatten()

        # 중복 없애기->집합생성
        dummy = x1.copy().tolist()

        # 동일한 값의 자료가 몇개인지 파악
        occ = Counter(dummy)

        # 중복된거지워주기
        for wid in list(occ.keys()):
            if occ[wid] != 1:
                del occ[wid]

        # survived 최종 남은 키워드
        survived = {}
        for word in list(occ.keys()):
            for i, k in enumerate(keywords1):
                # 열거해서 정렬
                if word in k:
                    if text_num[i] not in survived:
                        survived[text_num[i]] = [word]
                    else:
                        survived[text_num[i]].append(word)

        finalkeyword = []
        for s in text_num:
            output = [terms[x] for x in survived[s]]
            finalkeyword.append(output)
        # print(finalkeyword)

        tagged_list = []
        for i in finalkeyword:
            tagged_list.append(pos_tag(i))
        # print(tagged_list)

        checkbox = []
        for i in tagged_list:
            wordbox2 = [t[0] for t in i if t[1] == "NN" or t[1] == "NNS"]
            checkbox.append(wordbox2)

        # 중복값 및 의미없는 단어
        finalbox = []
        for i in checkbox:
            resultbox = i
            for k in i:
                for word in resultbox:
                    if k == word:
                        continue
                    elif word in k:
                        i.remove(word)
                    else:
                        continue
            finalbox.append(i)

        return finalbox