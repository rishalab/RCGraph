
import csv
from github import Github
from bs4 import BeautifulSoup
from knowledge_graph import construct_kg
from relation_extractor import Stanford_Relation_Extractor
from create_structured_csv import create_csv
from csv_utils import convert_to_json, clean_commits_csv, clean_readme_csv
import os

# using an access token
g = Github("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")


def kg_commits(repo,file_name):
    # repo = g.get_repo('PySimpleGUI/PySimpleGUI')
    
    commits = repo.get_commits(path=file_name)

    commits_list = []

    for commit in commits:
        commits_list.append(commit)
    print("Number of commits:",len(commits_list))
    commits_list.reverse()
    index = 273
    while index<len(commits_list):
        commit = commits_list[index]
        print("Commit: "+ str(index))
        index=index+1

        #print(commit.commit.message,commit.commit.committer.date, commit.sha)
        additions = ""
        deletions = ""

        for _file in commit.files:
            if _file.filename != file_name:
                continue
            patch = _file.patch
            
            if patch is None:
                patch=""
            patch_lines = patch.split("\n")
            
                # f.seek(0)
                # f.truncate()
            for line in patch_lines:
                if len(line) == 0 or len(line)==1:
                    continue
                if line[0] == "+" :
                    additions += (line[1:]+"\n")              
                    
                elif line[0]== "-":
                    deletions += (line[1:]+"\n")              
                    
            
        
        with open('./data/input/input_data.txt','w+') as f:
            f.write(additions)
        f.close()
        if len(additions) == 0:
            continue
        # Constructing kg on the readme file
        construct_kg(additions)
        Stanford_Relation_Extractor()
        create_csv(commit.commit.committer.date, commit.sha, "", "addition")

        if len(deletions) == 0:
            continue
        # Constructing kg on the readme file

        with open('./data/input/input_data.txt','w+') as f:
            f.write(deletions)
        f.close()
        construct_kg(deletions)
        Stanford_Relation_Extractor()
        create_csv(commit.commit.committer.date, commit.sha, "", "deletion")
                  
                # f.write(_file.patch)

def kg_readme(repo,file_name):
    readme = repo.get_contents(file_name)
    text = readme.decoded_content
    cleantext = BeautifulSoup(text, "lxml").text
    print(cleantext)
    with open('./data/input/input_data.txt','w+') as f:
            f.write(cleantext)
    f.close()
    construct_kg(cleantext)
    Stanford_Relation_Extractor()
    create_csv("", "", "readme", "")
   


# 'javascript', 'java,html','python','php','ruby','css','c#','c++'
languages = ['c']
for language in languages:
    if language == 'python' or language == 'javascript':
        continue
    print(language)


    repositories = g.search_repositories(query='language:'+language,sort='stars',order='desc')
    repo = repositories[1]
    
    if language == 'php':
        repo = g.get_repo('jquery/testswarm')
    print(repo.full_name)
    file_name = ""
    contents = repo.get_contents("")
    while len(contents)>0:
        file_content = contents.pop(0)
        if file_content.name.lower() == "readme.md":
            file_name = file_content.name
            break
    print(file_name)
    
    # kg_commits(repo,file_name)
    clean_commits_csv('./data/result/named_entity_input_data_.csv','./results/commits_'+repo.name+'.csv')
    convert_to_json('./results/commits_'+repo.name+'.csv','./results/commits_'+repo.name+'.json')
    kg_readme(repo,file_name)
    clean_readme_csv('./data/result/named_entity_input_data_readme.csv','./results/readme_'+repo.name+'.csv')

    with open('./data/result/named_entity_input_data_.csv','w') as out:
        writer = csv.DictWriter(out, fieldnames=['Type','Entity 1','Relationship','Type','Entity2','Date','Sha','Change'])
        writer.writeheader()
    with open('./data/result/named_entity_input_data_readme.csv','w') as out:
        writer = csv.DictWriter(out, fieldnames=['Type','Entity 1','Relationship','Type','Entity2','Date','Sha','Change'])
        writer.writeheader()
    break
    
    



