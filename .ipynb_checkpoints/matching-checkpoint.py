import recordlinkage as rl
import pandas as pd
import helpers as h
import jellyfish
from fuzzywuzzy import fuzz

def get_matches(left_dataset, right_dataset, similar_columns):
    #based on https://towardsdatascience.com/performing-deduplication-with-record-linkage-and-supervised-learning-b01a66cc6882
    indexer = rl.Index()
    for column in similar_columns:
        indexer.add(rl.index.SortedNeighbourhood(left_on = column
                                             , right_on = column
                                             , window = 3))
    combined_index = indexer.index(left_dataset['data'], right_dataset['data'])
    
    combined_index_unqiue = combined_index.drop_duplicates(keep='first')
    
    #based on https://medium.com/@appaloosastore/string-similarity-algorithms-compared-3f7b4d12f0ff
    compare = rl.Compare(n_jobs = -1)
    for column in similar_columns:
        compare.string(column, column, method = 'jarowinkler'
                       , label = column+'_similarity_score', threshold=0.85)

    comparison_vectors = compare.compute(combined_index_unqiue, left_dataset['data'], right_dataset['data'])
    
    similarity_query = ''
    
    for column in similar_columns:
        similarity_query += column+'_similarity_score == 1.0 & '
    
    similarity_query = similarity_query.strip(' &')
    
    true_links = comparison_vectors.query(similarity_query).index
    match_left = (left_dataset['data']
                .loc[list(true_links.get_level_values(0))]
                .reset_index()
                 )
    match_right = (right_dataset['data']
                .loc[list(true_links.get_level_values(1))]
                .reset_index()
            )
    
    subset_of_matches = match_left.join(match_right, lsuffix =  '__'+left_dataset['origin']
                          , rsuffix = '__'+right_dataset['origin'])
    
    subset_of_matches = subset_of_matches.reindex(sorted(subset_of_matches.columns), axis=1)
    
    return subset_of_matches

def unify_rows(dataset, blocking_columns):
    out = {}
    for row in dataset.iterrows():
        row = row[1]
        for column in row.keys():
            if column in blocking_columns:
                out[column] = row[column]
            else:
                if out.get(column) is None or pd.isna(out.get(column)):
                    out[column] = row[column]
                else:
                    if not pd.isna(row[column]) and not pd.isna(out[column]):
                        if len(str(out[column])) < len(str(row[column])):
                            out[column] = row[column]
    
    return out


def match(dataset_1, dataset_2, origin_mapping, similar_columns, logic_dict, combination):
    
    blocking_columns = []
    for column in logic_dict.keys():
        if logic_dict[column] == 'value':
            blocking_columns.append(column)
    
    filtering_dict = h.get_filtering_dict(logic_dict, combination)
    filtering_query = h.get_filtering_query(filtering_dict)
    
    datasets = h.filter_data(dataset_1, dataset_2, filtering_query, origin_mapping)
    subset_of_matches = get_matches(datasets['left'], datasets['right'], similar_columns)

    return subset_of_matches
    

def is_levenstein_matching(string_1, string_2, fuzzy = True):
    if fuzzy:
        distance = jellyfish.levenshtein_distance(string_1,string_2)
        length_1 = len(string_1)
        length_2 = len(string_2)

        if distance <= abs(length_1 - length_2)+1 and distance >= abs(length_1 - length_2)-1:
            return True
        else:
            return False
    
    else:
        return string_1 == string_2
    
def is_fuzzy_address_matching(address_1, address_2):
    #based on https://www.datacamp.com/community/tutorials/fuzzy-string-python
    partial_ratio = fuzz.partial_ratio(address_1, address_2)
    sort_ratio = fuzz.token_sort_ratio(address_1, address_2)
    set_ratio = fuzz.token_set_ratio(address_1, address_2)
    
    if abs(partial_ratio - sort_ratio) <=5 or set_ratio >=85:
        return True
    else:
        return False