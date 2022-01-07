import recordlinkage as rl
import pandas as pd

def get_matches(left_dataset, right_dataset, similar_columns):
    indexer = rl.Index()
    for column in similar_columns:
        indexer.add(rl.index.SortedNeighbourhood(left_on = column
                                             , right_on = column
                                             , window = 3))
    combined_index = indexer.index(left_dataset['data'], right_dataset['data'])
    
    combined_index_unqiue = combined_index.drop_duplicates(keep='first')
    
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