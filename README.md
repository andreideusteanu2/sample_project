# About

##### This repository contains Python Notebooks and Scripts for cleaning and combining 3 datasets
##### These datasets contain information about companies all over the world based on their website, google and facebook

# Environment used
In order to develop the matching pipeline I used a JupyterLab instance on a Google Cloud VM.
For storage I used a Google Cloud Storage Bucket
The Python version used is 3.7.12
All dependencies are listed in the requirements.txt file:
- Pandas library for working with tabular data
- Google Cloud Storage File System library for interacting with Google Cloud Storage as one would interact with a regular file system
- Record Linkage library for combining the datasets into a single one
- Jellyfish library for the calculation of Levenshtein edit distance and Jaro-Winkler string similarity
- FuzzyWuzzy library for the calculation of Levenshtein similarity ratio

# High Level Pipeline
## Step 1 - Clean and Understand the data
- represented in notebook Clean data.ipynb
## Step 2 - Find matches between 2 pairs of datasets
- represented in 3 notebooks:
    - Find Matches - Facebook_Google.ipynb
    - Find Matches - Facebook_Website.ipynb
    - Find Matches - Google_Website.ipynb
## Step 3 - Combine the matches from the pairs into a single dataset
- represented in notebook Unify Matched Data.ipynb
## Step 4 - Simplify and remove duplicate information from the single dataset
- represented in notebook Simplify Matched Data
## Step 5 - Deduplicate Matched Data
- represented in notebook Deduplicate Matched Data.ipynb

# Results
It is important to mention that this process described here acts only as a first stage of combining the 3 datasets into a single more useful one.

The approach outlined here does 2 things:
1. It combines Companies that are matching between either 2 of the datasets into a single view
2. It saves unmatched data separately for later use and enhancement

__Obviously unmatched data should be further explored__:
- are there other matching keys that could be used?
- is the unmatched data truly unique or did the matching logic miss some matches?
- in case no Country, Region, City information is available -> could a Machine Learning Classification algorithm be trained on the matched data to extract this information from the Address?
- could these be further reduced into a single dataset maybe by enforcing a common schema on them?
## Start
Based on the first step, I determined that the Google dataset has the most information ~ 360K rows, whereas the Website and Facebook datasets contain slightly less information at around 72K rows each.

However in the Google dataset, there is no unique key to use, plus there is a lot of duplicate information in terms of the domains - the most common domain is facebook with around 72K occurences.

Therefore I went for a fuzzy matching approach between pairs of datasets.
## End
In the end the approach resulted into 26344 companies that matched across the datasets.
## Improvements added by the process
Figures below are taken based on the output of the last cell in notebook Deduplicate Matched Data.ipynb
- Website dataset had no address information available. Now the address is available for 24373 companies
- Email was not available in the Website dataset. It is now available for 8517 of the companies
- Legal name was only available in the Website dataset. It is now available for 10444 companies
- Zip code was not available in the Website dataset. It is now available for 18297 companies
- Company description was not available in the Website dataset. It is now available for 11161 companies
- Address, Phone, Zip Codes had slightly different formats across the 3 datasets. In case they've matched they are now consistent in a single format, or if they did not represent the same phone number they are stored together separated by a / character
- Country, Region, City were not consistent across the 3 datasets. Now they're in the same format
- Companies that are duplicated across the 3 datasets are now separated from those that are unique to each dataset. However this last improvement is subject to the quality of the matching logic and fields used.

# Details of the Approach
## Step 1 - Clean and Understand the data
### Data Understanding
- represented in notebook Clean data.ipynb
- raw data is available in https://console.cloud.google.com/storage/browser/soleadify_sample_data/raw_data
- based on the exploration of data I have found several clusters of columns that can be used for matching:
    - Geographical information -> Country, Region, City
    - Domain
    - Company Name most commonly represented as Site Name
    - Phone Numbers
- besides these, there is also information unique to each dataset:
    - Website: legal_name, language and tld (top-level domain). Out of these 3, the legal_name is rather unique and possibly expanding the information available. Language and tld don't seem to be that useful.
    - Google: text. It seems to be a combination of address, Google Rating and something else.
    - Facebook: description, email, link, page_type. Out of these, the link is the least useful information. It is to some extent already included in the domain. Protocol is however not included here. Email, description are extremly useful and unique. Page Type can also be useful, but it's mainly subject to the definition used by Facebook.
### Data Cleaning
- apply some preprocessing on Country, Region, Citry, Site Name, Category to make them as consistent as possible across the 3 datasets:
    - Remove punctuation such as . " '
    - For City and Region remove numbers
    - Make them consistent in terms of case, be it UPPERCASE, Titlecase or lowercase
    - Combine Country related information - Country, Country Code, Phone Country Code - into a single column; for this ISO 3166-1 alpha-2 country codes are used to translate Country Codes into Country Names
- finally save these clean datasets in https://console.cloud.google.com/storage/browser/soleadify_sample_data/clean_data

## Step 2 - Find matches between 2 pairs of datasets
- represented in 3 notebooks:
    - Find Matches - Facebook_Google.ipynb
    - Find Matches - Facebook_Website.ipynb
    - Find Matches - Google_Website.ipynb
__Important Note: even after matching the Index from the original datasets is kept. The Index is an integer representing the position of a row in a certain dataset. This ensures that at any point the process a row can be traced back to its original dataset.__
- There are 5 stages of logic applied between each of the 3 pairs:
    1. Fuzzy Match on Domain and Site Name for Companies with the same Country, Region, City
    2. Fuzzy Match on Domain and Site Name for Companies with the same Country, Region that do not have City available
    3. Fuzzy Match on Domain and Site Name for Companies with the same Country that do not have City, Region available
    4. Fuzzy Match on Domain and Site Name for Companies with that do not have Country, City, Region available
    5. Fuzzy Match on Domain for Companies that do not have Site Name, Country, City, Region available
- fuzzy matching has been done using Record Linkage Library:
    - Country, Region, City -> acted as blocking columns gradually eliminating them
    - Domain and Site Name -> sort the datasets by these columns and take the 3 nearest neighbours from the left dataset to the right dataset
    - Fuzzy Match using Jaro-Winkler similarity score. If the score was above 0.85 it was considered a match
- the matching is represented in code using the file:matching.py, function:match which calls upon the function:get_matches to do the Sorted Neighbours pairs and calculate Jaro-Winkler similarity score.
- at each stage of logic data was written in a Google Cloud Storage bucket in a directory corresponding to the pairs of datasets
    - Facebook Google https://console.cloud.google.com/storage/browser/soleadify_sample_data/facebook_google_matches
    - Facebook Website https://console.cloud.google.com/storage/browser/soleadify_sample_data/facebook_website_matches
    - Google Website https://console.cloud.google.com/storage/browser/soleadify_sample_data/google_website_matches
    
### Why was the approach that follows chosen?
The approach to go from matched data across pairs of datasets to a 1 dataset for all was basically to:
1. combine all the paired data under a single schema and dataset - simply put a UNION in SQL terms 
2. reduce to the extent possible columns containing the same information into a single column - for instace instead of having 2 address fields keep only 1 address field matching / combining the previous 2 fields
3. apply a logic to deduplicate the resulting set - simply put a form of DISTINCT in SQL terms

An alternative approach could have been to JOIN again the dataset pairs.
However:
- this would have been even more reliant on the quality of the data and logic used in the JOIN Keys. At the moment of the implementation, I felt that the UNION approach allowed me to have more control over how I determine what entities I keep
- it may have left out some combinations. There are 3 original datasets and therefore 3 pairs of 2 datasets. Combining only based on 2 of the pairs could have wrongly left out some matches.

That was the rationale behind this approach. At the time of this development I thought it was best.
However based on the difficulty and low performance of the approach outlined in Step 5, I think the JOIN approach would have been better than the UNION + DISTINCT approach.
    
## Step 3 - Combine the matches from the pairs into a single dataset
- represented in notebook Unify Matched Data.ipynb
- the result from Step 2 was a set of around 4000 different csv files, one for each matching combination of Country, Region, City across the pairs of datasets
- this step does 2 things:
    - it reads data from all these 4000 files into 3 single datasets, one for each pair
    - it creates a common schema
    - it combines the 3 datasets into 1 single one with a unitary schema
- combined data is written in a CSV file here https://storage.cloud.google.com/soleadify_sample_data/unified_matched_data/matches_full.csv

## Step 4 - Simplify and remove duplicate information from the single dataset
- represented in notebook Simplify Matched Data
- based on step 3 there is some duplicate information in the columns:
    - Address, Zip Code, Phone, Site Name, Country, Region, City, Domain
- Country, Region, City, Domain were reduced to a single column using exact matching
- Zip Code and Phone Number both rely on a Levenshtein distance calculation and matching. This is available in code in the file:matching.py, function: is_levenstein_matching
- Zip Code was reduced to a single column as follows:
    - calculate the Levenshtein distance between Zip Code from Facebook vs the one from Google
    - if this distance is between the difference in length between the 2 strings +/-1 -> it's a match, otherwise they are different
    - this interval tries to make sure that the edit difference is caused by an extra space characther or different casing, and not by difference in the actual characthers
    - in case of a match -> only 1 zip code is retained. Otherwise both of them are retained separated by a / characther
- Phone number was reduced to a single column as follows:
    - Google Raw Phone offered the best format for human readability and interpretability. Therefore, if possible, this was the preffered one to keep
    - calculate the Levenshtein distance between Phone Number from Google vs the one from Facebook and Website respectively.
    - in case of a match -> Google Phone Number is kept
    - otherwise:
        - if there is a match between Website and Facebok Phone, keep the one from Website combined with the one from Google separated by a / characther
        - if not, all 3 were kept separated by a / characther
    - in case the Google Phone was not available:
        - check if Facebook and Website Phone match -> if they do keep the one from Website; if not keep both separated by / characther
        - if only the Facebook or Website Phone was available, keep the one that is available
- Address was reduced to a single column as follows:
    - Calculate the partial_ratio, token_sort_ratio and token_set_ratio using fuzzywuzzy library
    - These 3 functions are based on the Levenshtein distance and ratio combining this with some string preprocessing. They are documented here -> https://www.datacamp.com/community/tutorials/fuzzy-string-python and here -> https://towardsdatascience.com/string-matching-with-fuzzywuzzy-e982c61f8a84
    - This calculation is represented in code in file:matching.py, function:is_fuzzy_address_matching
    - If the absolute difference between the Partial Ratio and the Token Sort Ratio was less than or equal to 5 or if the Token Set Ratio was higher than 85, then these addresses were considered to be a match.
    - If the addresses matched, the longest string was kept. Otherwise both of them were kept separated by a / characther.
- This step finally wrote data to the file https://storage.cloud.google.com/soleadify_sample_data/unified_matched_data/matches_simplified.csv

## Step 5 - Deduplicate Matched Data
- represented in notebook Deduplicate Matched Data.ipynb
- There were in the simplified 29,761 rows in the dataset, however 26,350 unique entities in the dataset. Therefore some deduplication was needed.
- The challenge of this step was to combine information across rows into a single view. 1 row had the data from the Facebook - Website pair whereas another row had data from the Google - Facebook pair.
- The approach relies on the file:matching.py, function:unify_rows. The logic basically does a row by row comparison. It takes the values of the columns from the first row. Then if a following row has a NOT NULL information in 1 of the columns it takes that. Also if the length of the information in the following information is higher - it takes that one. (assumption take - a string of higher length contains more information than a shorter one)
- Finally unique, matched data is written to the file -> https://storage.cloud.google.com/soleadify_sample_data/unified_and_unmatched_data/unified_unique.csv
- The based on the Index unmatched data from the original datasets is separated into 3 different files based on their original source:
    - https://storage.cloud.google.com/soleadify_sample_data/unified_and_unmatched_data/facebook_unmatched.csv
    - https://storage.cloud.google.com/soleadify_sample_data/unified_and_unmatched_data/google_unmatched.csv
    - https://storage.cloud.google.com/soleadify_sample_data/unified_and_unmatched_data/website_unmatched.csv


# Critiques of the Approach and Improvement Points
1. The resulting dataset is small - only around 36.5% of the Facebook / Website datasests or 7.3% of the Google dataset. This could mean 2 things:
    a. The approach used for matching did not have enough coverage. If finally the Domain fuyzzy matching failed could the address have been used?
    b. Assuming the matching did its best using the available information, further development is needed to enhance the information available in the 3 datasets.
2. Category field is not unified. This information is rather different across the 3 datasets and I could not find an easy solution to combine them.
3. The unified unique dataset is not truly unique. There is still 1 duplicate Root Domain, several 

# Possible next steps


