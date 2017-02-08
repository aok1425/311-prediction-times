from __future__ import division
import pandas as pd
import shapegeocode
from datetime import datetime
import re
from tqdm import tqdm


def dummify(df, column, keep_baseline=False):
    # from Darren's linear regression slides   
    if keep_baseline:
        dummy = pd.get_dummies(df[column]).rename(columns=lambda x: column+'_'+str(x))
        print '{} is your baseline'.format(sorted(df[column].unique())[-1]) 
    else:
        dummy = pd.get_dummies(df[column]).rename(columns=lambda x: column+'_'+str(x)).iloc[:,0:len(df[column].unique())-1]
    
    df = df.drop(column,axis=1) #Why not inplace? because if we do inplace, it will affect the df directly             
    return pd.concat([df,dummy],axis=1)


def add_population(df):
    # will use race_total as proxy for pop for Census block group
    df_pop = pd.read_csv('../data/census-data/ACS_15_5YR_B03002_with_ann.csv', header=1)
    df_pop.insert(0, 'tract_and_block_group', df_pop['Id2'].apply(lambda id_: str(id_)[-7:]))
    df_pop = df_pop[['tract_and_block_group', 'Estimate; Total:']]
    df_pop = df_pop.rename(index=str, columns={'Estimate; Total:': 'population_total'})
    
    new_df = pd.merge(df, df_pop, on='tract_and_block_group', how='left')

    return new_df


def get_mode_table(df, cols):
    """Return table w two cols, tract_and_block_group, and modes of `cols`"""
    return df[cols + ['tract_and_block_group']].groupby('tract_and_block_group').agg(lambda row: row.value_counts().index[0]).reset_index()    


def get_count_table(df):
    type_cols = [col for col in df.columns if 'TYPE' in col]
    df_subset = df[['tract_and_block_group', 'SubmittedPhoto', 'is_description'] + type_cols]
    df_subset['NUM_ISSUES'] = 1

    df_subset1 = df_subset.groupby('tract_and_block_group').sum().reset_index()
    df_subset2 = add_population(df_subset1)

    for col in ['SubmittedPhoto', 'is_description'] + type_cols:
        df_subset2[col] = df_subset2[col] / df_subset2['population_total']

        # replaces w median for block groups where no people live, but where there are 311 issues
        df_subset2[col] = df_subset2[col].replace(pd.np.inf, df_subset2[col].median())

    return df_subset2.drop('population_total', axis=1)


def get_count_table(df):
    df_subset = df[['tract_and_block_group']]
    df_subset['NUM_ISSUES'] = 1

    df_subset1 = df_subset.groupby('tract_and_block_group').sum().reset_index()
    df_subset2 = add_population(df_subset1)

    # this was to make per pop. it performed v badly on Lasso.
    # df_subset2['NUM_ISSUES_PER_POP'] = df_subset2['NUM_ISSUES'] / df_subset2['population_total']
    # df_subset2.drop('NUM_ISSUES', axis=1, inplace=True)
    # df_subset2['NUM_ISSUES_PER_POP'] = df_subset2['NUM_ISSUES_PER_POP'].replace(pd.np.inf, pd.np.nan).fillna(df_subset2['NUM_ISSUES_PER_POP'].median())

    # return df_subset2.drop('population_total', axis=1)
    return df_subset2


def group_table(df):
    mode_table = get_mode_table(df, ['Source', 'Property_Type'])
    count_table = get_count_table(df)
    table = df.loc[:, 'tract_and_block_group': 'income_std_dev'].drop('is_description', axis=1).drop_duplicates() # brittle
    
    new_df1 = table.merge(mode_table, on='tract_and_block_group', how='left')
    new_df2 = new_df1.merge(count_table, on='tract_and_block_group', how='left')

    assert new_df2.Source.isnull().sum() == 0
    # assert new_df2.is_description.isnull().sum() == 0
    return new_df2


def removing_cols(df):
    cols_to_remove = ['CASE_ENQUIRY_ID', 'LOCATION_ZIPCODE', 'LATITUDE', 'LONGITUDE', 'description', 'COMPLETION_HOURS_LOG_10',
        'queue_wk', 'queue_wk_open', 'OPEN_DT', 'CLOSED_DT', 'SubmittedPhoto', 'TYPE', 'Source', 'Property_Type']
    cols_to_remove = ['queue_wk', 'queue_wk_open', 'Source', 'Property_Type']        
    return df.drop(cols_to_remove, axis=1)


def drop_duplicates(df):
    return df.drop_duplicates()


def main(df):
    for fn in [group_table, removing_cols, drop_duplicates]:
        df = fn(df)

    return df


if __name__ == '__main__':
    input_path = '../data/data_from_remove_from_dataset_head.pkl'
    df = main(input_path)
    # df.to_hdf('../data/data_from_add_to_dataset.h5', key='data_from_add_to_dataset')
    # df.to_pickle('../data/data_from_add_to_dataset.pkl')    
