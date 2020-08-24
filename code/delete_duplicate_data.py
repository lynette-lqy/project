#!/usr/bin/env python
# coding: utf-8

# This class is designed to delete duplicate data which exist both in NFRI database and NIFS database. This class only has one function which is mainly used to compare title which may have small differences.

# In[ ]:


import csv
import pandas as pd
import re
from nltk.stem import PorterStemmer 
ps = PorterStemmer()


# In[ ]:


class delete_duplicate_data:
    
    def __init__(self,specie):
        self.specie = specie
        
    # Define a class to compare titles in both databases.
    def search_title(self):
        ## Extract title of each database.
        nfri_title_list = list(set(pd_nfri_main[pd_nfri_main['specie']==self.specie]['title_of_record'].tolist()))
        nifs_title_list = list(set(pd_nifs_main[pd_nifs_main['specie']==self.specie]['title_of_record'].tolist()))
        ## Find common species in two databases.
        ## As the titles may have several differences, so I use word stemming to simplify the words in title.
        common_title = []
        for i in range (len(nfri_title_list)):
            nfri_stemming = [ps.stem(w) for w in nfri_title_list[i].split()]
            for j in range (len(nifs_title_list)):
                nifs_stemming = [ps.stem(w) for w in nifs_title_list[j].split()]
                if nfri_stemming == nifs_stemming: # Add common titles of two databases.
                    common_title.append([nfri_title_list[i],nifs_title_list[j]])
        
        # Extract record number of common titles in two databases.
        both_record = []
        for i in range (len(common_title)):
            nfri_record = pd_nfri_main[pd_nfri_main['title_of_record']==common_title[i][0]]['record_number'].tolist()
            nifs_record = pd_nifs_main[pd_nifs_main['title_of_record']==common_title[i][1]]['record_number'].tolist()
            both_record.append([nfri_record,nifs_record])
        
        # Record common record number if the value of meta data are the same under the same title.
        both_ID = []
        for i in range (len(both_record)):
            ## To save time of directly comparing meta data, I firstly compare the length of meta data.
            nfri_record = both_record[i][0]
            nifs_record = both_record[i][1]
            ## Compare the value of X and sort it by x value.
            for a in range (len(nfri_record)):
                nfri_data = pd_nfri_data[pd_nfri_data['ID']==nfri_record[a]]
                nfri_data = nfri_data.sort_values(by = ['X','Y','X_error','Y_error'],ascending=True) # Sort by x value.
                for b in range (len(nifs_record)):
                    nifs_data = pd_nifs_data[pd_nifs_data['ID']==nifs_record[b]] 
                    nifs_data = nifs_data.sort_values(by = ['X','Y','X_error','Y_error'],ascending=True) # Sort by x value.
                    if len(nfri_data) == len(nifs_data): # Compare x value.
                        ## If they are the same, record the record number respectively of two databases.
                        if nfri_data['X'].tolist() == nifs_data['X'].tolist(): 
                            both_ID.append([nfri_record[a],nifs_record[b]])
        self.both_ID = both_ID
        return both_ID

