# -*- coding: utf-8 -*-
"""Gensim_Topic_Modeling_Tuning v0.2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YSXHJHdoDgS23wKvlTxQRp28qsMW0ibW
"""

# Colab에 Khaiii 설치

import os
!git clone https://github.com/kakao/khaiii.git
!pip install cmake
!mkdir build
!cd build && cmake /content/khaiii
!cd /content/build/ && make all
!cd /content/build/ && make resource
!cd /content/build && make install
!cd /content/build && make package_python
!pip install /content/build/package_python

# src에 있는 preanal.manual 파일 dir로 옮기는 Code

import shutil

filename = "preanal.manual"
src = '/content/'
dir = '/content/khaiii/rsc/src/'

shutil.move(src+filename, dir+filename)

# Khaiii 사용자 사전 추가
''' 
** Khaiii 사용자 사전 추가를 참고  **
'''

!cd /content/khaiii/rsc
!mkdir -p /content/build/share/khaiii
!PYTHONPATH=/content/khaiii/src/main/python /content/khaiii/rsc/bin/compile_preanal.py --rsc-src=/content/khaiii/rsc/src --rsc-dir=/content/build/share/khaiii

"""## Gensim Topic Modeling"""

import pandas as pd


data = pd.read_csv('/content/final_input.csv', encoding='utf-8').drop(['Unnamed: 0'], axis=1)

data.info()

"""# Gensim LDA를 위한 데이터 전처리
## Experiment 1) Khaiii에서 명사, 어근만 추출해 Tokenizing
"""

from khaiii import KhaiiiApi
api = KhaiiiApi(rsc_dir="/content/build/share/khaiii")

n_tags = ['NNG', 'NNP', 'NNB', 'XR']#, 'VV', "VA"] # 동사도 넣고 싶으면 추가

'''
input : 추출할 Review의 list ;
output : n_tags의 tag와 일치하는 text list ; 
'''

def extract_corpus_khaiii(texts):
    extract_corpus = []
    for line in texts:
      if str(line) != 'nan':
        nouns = []

        for word in api.analyze(str(line)):
          for morphs in word.morphs:
            if morphs.tag in n_tags:
              if len(morphs.lex) > 1:
                nouns.append(morphs.lex)
              else:
                continue

        extract_corpus.append(nouns)

    return extract_corpus

data.Review[0]

n_tags = ['NNG', 'NNP', 'NNB']
api = KhaiiiApi(rsc_dir="/content/build/share/khaiii")
for word in api.analyze("유자 마카롱에 상큼한 필링이 가득했고, 초코 마카롱에 초코칩이 잔뜩 박혀 식감이 좋았어요"):
    for morph in word.morphs:
      if morph.tag in n_tags:
        print(morph)

# 네이버 영수증 리뷰, 인스타 리뷰에서 명사, 어근을 추출
khaiii_xr = extract_corpus_khaiii(data['Review']) 

#khaiii_all = extract_corpus_khaiii(data['Review']) # 명사, 동사, 형용사, 어근 모두 추출

# 추출 전 데이터와 비교

print(len(data), len(khaiii_xr))
#print(len(data), len(khaiii_all))

import gensim
from gensim.utils import simple_preprocess
# Build the bigram and trigram models
bigram = gensim.models.Phrases(khaiii_xr, min_count=5, threshold=100) # higher threshold fewer phrases.
trigram = gensim.models.Phrases(bigram[khaiii_xr], threshold=100)

# Faster way to get a sentence clubbed as a trigram/bigram
bigram_mod = gensim.models.phrases.Phraser(bigram)
trigram_mod = gensim.models.phrases.Phraser(trigram)

# remove Stopwords, make bigram, trigram function

def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]
    
def make_bigrams(texts):
    return [bigram_mod[doc] for doc in texts]

def make_trigrams(texts):
    return [trigram_mod[bigram_mod[doc]] for doc in texts]

stop_words = ['점심', '아침', '종류', '오랜만', '자리', '직원', '아이', '오픈', '날씨', '저녁', '따뜻', '메뉴', '다양','창녕', '달성군', '동대문', '수성', '영등포', '뻐용', '용산구', '관악', '오늘', '달서', '강동구', '모두', '평택', '과천', '해운대구', '합천', '계양', '매장', '광진구', '강동', '기장군', '남해', '서초', '경산시', '광양시', '논산시', '서대문', '단양군', '아산', '동구', '구미', '칠곡군', '공주시', '부산진', '계룡', '청도군', '제천', '부안', '정도', '하동군', '부여군', '괴산', '여수시', '송파구', '문경시', '거제시', '옹진', '함평', '평택시', '하동', '복기', '제주', '영주', '고령군', '울주군', '여수', '동해시', '아메리카', '보령시', '화성', '동두천', '원주', '정읍시', '커피', '영암', '양산', '철원군', '군위', '고흥군', '양구군', '강진', '여주시', '의정부시', '강화', '서대문구', '영광군', '저번', '북구', '시흥시', '양산시', '영양', '계양구', '사하구', '장수', '홍천군', '목포', '사람', '봉화군', '완주', '순천시', '경주시', '수성구', '이드', '완도', '구례', '보성군', '카페', '제천시', '카페라', '하남', '무안', '용산', '정선군', '울릉군', '안성시', '무주', '통영시', '울진군', '광진', '화성시', '영덕', '의정부', '마포구', '충주시', '기장', '괴산군', '익산', '완도군', '금천구', '성주', '김제시', '서산', '속초', '사상구', '남해군', '영천시', '가평군', '인제군', '제주시', '과천시', '동대문구', '광명', '구로구', '논산', '담양군', '오산시', '장성', '서천', '화순군', '양평군', '광산구', '성동', '중랑구', '이천시', '방문', '관악구', '무안군', '예천군', '남원', '함안', '구리', '성북구', '군포', '양천', '영덕군', '강화군', '평창', '김해시', '해남', '울릉', '금산', '광산', '함양', '곡성군', '봉화', '울주', '보은', '장수군', '홍천', '동작구', '부천', '디저트', '순창군', '최고', '추천', '부평구', '화순', '강남구', '증평군', '영월', '부여', '진안', '철원', '영월군', '양천구', '청양군', '의왕시', '양주', '포천시', '카페예', '공주', '강서구', '호점', '거창군', '영도구', '때문', '합천군', '강북구', '속초시', '울진', '경주', '대체', '시흥', '군산', '충주', '청송', '고흥', '송파', '동래구', '단양', '횡성', '양구', '증평', '보령', '안동시', '이천', '포천', '영광', '연수', '전체', '동해', '가격', '진도군', '달성', '양평', '사천시', '청양', '원주시', '김포시', '양주시', '진천군', '남원시', '그동안', '중랑', '강릉', '순천', '이후', '고창군', '하남시', '불구', '맛집', '안성', '산청', '강진군', '청도', '삼척시', '김천시', '종로구', '담양', '진주시', '횡성군', '구례군', '파주', '광명시', '은평구', '음성', '영주시', '예산군', '고성군', '노원', '김천', '광양', '장성군', '신안군', '도봉', '분위기', '추입', '사상', '강북', '서초구', '사하', '커피랑', '김제', '임실', '고창', '영등포구', '진천', '성동구', '산청군', '달서구', '사장', '연천', '장흥', '뻐요', '유성', '주문', '의령', '아메리카노랑', '당진', '부평', '도봉구', '서천군', '밀양', '상주시', '예천', '메리카노', '부산진구', '춘천시', '상주', '함평군', '의왕', '경산', '구요', '거창', '홍성군', '마포', '신발', '금천', '대덕', '고령', '종로', '해남군', '느낌', '남양주', '부안군', '통영', '이즈니버터', '가평', '화천군', '가요', '익산시', '정보궁금팔로다음', '창녕군', '홍성', '생각', '진안군', '사천', '목포시', '옹진군', '청송군', '은평', '삼척', '연수구', '칠곡', '니당', '여주', '신안', '정선', '의령군', '연천군', '의성', '동두천시', '어제', '정읍', '요즘', '군포시', '나주', '카페입니', '내일', '함양군', '시간', '양양군', '음성군', '인제', '군산시', '유성구', '구미시', '진짜', '영암군', '광주', '태백시', '구로', '해운대', '동작', '금정구', '강남', '강서', '밀양시', '서산시', '대덕구', '강릉시', '고성', '진도', '수영', '보성', '서귀포시', '수영구', '태안군', '양양', '부천시', '태안', '태백', '완전', '의성군', '케이크', '문경', '친절', '중구', '평창군', '남구', '순창', '서귀포', '음료', '연제', '동래', '예산', '영천', '거제', '영도', '보은군', ' 굿굿굿', '함안군', '파주시', '안동', '남양주시', '노원구', '김해', '서구', '곡성', '구리시', '군위군', '임실군', '진주', '영양군', '장흥군', '광주시', '완주군', '화천', '연제구', '무주군', '오산', '성주군', '당진시', '계룡시', '춘천', '성북', '아산시', '금산군', '김포', '멍멍', '크림', '금정', '나주시']

# Stop words 제거 및 trigram 만들기

khaiii_xr = remove_stopwords(khaiii_xr)

khaiii_xr = make_trigrams(khaiii_xr)

# countvectorize를 위한 역토큰화 진행
'''
input : n_tags만 뽑힌 token list
 Ex. ['얼그레이', '마카롱', '맛']

output : 역토큰화된 detoken list
 Ex. ['얼그레이 마카롱 맛']
'''
def detokenize(token_list):
  detokenized_doc = []
  for i in range(len(token_list)):
    if token_list[i] != []:
      t = ' '.join(token_list[i])

      detokenized_doc.append(t)
  return detokenized_doc
    #detokenized_doc.append([data['Nickname'][i], t]) -> 옆에 닉네임 붙여서 내보낼거면 활성화

# bigram, trigram으로 합쳐진 단어는 _로 합쳐지기 때문에 _를 제거하고 합쳐줌

for i in range(len(khaiii_xr)):
  for j in range(len(khaiii_xr[i])):
    khaiii_xr[i][j] = khaiii_xr[i][j].replace("_", "")

# trigram으로 형성된 토큰 역토큰화

detoken_xr = detokenize(khaiii_xr)

"""## Using Gensim"""

# install gensim

!pip install gensim

# import package

from sklearn.feature_extraction.text import CountVectorizer
from gensim.matutils import Sparse2Corpus

from gensim.models.ldamodel import LdaModel
from gensim.models.coherencemodel import CoherenceModel
from gensim.models.ldamulticore import LdaMulticore
from gensim import corpora


# Warning 무시
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
warnings.filterwarnings(action='ignore', category=Warning, module='gensim')
warnings.filterwarnings('ignore')

"""* **num_topics**: 최종 분석의 주제 수
* **passes**: 총 훈련 과정의 수. 신경망 학습에서 에포크와 같다
* **iteration** : 각 문서에 대해 업데이트를 반복하는 횟수
* **random_state**: 재현 가능한 결과를 위해 임의의 숫자를 설정한다.

### 최적의 number of words 찾기
* 지표 : Coherence
"""

# number_of_words를 찾기 위한 함수

def compete_number_of_words(detoken_data, token_data, min_num, max_num, step, random_state=None):

  '''
  number_of_words를 찾기 위한 함수 

  Parameters :
  -------------
  detoken_data : list 형태의 역토큰화된 데이터
  token_data : coherence 값을 계산하기 위한 token_data
  min_num : number of words range의 최솟값 min_num부터 시작
  max_num : number of words range의 최댓값 max_num까지 찾음
  step : min_num ~ max_num 까지 가기 위해 step을 얼마나 갈것인지
  random_state : 재현성을 주기 위해 설정, default = None

  Output :
  -------------
  coherence_value : Num of Words와 그에 따른 Coherence Value가 있는 DataFrame 반환
  
  '''

  coherence_value = pd.DataFrame(columns=['min_df', 'Perplexity Value','Coherence Value'])

  i = 0
  min_df = list(np.arange(min_num,max_num,step))
  for m in min_df :
    print("{} 번째, min_df = {}".format(i+1, m))

    vectorizer = CountVectorizer(min_df=m) # CountVectorizer 생성
    cv = vectorizer.fit_transform(detoken_data) # fit and transform

    dictionary = corpora.Dictionary([vectorizer.get_feature_names()])

    corpus = Sparse2Corpus(cv.T)

    lda_model = LdaModel(corpus=corpus, id2word=dictionary, random_state=random_state)

    coherence_lda = CoherenceModel(model=lda_model, texts=token_data, dictionary=dictionary, coherence='c_v')

    coherence_value.loc[i] = [m, lda_model.log_perplexity(corpus),coherence_lda.get_coherence()]
    i += 1

  return coherence_value

# 1000 ~ 32000까지 1000 step씩 건너며 coherence value 계산
import numpy as np
compete_num_words = compete_number_of_words(detoken_xr, khaiii_xr, 0.0001, 0.01, 0.0001, random_state=42)

compete_num_words.sort_values(by='Coherence Value', ascending=False).head()

compete_num_words.sort_values(by='Perplexity Value', ascending=True).head()

# Commented out IPython magic to ensure Python compatibility.
# 그래프 시각화를 위한 package import

# %matplotlib inline 
import matplotlib.pyplot as plt
import numpy as np

# 글씨 크기 조정
plt.rc('font', size=14)

# Number of words의 변화에 따른 coherence value 그래프 

plt.figure(figsize=(20, 10))
plt.xlabel('min_df')
plt.ylabel('Coherence Value')
plt.xticks(np.arange(0.0001,0.01,0.0001), rotation=90)
plt.yticks(np.arange(0.3, 0.35, 0.01))
plt.ylim(0.3, 0.35)
plt.grid(True)
plt.title("Coherence Value for chainging number of words")
plt.plot(compete_num_words['min_df'], compete_num_words['Coherence Value'])
plt.scatter(compete_num_words['min_df'], compete_num_words['Coherence Value'])
plt.show()

# Number of Words에 따른 abs(Log Perplexity) 값 그래프

plt.figure(figsize=(15, 10))
plt.xlabel('min_df')
plt.ylabel('Coherence Value')
plt.xticks(np.arange(0.0001,0.01,0.0001), rotation=45)
plt.grid(True)
plt.title("abs(Peplexity Value) for chainging number of words")
plt.plot(compete_num_words['min_df'], abs(compete_num_words['Perplexity Value']), 'r')
plt.scatter(compete_num_words['min_df'], abs(compete_num_words['Perplexity Value']), c='r')
plt.show()

# 위의 두 개의 그래프 합치기

fig, ax1 = plt.subplots(figsize=(10, 10))

x = np.arange(0.0001,0.01,0.0001)
y1 = compete_num_words['Coherence Value']
y2 = abs(compete_num_words['Perplexity Value'])

ax1.set_xlabel('min_df')
ax1.set_ylabel('Coherence Value', color='blue')
ax1.set_ylim(0.3, 0.35)
ax1.plot(x, y1, c='b')
ax1.scatter(x, y1, c='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()  
ax2.set_ylabel('Perplexity Value', color='red')  
ax2.plot(x, y2, c='r')
ax2.scatter(x, y2, c='r')
ax2.tick_params(axis='y', labelcolor='r')
fig.legend(['Coherence Value','c_v', 'abs(Perplexity Value', 'p_v'])
fig.tight_layout()

plt.grid()
plt.show()

"""# 최적의 LDA Model Parameter 찾기"""

# 이전의 결과로 나타난 max_featues : (       )를 사용
from google.colab import files

best_count = CountVectorizer(min_df=0.0099)

count_vec =  best_count.fit_transform(detoken_xr)

corpus = Sparse2Corpus(count_vec.T)

dic = corpora.Dictionary([best_count.get_feature_names()])

# coherence value를 반환 - 알파, 베타 고려 X

def compete_values(corpus, token_data, id2word, a='auto', b=None):

  lda_model = gensim.models.LdaModel(corpus=corpus,
                                         id2word=id2word,
                                         num_topics=5,
                                         random_state=42, 
                                         chunksize=256, 
                                         passes=10,
                                         alpha=a,
                                         eta=b,
                                         per_word_topics=True,
                                         iterations=500)
  
  coherence_model = CoherenceModel(model=lda_model, texts=token_data, dictionary=id2word, coherence='c_v')

  pv, cv = lda_model.log_perplexity(corpus), coherence_model.get_coherence()

  return pv, cv

# 최적의 Topic 개수 찾기 - 알파, 베타 고려 X

# Topic Range
min_topics = 5
max_topics = 45
step_size = 5
topic_range = range(min_topics, max_topics, step_size)

model_result = pd.DataFrame(columns=['n_topic', 'perplexity', 'coherence'])
i = 0
for n_topic in topic_range:
  print("{} 번째, n_topic : {}".format(i+1, n_topic))
  
  pv, cv = compete_values(corpus=corpus, token_data=khaiii_xr, id2word=dic, k=n_topic)

  model_result.loc[i] = [n_topic, pv, cv]
  print("{}번째\n coherence score : {}\n perplexity score : {}".format(i+1, cv, pv))
  print("=====================================================================")
  i += 1

model_result.to_csv('gensim optimizing model_step5.csv', encoding='utf-8')
files.download('gensim optimizing model_step5.csv')

model_result.sort_values(by=['coherence'],ascending=False)

model_result.sort_values(by=['perplexity'],ascending=True)

vectorizer = CountVectorizer(min_df=0.0099) # CountVectorizer 생성
cv = vectorizer.fit_transform(detoken_xr) # fit and transform

dictionary = corpora.Dictionary([vectorizer.get_feature_names()])

corpus = Sparse2Corpus(cv.T)

lda_model = gensim.models.LdaModel(corpus=corpus,
                                  id2word=dictionary,
                                  num_topics=5,
                                  random_state=42, 
                                  chunksize=256, 
                                  passes=10,
                                  alpha=a,
                                  beta=b,
                                  per_word_topics=True,
                                  iterations=500)

cv.shape

lda_model.print_topics()

import time
time.sleep(30000)

# Alpha parameter
alpha = list(np.arange(0.01, 1, 0.3))
alpha.append('symmetric')
alpha.append('asymmetric')

# Beta parameter
eta = list(np.arange(0.01, 1, 0.3))
eta.append('symmetric')

model_result = pd.DataFrame(columns=['alpha', 'eta', 'perplexity', 'coherence'])
i = 0

for A in alpha:
  for B in eta:
    print("i: {}, n_topic : 5, a : {}, b : {}".format(i+1, A, B))
    
    pv, cv = compete_values(corpus=corpus, token_data=khaiii_xr, id2word=dictionary, a=A, b=B)

    model_result.loc[i] = [a, b, pv, cv]
    print("{}번째\n coherence score : {}\n perplexity score : {}".format(i+1, cv, pv))
    print("=====================================================================")
    i += 1

model_result.sort_values(by=['coherence'],ascending=False).head(10)

model_result.sort_values(by=['perplexity'],ascending=True).head(10)

# 위의 두 개의 그래프 합치기

fig, ax1 = plt.subplots(figsize=(10, 10))

x = np.arange(0.0001,0.01,0.0001)
y1 = compete_num_words['Coherence Value']
y2 = abs(compete_num_words['Perplexity Value'])

ax1.set_xlabel('min_df')
ax1.set_ylabel('Coherence Value', color='blue')
ax1.set_ylim(0.3, 0.35)
ax1.plot(x, y1, c='b')
ax1.scatter(x, y1, c='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()  
ax2.set_ylabel('Perplexity Value', color='red')  
ax2.plot(x, y2, c='r')
ax2.scatter(x, y2, c='r')
ax2.tick_params(axis='y', labelcolor='r')
fig.legend(['Coherence Value','c_v', 'abs(Perplexity Value', 'p_v'])
fig.tight_layout()

plt.grid()
plt.show()

vectorizer = CountVectorizer(min_df=0.0099) # CountVectorizer 생성
cv = vectorizer.fit_transform(detoken_xr) # fit and transform

dictionary = corpora.Dictionary([vectorizer.get_feature_names()])

corpus = Sparse2Corpus(cv.T)

lda_model = gensim.models.LdaModel(corpus=corpus,
                                  id2word=dictionary,
                                  num_topics=5,
                                  random_state=42, 
                                  chunksize=256, 
                                  passes=10,
                                  alpha=0.01,
                                  eta=0.01,
                                  per_word_topics=True,
                                  iterations=500)

lda_model.print_topics()

"""## 이 밑 부분은 나중에 최적 개수 정해지면 튜닝"""

from google.colab import files

# Topic Range
min_topics = 5
max_topics = 35
step_size = 5
topic_range = range(min_topics, max_topics, step_size)

model_result = pd.DataFrame(columns=['n_topic', 'alpha', 'beta', 'perplexity', 'coherence'])
i = 0
for n_topic in topic_range:
  for a in alpha:
    for b in beta:
      print("i: {}, n_topic : {}, a : {}, b : {}".format(i+1, n_topic, a, b))
      
      pv, cv = compete_values(corpus=corpus, token_data=khaiii_xr, id2word=dic, k=n_topic, a=a, b=b)

      model_result.loc[i] = [n_topic, a, b, pv, cv]
      print("{}번째의 coherence의 score {}".format(i+1, cv))
      print("=====================================================================")
      i += 1

model_result.to_csv('gensim optimizing model_step5.csv', encoding='utf-8')
files.download('gensim optimizing model_step5.csv')

# 최적의 coherence value 찾기

n_topic = np.arange(5, 505, 5)

co_value = pd.DataFrame(columns=['Num Topic', 'c_v'])
i = 0
for topic in n_topic:
  print("{}번째, {} 개의 topic".format(i, topic))
  LDA = LdaModel(corpus=corpus, id2word=id2word, num_topics=topic)

  c_v_LDA = CoherenceModel(model=LDA, texts=khaiii_xr, dictionary=dictionary, coherence='c_v')
  co_value.loc[i] = [topic, c_v_LDA.get_coherence()]
  i+=1

plt.figure(figsize=(10, 10))
plt.plot(co_value['Num Topic'], co_value['c_v'])
plt.scatter(co_value['Num Topic'], co_value['c_v'])
plt.ylim(0.30, 0.35)
#plt.xticks(np.arange(5, 505, 5), rotation=90)
plt.grid()
plt.tight_layout()
plt.show()

haha = pd.read_csv('final_1.csv',encoding='utf-8')

haha.review[1]

import pandas as pd
import re 
import math
def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    
    return emoji_pattern.sub(r'', string)

print(haha.review[1]+'\n'+remove_emoji(str(haha['review'][1])))

!pip install soynlp

from soynlp.normalizer import *
print(repeat_normalize('휴일 마지막 깨알같이 촘촘히ㅋㅋㅋㅋ', num_repeats=1))

def clean_text(texts):
    corpus = []
    for i in range(0, len(texts)):
        review = re.sub(r'[@%\\*=()/~#&\+á?\xc3\xa1\-\|\.\:\;\!\-\,\_\~\$\'\"\^]', '',str(texts[i])) #remove punctuation
        review = re.sub(r'\s+', ' ', review) #remove extra space
        review = re.sub(r'<[^>]+>','',review) #remove Html tags
        review = re.sub(r'\s+', ' ', review) #remove spaces
        review = re.sub(r"^\s+", '', review) #remove space from start
        review = re.sub(r'\s+$', '', review) #remove space from the end
        review = re.sub(r'[ㄱ-ㅎㅏ-ㅣ]+', '', review)
        corpus.append(review)
    return corpus

clean_text('휴일 마지막 !')

# 띄어쓰기 검사기 설치
!pip install git+https://github.com/haven-jeon/PyKoSpacing.git

# 띄어쓰기 교정

from pykospacing import spacing
print('아빠가방에 들어가신다'+'\n'+spacing(str('아빠가방에 들어가신다')))

time.sleep(2000)

time.sleep(30000)
