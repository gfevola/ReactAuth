# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 12:40:20 2022

@author: 16317
"""

import re
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk as nltk

lemmatizer = WordNetLemmatizer()    

def removepunctuation(d):
    val = re.sub(r'[-/]'," ",d)
    val = val.replace(f'\t'," ")
    val = val.replace(",","")
    val = re.sub(" +"," ",val)
    return re.sub(r'[();"$#]',"",val)

def splitintograms(d):
    return(re.split(':|\.|\;| and ',d))

def addcategories(x, numwords, isBracketed):
    seq = [0]*numwords
    try:
         if isBracketed: 
             for [a] in x:
                seq[a] += 1
         else:
             for a in x:
                seq[a] += 1
    except:
         #print('failed')
         #print(x)
         pass
    return(pd.DataFrame(seq))
        

def stringna(str1):
    if pd.isna(str1):
        return("")
    else:
        return(str1)

def joinstrs(str1,str2):
    " ".join([str1,str2])


def filter_pos_tag(d):
    lst = [w for w in d if len(w)>1]
    p = pd.DataFrame(lst)
    return p[p[1].isin(["JJ","VB",'VBN','VBG','VBD',"NN","NNS","CD",])]
  
def intseq_unlist(d):
    return([x[0] for x in d if len(x)>0])    

def parse_term(d):
    if pd.isna(d):
        return '0'
    else:
        #p = [lemmatizer.lemmatize(x.lower()) for x in tokenizer.tokenize(d) if not x in stop_words]
        p = [lemmatizer.lemmatize(x.lower()) for x in word_tokenize(d)]
        #return [q for q in p if not q.isdigit()]
        return p

deglist = ["baccalaureate","masters","master's","phd","high"]
def degreelevel(d):
    found = [deg for deg in deglist if len(d[0][d[0]==deg])>0]
    if len(found)>0:
        return(found[0].replace("'",""))
    else:
        return('')
