# TODO: if I had more time, search Census for some measure of whether residnential or commerical
# bc in fidi lotsa issues bc parking, non-residential stuff

from __future__ import division
import pandas as pd
import shapegeocode
from datetime import datetime
import re
from tqdm import tqdm

import os, sys
sys.path.append(os.path.join(os.path.dirname('.'), "../app/models"))

from outliers import outliers


def dummify(df, column, keep_baseline=False):
    # from Darren's linear regression slides   
    if keep_baseline:
        dummy = pd.get_dummies(df[column]).rename(columns=lambda x: column+'_'+str(x))
        print '{} is your baseline'.format(sorted(df[column].unique())[-1]) 
    else:
        dummy = pd.get_dummies(df[column]).rename(columns=lambda x: column+'_'+str(x)).iloc[:,0:len(df[column].unique())-1]
    
    df = df.drop(column,axis=1) #Why not inplace? because if we do inplace, it will affect the df directly             
    return pd.concat([df,dummy],axis=1)


def add_population(df, just_dict=False):
    # will use race_total as proxy for pop for Census block group
    # just_dict is for making the API endpoint
    df_pop = pd.read_csv('../data/census-data/ACS_15_5YR_B03002_with_ann.csv', header=1)
    df_pop.insert(0, 'tract_and_block_group', df_pop['Id2'].apply(lambda id_: str(id_)[-7:]))
    df_pop = df_pop[['tract_and_block_group', 'Estimate; Total:']]
    df_pop = df_pop.rename(index=str, columns={'Estimate; Total:': 'population_total'})
    
    if just_dict:
        ans = df_pop.set_index('tract_and_block_group')['population_total'].to_dict()
        return ans

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


def get_count_table(df, by_year=False):
    if by_year:
        df_subset = df[['tract_and_block_group', 'OPEN_DT']]
        df_subset['year'] = df_subset.OPEN_DT.map(lambda x: x.year)
        df_subset.drop('OPEN_DT', axis=1, inplace=True)
        df_subset['NUM_ISSUES'] = 1
        df_subset1 = df_subset.groupby(['tract_and_block_group', 'year']).sum().reset_index()
    else:
        df_subset = df[['tract_and_block_group']]
        df_subset['NUM_ISSUES'] = 1
        df_subset1 = df_subset.groupby('tract_and_block_group').sum().reset_index()        

    df_subset2 = add_population(df_subset1)
    df_subset2['NUM_ISSUES_PER_1000_POP'] = df_subset2['NUM_ISSUES'] * 1000 / df_subset2['population_total']
    # df_subset2.drop('NUM_ISSUES', axis=1, inplace=True)
    # df_subset2['NUM_ISSUES_PER_1000_POP'] = df_subset2['NUM_ISSUES_PER_1000_POP'].replace(pd.np.inf, pd.np.nan).fillna(df_subset2['NUM_ISSUES_PER_1000_POP'].median())

    # return df_subset2.drop('population_total', axis=1)
    return df_subset2


def group_table(df, by_year=False, **kwargs):
    mode_table = get_mode_table(df, ['Source', 'Property_Type'])
    count_table = get_count_table(df, by_year, **kwargs)
    table = df.loc[:, 'tract_and_block_group': 'income_std_dev'].drop('is_description', axis=1).drop_duplicates() # brittle
    
    new_df1 = table.merge(mode_table, on='tract_and_block_group', how='left')
    new_df2 = new_df1.merge(count_table, on='tract_and_block_group', how='left')

    # hacky
    if by_year:
        # new_df2 = new_df1.merge(count_table, on=['tract_and_block_group', 'year'], how='left')
        assert 'year' in count_table.columns
        top_n_table = get_top_n_table(df)
        new_df2 = new_df2.merge(top_n_table, on=['tract_and_block_group', 'year'], how='left')

    assert new_df2.Source.isnull().sum() == 0
    # assert new_df2.is_description.isnull().sum() == 0
    return new_df2


def removing_cols(df, **kwargs):
    cols_to_remove = ['CASE_ENQUIRY_ID', 'LOCATION_ZIPCODE', 'LATITUDE', 'LONGITUDE', 'description', 'COMPLETION_HOURS_LOG_10',
        'queue_wk', 'queue_wk_open', 'OPEN_DT', 'CLOSED_DT', 'SubmittedPhoto', 'TYPE', 'Source', 'Property_Type']
    cols_to_remove = ['queue_wk', 'queue_wk_open', 'Source', 'Property_Type']  
    cols_to_remove = ['CASE_ENQUIRY_ID', 'LOCATION_ZIPCODE', 'LATITUDE', 'LONGITUDE', 'description', 'COMPLETION_HOURS_LOG_10',
        'queue_wk', 'queue_wk_open', 'OPEN_DT', 'CLOSED_DT', 'SubmittedPhoto', 'TYPE', 'zipcode', 'neighborhood_from_zip']          
    return df.drop(cols_to_remove, axis=1)


def assert_no_duplicates(df, **kwargs):
    df1 = df.drop_duplicates()
    assert df.shape == df1.shape
    return df


def drop_outliers(df, **kwargs):
    df1 = df[~df.tract_and_block_group.isin(outliers)]
    assert df.shape != df1.shape
    return df1


def main(df, by_year=False, **kwargs):
    for fn in [removing_cols, group_table, assert_no_duplicates, drop_outliers]:
        df = fn(df, by_year=by_year, **kwargs)

    return df


if __name__ == '__main__':
    df_orig = pd.read_pickle('../data/data_from_remove_from_dataset.pkl')
    df = main(df_orig, by_year=False)
    df.to_csv('../data/tableau_Q1_block_group_level.csv', index=False, encoding='utf-8')   
