# create_names_v2
second iteration of create_names prototype

# How to use:

1. Create new project
	* a. Run `sh create_new_project.sh <your_project_name>` to create project files under `projects/`

2. Add source data 
    * a. Add a .txt file with relevant sentences to folder `projects/<your_project_name>/data/sentences/<filename>.txt`
    * b. Add a .txt file with relevant keywords to folder `projects/<your_project_name>/data/keywords/<filename>.txt`

3. Generate keywords from sentences and keywords
    * a. Run `create_keywords.sh <your_project_name>`

4. Choose keywords 
    * a. Open the keywords file under `projects/<your_project_name>/results/<your_project_name>_keywords_shortlist.xlsx`
    * b. Add "s" to keywords you want to shortlist on column "Keyword shortlist (insert "s")". (Ideally, add 8 nouns, 3 verbs, 3 adjectives and 1 adverb) 
    * c. Save file

5. Generate names and check domains
    * a. Run `create_names.sh <your_project_name>`
    * b. Run `check_domains.sh <your_project_name>`. This generates 200 available domain name ideas per name type. If you need more name ideas, run `check_domains.sh <your_project_name>`again and it will add the next 200 names if available. 
    * c. If you want to change or adjust your keywords selection, make the changes to the keywords file under `projects/<your_project_name>/results/<your_project_name>_keywords_shortlist.xlsx` and run `create_names.sh <your_project_name>`.