import pandas as pd

def get_filtering_dict(logic_dict, combination):
    filtering_dict = {}
    for key in logic_dict.keys():

        if logic_dict[key] == 'value':
            filtering_dict [key] = combination[key]
        else:
            filtering_dict [key] = logic_dict[key] + '()'
    
    return filtering_dict

def get_filtering_query(filtering_dict):
    filtering_query = ''
    for key in filtering_dict.keys():
        if not filtering_dict[key].endswith('()'):
            filtering_query += key + '== "' + filtering_dict[key] + '"'
        else:
            filtering_query += key + '.'+ filtering_dict[key]

        filtering_query += ' & '

    filtering_query = filtering_query.strip(' &')
    
    return filtering_query


def filter_data(dataset_1, dataset_2, filtering_query, origin_mapping):
    dataset_1_subset = dataset_1.query(filtering_query)
    
    if dataset_2:
        dataset_2_subset = dataset_2.query(filtering_query)

        counts = {'dataset_1':dataset_1_subset.shape[0]
              , 'dataset_2':dataset_2_subset.shape[0]}

        if counts['dataset_1']> counts['dataset_2']:
            datasets = {'left':{'origin':origin_mapping['dataset_1']
                                ,'data':dataset_1_subset.copy(deep = True)}
                       ,'right':{'origin':origin_mapping['dataset_2']
                                 ,'data':dataset_2_subset.copy(deep = True)}
                       }

        else:
            datasets = {'left':{'origin':origin_mapping['dataset_2']
                                ,'data':dataset_2_subset.copy(deep = True)}
                       ,'right':{'origin':origin_mapping['dataset_1']
                                 ,'data':dataset_1_subset.copy(deep = True)}
                       }

        return datasets
    else:
        return dataset_1_subset

def get_combinations(dataset_1, dataset_2, blocking_columns):
    if bool(blocking_columns):
        if dataset_2:
            combinations = (pd.concat([dataset_1[blocking_columns]
                                  , dataset_2[blocking_columns]])
                        .drop_duplicates()
                        .dropna()
                       )
        else:
            combinations = (dataset_1[blocking_columns]
                            .drop_duplicates()
                            .dropna()
                           )

        combinations = combinations.to_dict(orient = 'records')

        return combinations
        