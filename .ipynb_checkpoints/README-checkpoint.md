# About

##### This repository contains Python Notebooks and Scripts for cleaning and combining 3 datasets
##### These datasets contain information about companies all over the world based on their website, google and facebook

# Environment used
In order to develop the matching pipeline I used a JupyterLab instance on a Google Cloud VM.
For storage I used a Google Cloud Storage Bucket
The Python version used is 3.7.12
All dependencies are listed in the requirements.txt file

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
## Start
## End
## Improvement added by the process

# Details of the Approach

# Improvement Points

# Possible next steps


