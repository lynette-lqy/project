#!/usr/bin/env python
# coding: utf-8

# This file is class designed for doing data mining for a given specied in NFRI database.Befroe the main functions conducting, I define three classes to help.
# <p> Firstly, I define a function to connect website process with QDB process. 
# <p> Secondly, I define a function to define specie and state, in other words, to make sure whether it has charge, because it's not listed on the website.
# <p> Thirdly, I define a function to extract reference information for a given record number.
# Then, in the main functions:
# <p> Firstly, I define a function to extract all URL links and their types which are related to electron impact for a given specie.
# <p> Then, for a given URL link, I retrieve all basic information for recommanded type, including record number, reference information, reaction formula, process, sub process.
# <p> Finally, for a given record number, I retrieve all the meta data.

# In[ ]:


import csv
import pandas as pd
import re
from nltk.stem import PorterStemmer 
from selenium import webdriver
from time import sleep
ps = PorterStemmer()


# In[ ]:


class creep_species_nfri:
    
    def __init__(self,specie):
        
        self.specie = specie
        self.pd_data_dict = {}
        self.pd_specie = pd.DataFrame(columns=['specie','record_number','process','QDB_process',                                               'type','element','ionic_state','initial_state_conf',                                               'initial_state','final_state','reaction_formula',                                               'x_unit','y_unit','reference_number','author',                                               'title_of_record','journal_name','volume_and_issue_No',                                               'page_number','date_of_publication'])
        
    # Define a function to connect website process wtih QDB process.
    def define_QDB_process(self,process):
        
        # Set it empty in case there is no related QDB process.
        QDB = ''
        
        # Judge whether there is a related QDB process, if there is, reset the value of "QDB".
        if process == 'Electron Impact Total Scattering':
            QDB = "ETS"
        if process == 'Electron Impact Total Ionization':
            QDB = "ETI"
        if process == 'Electron Impact Elastic Scattering':
            QDB = "EEL"
        if process == 'Electron Impact Momentum Transfer  Scattering':
            QDB = "EMT"       
        if process == 'Electron Impact Partial Ionization':
            QDB = "EIN"
        if process == 'Electron Impact Vibrational Excitation':
            QDB = "EVX"
        if process == 'Electron Impact Neutral Product Dissociation Dissociation':
            QDB = "EDS"
        if process == 'Electron Impact Dissociative Attachment':
            QDB = "EDA"
        if process == 'Electron Impact Electronic Excitation':
            QDB = "EEX"        
        if process == 'Electron Impact Rotational Excitation':
            QDB = "ECX"      
        if process == 'Electron Impact Total Attachment':
            QDB = "EDA" 
        if process == 'Electron Impact Single Ionization':
            QDB = "EIN"
        if process == 'Electron Impact Dissociative Excitation':
            QDB = "EDE"        
        if process == 'Electron Impact Total Dissociation':
            QDB = "EDS"
        if process == 'Electron Impact Total Excitation':
            QDB = "EEX"  
        if process == 'Electron Impact Total Neutral Fragments Dissociation':
            QDB = "EDS"  
        if process == 'Electron Impact Momentum Transfer Scattering':
            QDB = "EMT"          
        if process == 'Electron Impact Electronic Ionization':
            QDB = "EIN"  
        if process == 'Electron Impact Neutral Fragments Dissociation':
            QDB = "EDS"  
        if process == 'Electron Impact State Selectivity Dissociation':
            QDB = "EDS"  
            
        return QDB
    
    # Define a function to define specie.
    def define_specie(self,reaction_formula):
        
        # Judge whether there is an arrow in the reaction formula, if there is, the products and the final state exists. 
        # Then, extract the reactants and make formula_1 equal to it.
        if re.search('[->]',reaction_formula) == None:
            formula_1 = reaction_formula # Define reactants.
            final_state = "" # Define final_state.
        else:
            situation = re.search('[-]+[>]',reaction_formula).span()[0] # Find where reactants end.
            situation_end = re.search('[-]+[>]',reaction_formula).span()[1] # Find where final state begin.
            formula_1 = reaction_formula[:situation+1] # Define reactants.
            final_state = reaction_formula[situation_end+1:] # Define final_state.
        
        # Judge whether there is parenthese in the formula_1, if there is, the initial state conf exists.
        # The define specie is the specie begin from the search and before parenthese. 
        if re.search('[(]',formula_1) == None:
            start = re.search(self.specie,formula_1).span()[0] # Search for the given specie and where it starts.
            end = re.search(self.specie,formula_1).span()[1] + 1 # Search for the given specie and where it ends.
            define_specie = formula_1[start:end] # Define the specie.
            initial_state_conf = "" # Define initial state conf.
        else:
            start = re.search(self.specie,formula_1).span()[0] # Search for the given specie and where it starts.
            end = re.search('[(]',formula_1).span()[0] # Find where parenthese starts.
            define_specie = formula_1[start:end] # Define the specie.
            start_1 = re.search('[)]',formula_1).span()[0] # Find where parenthese ends.
            initial_state_conf = formula_1[end+1:start_1] # Define initial state conf.
         
        # Define the inion state by means of searching for "+" and "-" in the reaction formula.
        if "+" in define_specie:
            ionic_state = 1 # Define that the specie is with positive charge.
        elif  "-" in define_specie:
            ionic_state = -1 # Define that the specie is with negative charge.
        else:
            ionic_state = 0 # Define that the specie is without charge.
        
        # Define initial state which includes defined specie and initial state conf.
        initial_state = formula_1[start:]

        return define_specie,ionic_state,initial_state_conf,initial_state,final_state
    
    #Define a function to extrac reference information
    def extract_DOI(self,No_list_recommended_data):
        
        # Extract reference number through record number and go the website.
        website_basic_information = "https://dcpp.nfri.re.kr/search/popupViewBasic.do?plBiDataNum="                                    + No_list_recommended_data[3:] # Get the URL link.
        driver_basic_information = webdriver.Chrome()
        driver_basic_information.get(website_basic_information) # Go to that website.
        
        # Get the reference number.
        reference_num = driver_basic_information.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[1]/td/a/span").text
        
        # Close the website.
        driver_basic_information.close()

        # Get the reference information website through reference number. 
        website_reference_link = "https://dcpp.nfri.re.kr/search/popupViewArticle.do?plRaiArtclNum="                                    + reference_num # Get the URL link.
        driver_reference_link = webdriver.Chrome()
        driver_reference_link.get(website_reference_link) # Go to the website.
        
        # Extract reference information
        ## Extract DOI information.
        DOI = driver_reference_link.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[5]/td").text
        ## Extract title information.
        title = driver_reference_link.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[2]/td").text
        ## Extract author information.
        author = driver_reference_link.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[3]/td").text
        author = re.sub(","," ",author) # Sub "," with space.
        ## Extract journal name information
        journal_name = driver_reference_link.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[4]/td").text
        ## Extract volume and issue number information.
        volume_and_issue_No = driver_reference_link.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[10]/td").text                              + driver_reference_link.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[7]/td").text
        ## Extract page number information.
        page_number = driver_reference_link.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[12]/td").text                      + "/" +  driver_reference_link.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[13]/td").text
        ## Extract date of publication information.
        date_of_publication =  driver_reference_link.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[14]/td").text

        # Close the website.
        driver_reference_link.close()

        return DOI,title,author,journal_name,volume_and_issue_No,page_number,date_of_publication,reference_num
    
    # Record all URL links for a given specie.
    def get_website(self):
        
        # Get through the website where I find the data
        driver = webdriver.Chrome()
        driver.get("https://dcpp.nfri.re.kr/index.do")
        
        # Enter the species we want to find 
        driver.find_element_by_id('keyword').send_keys(self.specie)
        sleep(2) # Sleep in case that the website hasn't opened.
        driver.find_element_by_id('searchimg').click()
        sleep(2) # Sleep in case that the website hasn't opened.    
        
        # Find the cross section id
        ## Find URL links which are related with electron impact.
        urls = driver.find_elements_by_xpath("//div[@id='containerPlBiDataBranchDB_02-MP_01-IC_01']/a")
        
        # Extract cross section id, URL links and type.
        cross_section_id = []
        cross_section_urls = []
        cross_section_type = []
        ## Get the attribute "ID" of each URL link.
        if len(urls) != 0:
            for url in urls:
                id = url.get_attribute("id")
                cross_section_id.append(id)

            # Through cross section id I can find all the links
            len_cross_section_id = len(cross_section_id)
            if len_cross_section_id != 0: # If it is equal to 0, it means there is no URL links.
                for i in range (len_cross_section_id):
                    # if the length is more than 4, I need to page turning to get URL links
                    if i > 4:
                        driver.find_element_by_id('btnPlBiDataBranchNext:DB_02-MP_01-IC_01').click() # Find page turning icon and click it.
                    driver.find_element_by_id(cross_section_id[i]).click()
                    # Get the current URL link and record it.
                    now_url = driver.current_url
                    cross_section_urls.append(now_url)
                    driver.back()
                    
                # Define cross section type through cross section id
                for i in range (len_cross_section_id):
                    type_xpath = "//a[@id='"+cross_section_id[i]+"']/strong" # Find type name location through id.
                    type_name = driver.find_element_by_xpath(type_xpath).text # Extract type name.
                    cross_section_type.append(type_name)
                    
            # Close the website.
            driver.close()
        else:
            # Close the website.
            driver.close()
          
        # Memorize cross section informaion in the class.
        self.cross_section_urls = cross_section_urls
        self.cross_section_type = cross_section_type
     
    # Define a function to extract basic information
    def extract_pd_specie(self,url,type_name):
        
        # Go to the website for a given cross section type which is connected with URL link.
        driver_specie = webdriver.Chrome()
        driver_specie.get(url)
        
        # Extract units information.
        ## Find x unit
        x_label = driver_specie.find_elements_by_class_name("nv-axislabel")[0].text # Find the location of x unit.
        if re.search('[[]',x_label) != None:
            x_begin = re.search('[[]',x_label).span()[1] # Find the start of x unit.
            x_end = re.search('[]]',x_label).span()[0] # Find the end of x unit.
            x_unit = x_label[x_begin:x_end]
        else:
            x_unit = 'eV' # If the figure doesn't show x label, it will be assigned "eV".
        ## Find y unit   
        y_label = driver_specie.find_elements_by_class_name("nv-axislabel")[1].text # Find the location of y unit.
        if re.search('[[]',y_label) != None:
            y_begin = re.search('[[]',y_label).span()[1] # Find the start of y unit.
            y_end = re.search('[]]',y_label).span()[0] # Find the end of y unit.
            y_unit = y_label[y_begin:y_end]
        else:
            y_unit = '1E-16 cm^2' # If the figure doesn't show y label, it will be assigned "1E-16 cm^2".
        
        # Extract all the record number for a given type
        No_list_xpath = driver_specie.find_elements_by_xpath("//table[@class='table_list datatable']/tbody/tr") # Find record number location.
        No_list = []
        for No in No_list_xpath:
            No_list.append(No.get_attribute("id")) # Record "ID" to judge whether it is recommanded later.

        # Extract recommended data record number.
        No_list_recommended_data = []
        for i in range (len(No_list)):
            xpath = "//tr[@id='"+No_list[i]+"']/td[8]" # Find theory location.
            ## Get theory and in case the text is hidden, I use "innerText".
            theory = driver_specie.find_elements_by_xpath(xpath)[0].get_attribute("innerText")
            if theory == "Recommended Data": # If theory is recommaned, append record number.
                No_list_recommended_data.append(No_list[i])
        
        # Extract basic information for each record number.
        for i in range (len(No_list_recommended_data)):
            ## Define current record number.
            ID = No_list_recommended_data[i]
            ## Extract meta data for a given ID.
            result_DOI = self.extract_DOI(ID)
            ## Define type.
            type = "R"
            
            # Extract reaction formula.
            xpath_reaction_formula = "//tr[@id='"+ID+"']/td[5]" # Find reaction formula location.
            reaction_formula = driver_specie.find_elements_by_xpath(xpath_reaction_formula)[0].get_attribute("innerText") # Get reaction formula.
    
            #extract collision method.
            xpath_collision_method = "//tr[@id='"+ID+"']/td[6]" # Find collision method.
            collision_method = driver_specie.find_elements_by_xpath(xpath_collision_method)[0].get_attribute("innerText") # Get collision method.
            
            # Extract sub process
            xpath_sub_process = "//tr[@id='"+ID+"']/td[7]" # Find sub process location.
            sub_process = driver_specie.find_elements_by_xpath(xpath_sub_process)[0].get_attribute("innerText") # Get sub process.
            
            # Define specie name, ionic state, initial state conf, initial state and final state through define specie function.
            specie_name = self.define_specie(reaction_formula)[0]
            ionic_state = self.define_specie(reaction_formula)[1]
            initial_state_conf = self.define_specie(reaction_formula)[2]
            initial_state = self.define_specie(reaction_formula)[3]
            final_state = self.define_specie(reaction_formula)[4]
            
            # Combine collision method, sub process and type name into process
            process = collision_method + " " + sub_process + " " + type_name
            QDB_process = self.define_QDB_process(process)
            
            # Memorize the record and add it into the dataframe.
            pd_single_specie = pd.DataFrame(data = [specie_name,ID,process,QDB_process,                                                    type,self.specie,ionic_state,initial_state_conf,                                                    initial_state,final_state,reaction_formula,                                                    x_unit,y_unit,result_DOI[7],result_DOI[2],                                                    result_DOI[1],result_DOI[3],result_DOI[4],                                                    result_DOI[5],result_DOI[6],result_DOI[0]],                                           index = ['specie','record_number','process','QDB_process',                                                    'type','element','ionic_state','initial_state_conf',                                                    'initial_state','final_state','reaction_formula',                                                    'x_unit','y_unit','reference_number','author',                                                    'title_of_record','journal_name','volume_and_issue_No',                                                    'page_number','date_of_publication','DOI']).T
            self.pd_specie = self.pd_specie.append(pd_single_specie,sort=False)
        
        # Close the website.
        driver_specie.close()
    
    # Define a function to extract meta data.
    def extract_data(self):
        
        # Get all cross section URL links.
        self.get_website()
        
        if len(self.cross_section_urls) != 0:
        
            for i in range (len(self.cross_section_urls)):
                url = self.cross_section_urls[i]
                ## Extract type name.
                type_name = self.cross_section_type[i]
                ## Extract basic information for a given type.
                self.extract_pd_specie(url,type_name)

            # Get record number list.
            ID_list = self.pd_specie['record_number'].tolist()

            # Extract meta data for each record number.
            for j in range (len(ID_list)):
                ## Get the URL link.
                website_view_data = "https://dcpp.nfri.re.kr/search/popupView.do?type=numerical&plBiDataNum="+str(ID_list[j][3:])
                ## Get into the website.
                driver_view_data = webdriver.Chrome()
                driver_view_data.get(website_view_data)
                ## Count number of meta data
                cout = len(driver_view_data.find_elements_by_xpath("//tbody[@id='tbody']/tr"))

                X = []
                Y = []
                X_error = []
                Y_error = []

                ## Extract meta data
                for i in range (cout):
                    ### Find positions
                    xpath_x = "//tbody[@id='tbody']/tr[" + str(i + 1) + "]/td[1]"
                    xpath_y = "//tbody[@id='tbody']/tr[" + str(i + 1) + "]/td[2]"
                    xpath_x_err = "//tbody[@id='tbody']/tr[" + str(i + 1) + "]/td[3]"
                    xpath_y_max_err = "//tbody[@id='tbody']/tr[" + str(i + 1) + "]/td[4]"
                    xpath_y_min_err = "//tbody[@id='tbody']/tr[" + str(i + 1) + "]/td[5]"

                    ### Record data
                    x_value = driver_view_data.find_elements_by_xpath(xpath_x)[0].text
                    y_value = driver_view_data.find_elements_by_xpath(xpath_y)[0].text
                    x_err = driver_view_data.find_elements_by_xpath(xpath_x_err)[0].text
                    y_max_err = driver_view_data.find_elements_by_xpath(xpath_y_max_err)[0].text
                    y_min_err = driver_view_data.find_elements_by_xpath(xpath_y_min_err)[0].text
                    
                    ### Judge whether y max error is equal to y min error. If it's true, just keep one of them, otherwise keep them both.
                    if float(y_max_err) == float(y_max_err):
                        y_err = y_max_err
                    else:
                        y_err = "Max:" + y_max_err + "/Min:" + y_min_err


                    X.append(x_value)
                    Y.append(y_value)
                    X_error.append(x_err)
                    Y_error.append(y_max_err)

                # Close the website.
                driver_view_data.close()

                # Memorize meta data dataframe and build a library to record it for each ID.
                pd_data = pd.DataFrame(data = [X,Y,X_error,Y_error],                                       index = ['X','Y','X_error','Y_error']).T
                pd_data = pd_data.reindex(columns=['ID','X','Y','X_error','Y_error'],                                                   fill_value=ID_list[j])
                self.pd_data_dict[ID_list[j]] = pd_data

