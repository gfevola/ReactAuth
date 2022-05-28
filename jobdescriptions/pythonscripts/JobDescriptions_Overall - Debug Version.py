# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 11:58:25 2022

@author: 16317
"""

import pandas as pd
import numpy as np

from sklearn.manifold import TSNE


def JobDescriptionsAnalyze(file, jobcodefield, jobtitlefield, descfield):

    #run once
    # nltk.download('stopwords')
    # nltk.download('wordnet')
    # nltk.download('averaged_perceptron_tagger')
    # nltk.download('punkt')
    jobcodefield = "Job.ID"
    jobtitlefield="Business.Title"
    descField = "Job.Description"
    jd = pd.read_excel("C:\\Users\\16317\\Documents\\Datasets\\NYCJobs.xlsx")
    jd = jd.loc[0:70,:]
    jdunique = jd[[jobcodefield,'Job.Description','Minimum.Qual.Requirements','Job.Category','Business.Title']].drop_duplicates().reset_index()
    jdunique['index'] = range(len(jdunique))
    jdunique[jobcodefield] = jdunique[jobcodefield].apply(lambda x: str(x))
    jdcodes = jdunique[[jobcodefield,'index']]
    
    ##--run functions --
    formatted = jdunique['Job.Description'].apply(lambda x: removepunctuation(str(x)))
    jdgrams_list = formatted.apply(lambda x: splitintograms(x))
    
    #secondary functions
    [alltagslist, allgramslist] = assemblejdtags(jdgrams_list)
    [datacharacteristics, uniques, xvals] = taglist_to_grams(alltagslist,allgramslist)
    [uniqueStrings, dictterms, diffmelt_mg, corpus_topics] = lda_grammodeling(uniques)    
    [matches_grams, matches_counts, matches_check] = TextsOrganizeandCompare(diffmelt_mg, allgramslist, jdunique)
    
    allgramslist_mg = allgramslist.merge(uniqueStrings,how="left",left_on="JDString",right_on="JDString")
    allgramslist_mg = allgramslist_mg.merge(jdcodes,how='left',left_on='Entry',right_on='index')
    
    return([allgramslist_mg, matches_grams])

    
    uniques_topics = pd.concat([uniqueStrings,pd.Series(corpus_topics)],axis=1)
    uniques_topics = uniques_topics[['JDString','Topic',0]]
    
    #---------------------------------------
    #categories--------------
    #summarize xvals by entry (JD)
    datacharacteristics = datacharacteristics.reset_index(drop=True)
    xvals = xvals.reset_index(drop=True)
    dataX = pd.concat([datacharacteristics,pd.DataFrame(xvals)],axis=1)
    dataXsum = dataX.groupby('EntryNo').sum()
    xvalssum = dataXsum.loc[:,1:len(xvals.columns)]
    foundEntries = dataX['EntryNo'].unique()
    
    #create tokenized from categories
    jdunique['Category'] = [" ".join([stringna(jdunique['Job.Category'][i]),stringna(jdunique['Business.Title'][i])]) for i in range(len(jdunique))]
    [textdf, cat_xvals,cat_tokenizer] = Texts_to_Seqs(jdunique['Category'])
    cat_xvals = cat_xvals.reset_index(drop=True)
    xcat_tsne = pd.DataFrame(TSNE(2).fit_transform(cat_xvals)).reset_index()
    
    textdf1 = pd.concat([textdf,xcat_tsne],axis=1)
    

#---------------
