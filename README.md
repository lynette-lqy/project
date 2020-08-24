# project
This project is for Data mining for electron molecular collision cross section project. There are four folders in it.
## nfri_data
This folder is used to store each meta data for every record number and to store main reference file for NFRI database.
## nifs_data
This folder is used to store each meta data for every record number and to store main reference file for NIFS database.
## final_results
This folder is used to store the whole data for each database, including metadata and main data for each database.
##
This folder is used to store code files and the species list that I use when I operate the codes. Each code file is stored in two types - ".ipynb" and ".py", which means you can operate the codes in both Visual Code and Jupyter Notebook. However, I recommand you to operate "main.ipynb" in Jupyter Notebook.
The only file in this folder, which needs to be operated is "main" file. The "creeper_nfri" file is a class that is uesd to retrieve data from NFRI database. The "creeper_nifs" file is a class that is uesd to retrieve data from NIFS database. The "delete_duplicate" file is a class to delete duplicate records and metadata in both databases, I call these three funtions in "main" file.
