# -*- coding: utf-8 -*-
"""
Created on Wed May 11 10:05:03 2022
Python Version : 3.9.7
Panda version : 1.3.3
Summary : count word frequency from job details found in csv file
@author: creme332
"""
import pandas as pd
import numpy as np
import re
from csv import writer

data_source_filename = 'TESTING.csv'
jobs_df = pd.read_csv(data_source_filename)
jobs_df.drop_duplicates(
    subset=None, keep='first', inplace=False)  # drop duplicates

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 500)

# construct a separate csv file for word count


def AnalyseLanguages(destination_filename):

    language_count = {
        "C++": 0, "Java": 0, "Python": 0, "Javascript": 0, "PHP": 0,
        "HTML": 0, "CSS": 0, "Node.js": 0, "Clojure": 0,
        "C#": 0, "Bash": 0, "Shell": 0, "PowerShell": 0, "Kotlin": 0,
        "Rust": 0, "Typescript": 0, "SQL": 0, "Ruby": 0, "Dart": 0
    }

    # languages that contain special characters.
    special_languages = ["C++", "Node.js", "C#"]
    # These languages are never substrings of other another language.

    # token testing : java, python, javascript, php, html, ...
    standard_languages = ["Java", "Python", "Javascript",
                          "PHP", "HTML", "CSS", "Clojure",
                          "PowerShell", "Kotlin", "Rust", "Typescript",
                          "SQL", "Ruby", "Dart", "Bash", "Shell"]
    # Java is  a substring of Javascript
    # SQL is a subtstring of mySQL, NoSQL
    # Ruby is a substring of "Ruby on Rails"
    # so substring method cannot be used here.

    # languages in language_count, special_languages, standard language must match exactly

    for row in range(len(jobs_df)):  # for each collected job details
        jobs_details = jobs_df.loc[row, "job_details"].lower()

        # 1st search : search for languages using token method
        # any symbol is used as string delimiter

        # list of words in job details
        words = re.findall(r'\w+', jobs_details)

        for i in range(0, len(words)):  # for each word in job details
            for lang in standard_languages:  # search for standard languages

                if lang.lower() == words[i]:
                    if(lang.lower() == "ruby"):  # distinguish between ruby and ruby on rails
                        if(i > len(words)-3):
                            # language is definitely ruby
                            language_count[lang] += 1
                        else:
                            if(words[i+1].lower() != "on" and words[i+2].lower() != "rails"):
                                # current word is not part of ruby on rails
                                language_count[lang] += 1
                    else:
                        language_count[lang] += 1  # other standard language

        # search special languages using substring
        for lang in special_languages:
            if lang.lower() in jobs_details:
                language_count[lang] += 1

    # save language_count to a csv file
    tester = pd.DataFrame(language_count.items(), columns=[
                          'Language', 'Frequency'])
    tester.to_csv(destination_filename, sep='\t',
                  encoding='utf-8-sig', index=False)

    display(tester)


def AnalyseDatabases(destination_filename):
    databases_count = {
        "MySQL": 0, "PostgreSQL": 0, "SQLite": 0, "MongoDB": 0,
        "Microsoft SQL Server": 0, "Redis": 0, "MariaDB": 0, "Firebase": 0,
        "Elasticsearch": 0, "Oracle": 0, "DynamoDB": 0, "Cassandra": 0,
        "IBM DB2": 0, "Couchbase": 0, "NoSQL": 0
    }  # Will misflag Oracle Cloud as Oracle database

    for row in range(len(jobs_df)):
        jobs_details = jobs_df.loc[row, "job_details"].lower()  # lower case

        # use substring method for database names with more than 1 word
        if("microsoft sql server" in jobs_details):
            databases_count["Microsoft SQL Server"] += 1

        if("ibm db2" in jobs_details):
            databases_count["IBM DB2"] += 1

        # use token method for single-word databases
        words = re.findall(r'\w+', jobs_details)

        for db in databases_count:
            if db.lower() in words:
                databases_count[db] += 1

    # save databases_count to a csv file
    lang_filename = destination_filename
    tester = pd.DataFrame(databases_count.items(), columns=[
                          'Database', 'Frequency'])
    tester.to_csv(lang_filename, sep='\t', encoding='utf-8-sig', index=False)

    # display(tester)


def AnalyseWebFrameworks(destination_filename):
    web_frameworks_count = {"Svelte": 0,
                            "ASP.NET Core": 0,
                            "FastAPI": 0,
                            "React.js": 0,
                            "Vue.js": 0,
                            "Express": 0,
                            "Spring": 0,
                            "Ruby on Rails": 0,
                            "Angular": 0,
                            "Django": 0,
                            "Laravel": 0,
                            "Flask": 0,
                            "Gatsby": 0,
                            "Symfony": 0,
                            "ASP.NET": 0,
                            "jQuery": 0,
                            "Drupal": 0,
                            "Angular.js": 0
                            }
    # asp.net vs asp.net core confusion
    special_web_frameworks = ["ASP.NET Core", "React.js", "Vue.js",
                              "Ruby on Rails", "Angular.js", "ASP.NET"]

    for row in range(len(jobs_df)):
        jobs_details = jobs_df.loc[row, "job_details"].lower()  # lower case

        for wb in special_web_frameworks:
            if wb.lower() in jobs_details:
                web_frameworks_count[wb] += 1

        # use token method for single-word databases
        words = re.findall(r'\w+', jobs_details)

        for wb in web_frameworks_count:
            if wb.lower() in words:
                web_frameworks_count[wb] += 1

    tester = pd.DataFrame(web_frameworks_count.items(), columns=[
                          'WebFrameworks', 'Frequency'])
    tester.to_csv(destination_filename, sep='\t',
                  encoding='utf-8-sig', index=False)
    display(tester)


def AnalyseOtherTools():

    # for the following tools/platforms/libraries, substring method only is required
    cloud_platforms = {"AWS": 0,
                       "Google Cloud Platform": 0,
                       "Microsoft Azure": 0,
                       "Heroku": 0,
                       "DigitalOcean": 0,
                       "Watson": 0,
                       "Oracle Cloud Infrastructure": 0
                       }

    libraries = {".NET Framework": 0,
                 "NumPy": 0,
                 ".NET Core": 0,
                 "Pandas": 0,
                 "TensorFlow": 0,
                 "React Native": 0,
                 "Flutter": 0,
                 "Keras": 0,
                 "PyTorch": 0,
                 "Cordova": 0,
                 "Apache Spark": 0,
                 "Hadoop": 0,
                 "Tableau": 0,
                 "Power BI": 0,
                 "Power Query": 0,
                 }

    other_tools = {
        "Git": 0,
        "Terraform": 0,
        "Kubernetes": 0,
        "Docker": 0,
        "Ansible": 0,
        "Yarn": 0,
        "Unreal Engine": 0,
        "Unity 3D": 0,
        "GitHub": 0,
    }  # Git is a substring of GitHub

    operating_system_count = {
        "Windows": 0,
        "Mac": 0,
        "Linux": 0,
    }

    # word frequency of Linux, GitHub

    for row in range(len(jobs_df)):
        jobs_details = jobs_df.loc[row, "job_details"].lower()

        # search cloud platforms
        for cp in cloud_platforms:
            if cp.lower() in jobs_details:
                cloud_platforms[cp] += 1

        # search libraries
        for lb in libraries:
            if lb.lower() in jobs_details:
                libraries[lb] += 1

        for tool in other_tools:
            if tool.lower() in jobs_details and tool != "Git":  # must distinguish between git and github
                other_tools[tool] += 1
        words = re.findall(r'\w+', jobs_details)
        if "git" in words:
            other_tools["Git"] += 1

        for os in operating_system_count:
            if os.lower() in jobs_details:  # must distinguish between git and github
                operating_system_count[os] += 1

    # save cloud platforms
    cloud_df = pd.DataFrame(cloud_platforms.items(), columns=[
        'CloudPlatforms', 'Frequency'])
    cloud_df.to_csv("CloudData.csv", sep='\t',
                    encoding='utf-8-sig', index=False)
    display(cloud_df)

    # save libraries
    libraries_df = pd.DataFrame(libraries.items(), columns=[
        'Libraries', 'Frequency'])
    libraries_df.to_csv("LibrariesData.csv", sep='\t',
                        encoding='utf-8-sig', index=False)
    display(libraries_df)

    # save tools
    tools_df = pd.DataFrame(other_tools.items(), columns=[
        'Tools', 'Frequency'])
    tools_df.to_csv("ToolsData.csv", sep='\t',
                    encoding='utf-8-sig', index=False)
    display(tools_df)

    # save OS
    os_df = pd.DataFrame(operating_system_count.items(), columns=[
        'OS', 'Frequency'])
    os_df.to_csv("OSData.csv", sep='\t',
                 encoding='utf-8-sig', index=False)
    display(os_df)


AnalyseOtherTools()
# AnalyseWebFrameworks("WebData.csv")
# AnalyseLanguages("LanguageCountData.csv")
# AnalyseDatabases("DatabasesCountData.csv")
# AnalyseDatabases("DatabasesCountData.csv")
# AnalyseDatabases("DatabasesCountData.csv")
# AnalyseDatabases("DatabasesCountData.csv")