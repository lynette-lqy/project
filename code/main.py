#!/usr/bin/env python
# coding: utf-8

# In[5]:


import csv
import pandas as pd
import re
from nltk.stem import PorterStemmer 
from selenium import webdriver
from time import sleep
import sys
import creeper_nfri 
import creeper_nifs 
import delete_duplicate_data
ps = PorterStemmer()


# # Part 1 Do NLP for species

# Firstly, I define a function to remove charge in the ordinary formula.

# In[ ]:


# Define a function to remove charge.
def NLP_species(specie):
    # Remove positive and negative charge in the ordinary formula.
    r_1 = '[+]'
    r_2 = '-'
    output = re.sub(r_1,'',specie)
    output = re.sub(r_2,'',output)
    return output


# Then, I extract original file of species list.

# In[ ]:


# Read the file and make it a dataframe.
qdb_species_list = []
with open('qdb_species.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        qdb_species_list.append(row)
qdb_species = pd.DataFrame(qdb_species_list[1:],                            columns=qdb_species_list[0]) 
qdb_species = qdb_species.drop(['mass', 'energy', 'hform',                                 'lj_epsilon', 'lj_sigma'], axis = 1)


# Finally, by using the function above, I can get a list of species without charge.

# In[ ]:


# Add column which record species without charge.
qdb_species['ordinary_formula_without_charge'] = 0
len_species = len(qdb_species)
for i in range (len_species):
    qdb_species['ordinary_formula_without_charge'].iloc[i] = NLP_species(qdb_species['ordinary_formula'].iloc[i])
# Extract species and avoid duplicate species.
species_list = list(set(qdb_species['ordinary_formula_without_charge'].tolist()))


# # Part 2 Data mining for NFRI database

# In[ ]:


# Do data mining for NFRI database and save basic information data and meta data for each specie.
cs_nifr_list = []
for i in range (len(species_list)):
        cps_nfri = creeper_nfri.creep_species_nfri(species_list[i])
        cps_nfri.extract_data()
        cs_nifr_list.append([cps_nfri.pd_specie,cps_nfri.pd_data_dict])

# Combine basic information data for all species.       
pd_nfri_main = pd.DataFrame(index=['specie','record_number','process','QDB_process',                                   'type','element','ionic_state','initial_state_conf',                                   'initial_state','final_state','reaction_formula',                                   'x_unit','y_unit','reference_number','author',                                   'title_of_record','journal_name','volume_and_issue_No',                                   'page_number','date_of_publication','DOI']).T
for i in range (len(cs_nifr_list)):
    pd_nfri_main = pd_nfri_main.append(cs_nifr_list[i][0])
# Save the file.
pd_nfri_main.to_csv('pd_nfri_main.csv',sep='\t',index=False)

# Combine meta data for all record numbers
pd_nfri_data = pd.DataFrame(columns=['ID','X','Y','X_error','Y_error'])
for i in range (len(cs_nifr_list)):
    if len(cs_nifr_list[i][0])!=0: # If the length of meta data is 0, I don't need to append it.
        ID = cs_nifr_list[i][0]['record_number'].tolist()
        for j in range (len(ID)):
            if len(cs_nifr_list[i][1])!=0:
                pd_nfri_data = pd_nfri_data.append(cs_nifr_list[i][1][ID[j]])
                ## Save single file for each record number.
                cs_nifr_list[i][1][ID[j]].to_csv(ID[j]+'.csv',sep='\t',index=False)
# Save the whole meta data file.
pd_nfri_data.to_csv('pd_nfri_data.csv',sep='\t',index=False)


# # Part 3 Data mining for NIFS database

# In[ ]:


# I extract nifs species list to find common species in both databases.
## Open the file of nifs species.
nifs_species_list = []
with open('nifs_species.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        nifs_species_list.append(row[0])
nifs_species_list = nifs_species_list[1:]
nifs_species_list = list(set(nifs_species_list))

# Find common species in QDB specie list and NIFS database.
nifs_qdb_species = []
for i in range (len(nifs_species_list)):
    if nifs_species_list[i] in species_list:
        nifs_qdb_species.append(nifs_species_list[i])


# In[ ]:


# Do data mining for NIFS database and save basic information data and meta data for each specie.
cs_nifs_list = []
for i in range (len(nifs_qdb_species)):
    cs_nifs = creeper_nifs.creep_species_nifs(nifs_qdb_species[i].strip())
    cs_nifs.extract_basic_information()
    cs_nifs.extract_data()
    cs_nifs_list.append([cs_nifs.pd_specie,cs_nifs.data_list])

# Combine basic information data for all species.
pd_nifs_main = pd.DataFrame(columns=['specie','record_number','process','QDB_process','type','element',                                    'ionic_state','initial_state_conf','initial_state',                                    'final_state','reaction_formula','x_unit','y_unit',                                    'reference_number','author','title_of_record','journal_name',                                    'volume_and_issue_No','page_number','date_of_publication'])
for i in range (len(cs_nifs_list)):
    pd_nifs_main = pd_nifs_main.append(cs_nifs_list[i][0])
# Save the file.
pd_nifs_main.to_csv('pd_nifs_main.csv',sep='\t',index=False)

# Combine meta data for all record numbers
pd_nifs_data = pd.DataFrame(columns=['ID','X','Y','X_error','Y_error'])
for i in range (len(cs_nifs_list)):
    ID = cs_nifs_list[i][0]['record_number'].tolist()
    for j in range (len(ID)):
        if len(cs_nifs_list[i][1])!=0: # If the length of meta data is 0, I don't need to append it.
            pd_nifs_data = pd_nifs_data.append(cs_nifs_list[i][1][ID[j]])
            ## Save single file for each record number.
            cs_nifs_list[i][1][ID[j]].to_csv(ID[j]+'.csv',sep='\t',index=False)
# Save the whole meta data file.
pd_nifs_data.to_csv('pd_nifs_data.csv',sep='\t',index=False)


# # Part 4 Delete duplicate data

# In[ ]:


# Extract NFRI meta data.
pd_nfri_data = []
with open("pd_nfri_data.csv") as csvfile:
    csvreader = csv.reader(csvfile, delimiter="\t")
    for line in csvreader:
        pd_nfri_data.append(line[:])
pd_nfri_data = pd.DataFrame(data=pd_nfri_data[1:],columns=pd_nfri_data[0])
# Change the format of x value.
for i in range (len(pd_nfri_data)):
    pd_nfri_data['X'].iloc[i] = Decimal(pd_nfri_data['X'].iloc[i]).normalize()
    
# Extract NIFS meta data
pd_nifs_data = []
with open("pd_nifs_data.csv") as csvfile:
    csvreader = csv.reader(csvfile, delimiter="\t")
    for line in csvreader:
        pd_nifs_data.append(line[:])
pd_nifs_data = pd.DataFrame(data=pd_nifs_data[1:],columns=pd_nifs_data[0])
# Change the format of x value.
for i in range (len(pd_nifs_data)):
    pd_nifs_data['X'].iloc[i] = Decimal(pd_nifs_data['X'].iloc[i]).normalize()
    
# Extract NFRI basic information data.
pd_nfri_main = []
with open("pd_nfri_main.csv") as csvfile:
    csvreader = csv.reader(csvfile, delimiter="\t")
    for line in csvreader:
        pd_nfri_main.append(line[:])
pd_nfri_main = pd.DataFrame(data=pd_nfri_main[1:],columns=pd_nfri_main[0])
# Extract NFRI species list.
nfri_specie = list(set(pd_nfri_main['specie'].tolist()))
for i in range (len(nfri_specie)):
    nfri_specie[i] = nfri_specie[i].strip()

# Extract NIFS basic information data.
pd_nifs_main = []
with open("pd_nifs_main.csv") as csvfile:
    csvreader = csv.reader(csvfile, delimiter=",")
    for line in csvreader:
        pd_nifs_main.append(line[:])
pd_nifs_main = pd.DataFrame(data=pd_nifs_main[1:],columns=pd_nifs_main[0])
# Extract NIFS species list.
nifs_specie = list(set(pd_nifs_main['specie'].tolist()))
for i in range (len(nifs_specie)):
    nifs_specie[i] = nifs_specie[i].strip()

# Find common species of two databases.
specie_common = []
for i in range (len(nifs_specie)):
    if nifs_specie[i] in nfri_specie:
        specie_common.append(nifs_specie[i])


# In[ ]:


# Find the common record numbers in two databases.
common_results = {}
for i in range (len(specie_common)):
    ddd = delete_duplicate_data.delete_duplicate_data(specie_common[i])
    common_result = ddd.search_title()
    if len(common_result) != 0: # I only need to record common species which have common meta data.
        common_results[specie_common[i]] = common_result

# Record record numbers which need to be deleted in NIFS database.
delete_record_number = []
list_common_keys = list(common_results.keys())
for i in range (len(list_common_keys)):
    common_result = common_results[list_common_keys[i]]
    for j in range (len(common_result)):
        delete_record_number.append(common_result[j][1])
delete_record_number = list(set(delete_record_number))

# Find record numbers that are not in delete_record_number list.
nifs_main_record_number = list(set(pd_nifs_main.record_number))
nifs_rest_record_number = []
for i in range (len(nifs_main_record_number)):
    if nifs_main_record_number[i] not in delete_record_number:
        nifs_rest_record_number.append(nifs_main_record_number[i])


# In[ ]:


# Delete duplicate basic information data and meta data in NIFS database, and combine two databases together.
pd_nifs_main_rest = pd_nifs_main[pd_nifs_main.record_number.isin(nifs_rest_record_number)]
pd_nifs_main_rest = pd_nifs_main_rest.reindex(columns=['specie','record_number','process','QDB_process',                                   'type','element','ionic_state','initial_state_conf',                                   'initial_state','final_state','reaction_formula',                                   'x_unit','y_unit','reference_number','author',                                   'title_of_record','journal_name','volume_and_issue_No',                                   'page_number','date_of_publication','DOI'],fill_value='')
main = pd_nfri_main.append(pd_nifs_main_rest)
# Save the file.
main.to_csv('main.csv',sep='\t',index=False)

pd_nifs_data_rest = pd_nifs_data[pd_nifs_data.ID.isin(nifs_rest_record_number)]
data = pd_nfri_data.append(pd_nifs_data_rest)
# Save the file.
data.to_csv('data.csv',sep='\t',index=False)

