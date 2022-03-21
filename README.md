# create_names_v2
second iteration of create_names prototype

# How to use:

1. Add source data 
    a. Add sentences to the sentences file (data/sentences) 
    b. Add keywords to the keywords file (data/keywords)

2. Run "create_keywords.sh"

3. Choose keywords 
    a. Open the keywords file (results/keywords.xlsx) 
    b. On column "Keyword shortlist (insert "s")", add "s" to keywords you like. (For test purposes, add 3 nouns, 3 verbs and 3 adjectives) 
    c. save file

4. Run "create_names.sh" 
    a. See names at results/names.xlsx 
    b. For raw data output, see tmp/names.json

# What's changed:

## Overall Process:

Before:
Add source data and name styles -> generate names -> review names and add keywords to white/blacklist -> generate names -> review...

Now:
Add source data (use 2000+ default name styles no need to add anything) -> generate keywords -> add keywords to whitelist -> generate names 
-> review names and keyword whitelist -> generate names -> review...

## keyword_generator.py

### discontinued modules
- modules.get_keyword_wiki_scores -> discontinued due to buggy scoring results. (Could be revived once more research can be done to improve scoring accuracy)
- modules.find_unique_lines -> discontinued as json data generated is not useful (spacy module now accepts list of text rather than dict of text)
- modules.import_keyword_list -> discontinued (replaced entire function with list(set(keywords)))
- modules.filter_keywords -> discontinued (copy pasted entire function into keyword_generator.py for better management)

### modules with changed names
- modules.extract_words_with_spacy.py -> changed to -> modules.process_text_with_spacy.py

### major changes
1. File import process simplified
    a. Both sentences and keyword lists are transformed into a list of unique elements by using list(set(list(data.read().splitlines()))
    b. Modules and functions that were built to import source text is now discontinued.
2. Spacy now used for both sentences and keyword list. 
    a. For keywords from keyword list, lemma generated from spacy is also used to pull pos from wordsAPI database
    b. For keywords from keyword list, Spacy_pos is removed as there is no surrounding text to accurately identify keyword pos. 
3. As users pick a small number of keywords, keyword scores has been entirely discontinued. 
    a. Keyword scores may be revived later on with more research to generate "reccommended keywords"
4. Keywords are now outputted as an excel file for user review. (Whitelist is generated here)

## name_generator.py

### discontinued modules
- None

### modules with changed names
- modules.combine_words -> changed to -> modules.make_names

### new modules
- modules.collect_algorithms -> algorithm collection function now a separate module

### major changes
1. Names output/storage updated 
    a. lists of dictionaries -> dictionary of lists of dictionaries
    b. Names are stored in nexted key/value pairs where the first key is "name_lower" (name in lowercase) and the second key is "name_title" (name components in titlecase) and the resulting value is a list of Names.
    c. Permutations of names could generate identical names from different sets of keywords. The new name storage system is designed to manage this and create a list of unique names with easy access to the multiple ways it was generated.

2. name style (algorithm) system updated
    a. "joints" and other text components are also considered as "keywords". 
    b. for text component, the pos designation will be the type of text component. (ie. pos of "joint" component will be "joint")
    c. There are three new standard text components: head, joint, tail.
        - "Head" component are text that come at the beginning of name (ie, "the-", "we-", "my-" etc.)
        - "Joint" component are text that come between other keywords (ie, "and", "to" etc.)
        - "Tail" component are text that come at the end of name (ie, "-studio", "-company", "-sport", "-&co" etc.)
    d. modifiers are now paired with each keyword. Modifiers can alter each keyword in a specific way (eg. extract first 3 letters "number" -> "num")

3. dictionaries are pulled only if required
    a. When the algorithm list is imported, a "list of required components" is generated. Dictionaries are pulled only if the specific component is in that list. (ie. the prefix dictionary is only imported if prefix is in the "list of required components")

4. Names do not contain "keyword scores" anymore 
    a. As mentioned in "keyword_generator.py", this value could be revived in the future with more research and development.

5. Names contain a list of keywords - this list is generated out of keywords used in multiple names creating identical names.

## classes.algorithm.py

### major changes
1. Uses the new algorithm class from ng_back_end repo
2. Components are stored in a list of component/modifier pairs
3. Added the new "Component" class
    a. Algorithm "component"s are a list of these objects

## classes.keyword.py

### major changes
1. Attribute order has changed - see classes.keyword.py

2. "Keyword" attributes have changed:
  a. "origin" -> type changed to list of strings so that mutiple origins can be stored
    b. "word" -> "source_word"
    c. "lemma" -> "spacy_lemma"
    d. "occurrence" -> "spacy_occurrence"
    e. "algorithm": REMOVED
    f. "keyword_user_score": REMOVED
    g. "keyword_wiki_score": REMOVED
    h. "keyword_total_score": REMOVED

3. New attributes to "Keyword" have been added:
    a. "pos": final "pos" based on both spacy and wordAPI "pos"
    b. "pairing_limitations": some keywords can be limited to be paired with specific types of keywords. (eg. rules such as "nouns" can only come after "verb" can be implemented this way)

4. "Modword" class have been added:
    a. "modifier": type of modification (eg. extract first 3 letters "number" -> "num"). Default is "no_mod" for "no modification required"
    b. "modword": keyword after modification. The modword will be used in the name, not keywords.(If no modification, keyword = modword)
    c. "modword_len": length of keyword after modification

5. Keyword/pos pairs found both in sentences and keyword lists are combined. (origin will be a list containing both "sentences" and "keyword_list")

## classes.name.py

### major changes
1. Attribute order has changed - see classes.name.py

2. "Name" attributes have changed:
    a. "name" -> "name_title"
    a. "name_length_score" -> "length_score"
    b. "name_score" -> "total_score"
    c. "all_keywords" -> "keywords" (list of unique keywords)
    d. "keyword1" -> REMOVED
    e. "keyword2" -> REMOVED
    f. "keyword_1_score" -> REMOVED
    g. "keyword_2_score" -> REMOVED

3. New attributes to "Name" have been added:
    a. "name_lower": name in lowercase form. "name" attribute contains the name in titlecase form.

4. "Domain" class have been added (not yet used - still subject to major change): 

    a. "tld_list": list of tlds requested by user
    b. "domain": list of domain, availability pairs stored in a tuple

## modules.process_text_with_spacy.py

### major changes
1. Name has changed from "extract_words_with_spacy" to "process_text_with_spacy"

2. Function input format has changed:
    a. Previously required a dictionary but now only requires a list of text

3. "Origin" attribute no longer assigned in module. (As both sentences and keyword_list will use this module)

## modules.get_wordAPI.py

### major changes

1. function "create_small_wordAPI" discontinued.
    a. Smaller versions of wordsAPI will no longer be saved.

2. function "update_pos_value" absorbed into function "verify_words_with_wordsAPI".
    a. pos variations of each keyword will be now created in "verify_words_with_wordsAPI"

3. A new function "check_wordsAPI_dict" created:
    a. This function will loop through wordsAPI database and fetch all the pos

4. Major modifications made to function "fetch_pos_wordAPI":
    a. Keyword will be first checked to see if it not None. (This was previously done outside this function)
    b. The pos "number" (changed from "NUM") will be assigned for keywords that are int/float or numbers spellt as text (contained in list "numbers_as_str")
    c. if spacy_pos is not None and it matches one of the pos found in the wordsAPI dictionary, other POS variants are discarded. If spacy_POS is not found in wordsAPI database, all possible variants are returned. (If not found, spacy has likely made an error.)
    d. Spacy POS format to wordsAPI pos format conversion also added. (dict called "pos_conversion")
    d. The POS of lemma is also searched. If the pos of the keyword returns empty, the correct POS can be found using lemma.

## modules.make_names.py

### major changes
1. Name has changed from "combine_words" to "make_names"

2. functions "combine_1_word", "combine_2_words", "combine_3_words" added.
    a. These functions are used based on the length of the algorithm or how many keywords are used (ie. if algorithm has 2 keywords, "combine_2_words" is used)
    b. The 

3. "name_key" is the list of keywords used. This will become the key for each name list in the final dict output.

4. function "keyword_modifier" added:
    a. Based on "modifier, the "Keyword" object will be transformed into a "Modword" object.
    b. Dunctions "combine_1_word", "combine_2_words", "combine_3_words" will only accept "Modword" objects as input (not "Keyword" objects).

5. Whether a keyword is a prefix, suffix etc. is no longer required to be identified. Attributes are assigned outside this module.

6. Name length scores slightly altered. (Still under development and is subject to change)

7. Keyword scores no longer calculated. (However function "combined_keyword_scorer" kept for potential future use). 