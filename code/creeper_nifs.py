#!/usr/bin/env python
# coding: utf-8

# This file is class designed for doing data mining for a given specied in NIFS database.Befroe the main functions conducting, I define two classes to help.
# <p> Firstly, I define a function to define process, as QBD cannot be judged directly from the original process.
# <p> Secondly, I define a function to connect website process with QDB process. 
# Then, in the main functions:
# <p> Firstly, for a given specie, I retrieve all basic information for each record number, including reference information, reaction formula, process, sub process, states and so on.
# <p> Then, for a given record number, I retrieve all the meta data.

# In[ ]:


import csv
import pandas as pd
import re
from nltk.stem import PorterStemmer 
from selenium import webdriver
from time import sleep
import sys
ps = PorterStemmer()


# In[ ]:


class creep_species_nifs:
    
    def __init__(self,specie):
        self.specie = specie
        self.data_list = {}
        
    # Define a function to do pre-processing for procss.
    def define_process(self,process):
        if re.search(";",process) != None: # If there is ";",  the process contains multi processes.
            process = re.sub("[;]"," ",process)
            process_list = re.split(" ",process) # Split the process into single word for the purpose of connecting QDB process.
        else:
            process_list = re.split(" ",process) # Split the process into single word for the purpose of connecting QDB process.
        return process_list
    
    # Define a function to connect website process wtih QDB process.
    def QDB_process(self,process_list):
        
        ## Set it empty in case there is no related QDB process.
        abbreviation = ""
        
        ## Judge whether there is a related QDB process, if there is, reset the value of "QDB".
        if "deexcitation" in process_list:
            abbreviation = "EDX"
            
        if ("elastic" in process_list) and ("scattering" in process_list):
            abbreviation = "EEL"
            
        if "ionization" in process_list:
            if "dissociative" in process_list:
                abbreviation = "EDI"
            elif ("electron" in process_list) and ("total" in process_list):
                abbreviation = "ETI"
            else:
                abbreviation = "EIN"
                
        if "dissociation" in process_list:
            abbreviation = "EDS"
        
        if "recombination" in process_list:
            if "radiative" in process_list:
                abbreviation = "ERR"
            elif "dissociative" in process_list:
                abbreviation = "EDR"
            else:
                abbreviation = "ERC"
                
        if ("momentum" in process_list) and ("transfer" in process_list):
            abbreviation = "EMT"

        if "attachment" in process_list:
            if "dissociative" in process_list:
                abbreviation = "EDA"
            elif "electron" in process_list:
                if "total" in process_list:
                    abbreviation = "ETA"
                else:
                    abbreviation = "EDT"
                    
        if ("total" in process_list) and ("scattering" in process_list):
            abbreviation = "ETS"


        if "excitation" in process_list:
            if "dissociative" in process_list:
                abbreviation = "EDE"
            elif "electronic" in process_list:
                    abbreviation = "EEX"
            elif "vibrational" in process_list:
                    abbreviation = "EVX"
            else:
                abbreviation = "ECX"
           
        return abbreviation
    
    # Define a function to extract basic information for a given specie.
    def extract_basic_information(self):
        
        ## Search for the given specie.
        driver = webdriver.Chrome()
        driver.get("http://dbshino.nifs.ac.jp/nifsdb/nifs_db/select")
        driver.find_element_by_xpath("/html/body/h2[2]/ul/a[5]").click()
        sleep(5) # In case I don't get into the website
        driver.find_element_by_xpath("/html/body/form/ul[1]/table[1]/tbody/tr[1]/td[3]/input").send_keys(self.specie) # Enter the specie.
        driver.find_element_by_id("btn_search").click() 

        # Click the boxes to display and extract basic information later.
        if len(driver.find_elements_by_id("display_format_custom")) != 0:
            driver.find_element_by_id("display_format_custom").click()
            for i in range (7):
                if i != 5:
                    for j in range (4):
                        if (i==0 and j!=3) or (i==1 and j!=1) or (i==2 and j!=3) or (i==3 and j!=0) or (i==6 and j<2) or i==4:
                            x_path = "/html/body/form/ul[2]/table/tbody/tr["                                     + str(i + 1) + "]/td[" + str(j + 1)+"]/input[2]"
                            driver.find_element_by_xpath(x_path).click()
            driver.find_element_by_id("btn_find_display").click()

            # Extract basic information
            cout = len(driver.find_elements_by_xpath("//body/form/ul"))
            specie = []
            record_number = []
            process = []
            QDB = []
            type_name = []
            element = []
            ionic_state = []
            initial_state_conf = []
            initial_state = []
            final_state = []
            reaction_formula = []
            reference_number = []
            author = []
            title_of_record = []
            journal_name = []
            volume_and_issue_No = []
            page_number = []
            data_of_publication = []
            x_unit = []
            y_unit = []

            for k in range (cout):

                ## Extract basic information and splitting it to classify them.
                text_xpath = "/html/body/form/ul["+str(k+1)+"]" # Find whole information location
                text = driver.find_element_by_xpath(text_xpath).text # Extract the information.
                text_split = re.split('[\n]',text) # Split text through "enter"
                len_text = len(text_split)
                result_text = []
                 
                # Split text through "=" to get value for each attribute
                for a in range (len_text):
                    locate = re.search('[=]',text_split[a]).span()[1]
                    result_text.append(text_split[a][locate:]) 

                # Define specie through charge.
                text_element = result_text[3].strip()
                if text_element==self.specie:
                    if result_text[4].strip()=='1': # The specie is with positive charge.
                        specie.append(self.specie+"+")
                    if result_text[4].strip()=='-1': # The specie is with nagetive charge.
                        specie.append(self.specie+"-")
                    if result_text[4].strip()=='0': # The specie is without charge.
                        specie.append(self.specie)
                    
                    # Memorize record number and process.
                    record_number.append(result_text[0].strip())
                    process.append(re.sub("[;]"," ",result_text[1].strip()))
                    
                    # Split process and then define QDB process
                    process_list = self.define_process(result_text[1].strip())
                    QDB.append(self.QDB_process(process_list))
                    
                    # Memorize basic information
                    type_name.append(result_text[2])
                    element.append(result_text[3])
                    ionic_state.append(result_text[4])
                    initial_state_conf.append(result_text[5])
                    initial_state.append(result_text[6])
                    final_state.append(re.sub("[;]","+",result_text[7])) # Replace ";" with "+" to make the products in one column.
                    reaction_formula.append(result_text[8])
                    reference_number.append("RN"+result_text[9]) # Add "RN" in case of the mathematic formation of "E"
                    author.append(re.sub("[,$]"," ",result_text[10])) # Replace "," and "$" to make the author in one column.
                    title_of_record.append(result_text[11])
                    journal_name.append(result_text[12])
                    volume_and_issue_No.append(result_text[13])
                    page_number.append(result_text[14])
                    data_of_publication.append(result_text[15])
                    x_unit.append(result_text[16])
                    y_unit.append(result_text[17])
                # Record basic information.
                self.pd_specie = pd.DataFrame(data=[specie,record_number,process,QDB,type_name,\
                                                    element,ionic_state,initial_state_conf,\
                                                    initial_state,final_state,reaction_formula,\
                                                    x_unit,y_unit,reference_number,author,title_of_record,\
                                                    journal_name,volume_and_issue_No,\
                                                    page_number,data_of_publication],\
                                             index=['specie','record_number','process','QDB_process','type','element',\
                                                    'ionic_state','initial_state_conf','initial_state',\
                                                    'final_state','reaction_formula','x_unit','y_unit',\
                                                    'reference_number','author','title_of_record','journal_name',\
                                                    'volume_and_issue_No','page_number','date_of_publication']).T

            # Close the website.
            driver.close()
        else:
            # Close the website.
            driver.close()  
    
    # Define a function to extract meta data.
    def extract_data(self):
        # Get into the website to get meta data for a given specie.
        driver = webdriver.Chrome()
        driver.get("http://dbshino.nifs.ac.jp/nifsdb/nifs_db/select")
        driver.find_element_by_xpath("/html/body/h2[2]/ul/a[5]").click()
        sleep(5) # In case I don't get into the website
        driver.find_element_by_xpath("/html/body/form/ul[1]/table[1]/tbody/tr[1]/td[3]/input").send_keys(self.specie) # Enter the specie.
        driver.find_element_by_id("btn_search").click()

        # Click for meta data graph.
        if len(driver.find_elements_by_id("display_format_numeric")) != 0:
            driver.find_element_by_id("display_format_numeric").click()
            driver.find_element_by_id("btn_find_display").click() # Display the graph
            sleep(5) # In case I don't get into the website
            driver.find_element_by_id("display_write_vertical").click()
            driver.find_element_by_id("btn_num_display").click() # Show all the meta data.

            # Count the number of meta data for a given record number.
            cout = len(driver.find_elements_by_xpath("//body/form/ul"))
            for i in range (cout):
                text = driver.find_element_by_xpath("//body/form/ul["+str(i+1)+"]").text # Find record number location.
                record_number = re.split('[\n=]',text)[1]
                if record_number in self.pd_specie["record_number"].tolist(): # Only record meta data whose record number in list.
                    # Extract meta data.
                    X = []
                    Y = []
                    X_error = []
                    Y_error = []
                    data_xpath = "/html/body/form/ul["+str(i+1)+"]/ul/table/tbody/tr" # Find meta data location.
                    amount = len(driver.find_elements_by_xpath(data_xpath)) # Count the number of meta data.
                    for k in range (amount):
                        if k != 0: # The first piece is not meta data.
                            x_path = "/html/body/form/ul["+str(i+1)+\
                                     "]/ul/table/tbody/tr["+str(k+1)+"]/td[1]"
                            y_path = "/html/body/form/ul["+str(i+1)+\
                                     "]/ul/table/tbody/tr["+str(k+1)+"]/td[2]"
                            y_error_path = "/html/body/form/ul["+str(i+1)+\
                                     "]/ul/table/tbody/tr["+str(k+1)+"]/td[3]"            
                            y_error_minus_path = "/html/body/form/ul["+str(i+1)+\
                                     "]/ul/table/tbody/tr["+str(k+1)+"]/td[4]" 

                            x = driver.find_element_by_xpath(x_path).text
                            y = driver.find_element_by_xpath(y_path).text
                                         
                            # Compute y error average which is the average value of y error minus and y error.
                            y_error = driver.find_element_by_xpath(y_error_path).text
                            y_error_minus = driver.find_element_by_xpath(y_error_minus_path).text
                            y_error_average = (abs(float(y_error))+abs(float(y_error_minus)))/2
                            x_error = 0 # This database doesn't include x error value, so I make it zero.

                            X.append(x)
                            Y.append(y)
                            X_error.append(x_error)
                            Y_error.append(y_error_average)

                    # Memorize meta data dataframe.
                    pd_data_1 = pd.DataFrame(data=[X,Y,X_error,Y_error],\
                                           index=['X','Y','X_error','Y_error']).T
                    pd_data_1 = pd_data_1
                    self.data_list[record_number] = pd_data_1.reindex(columns=['ID','X','Y','X_error','Y_error'],\
                                                                               fill_value=record_number
                                                                 )
            # Close the website.
            driver.close()

