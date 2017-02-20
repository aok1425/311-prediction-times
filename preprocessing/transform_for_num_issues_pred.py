# TODO: if I had more time, search Census for some measure of whether residnential or commerical
# bc in fidi lotsa issues bc parking, non-residential stuff

from __future__ import division
import pandas as pd
import shapegeocode
from datetime import datetime
import re
from tqdm import tqdm


BLOCK_GROUP_BLACKLIST = ["9807001", "9818001", "0303003", "0701018", "9811003"] # these are parks or South Station
OUTLIERS_COMMERCIAL_INDUSTRIAL = ['0102034', '0107013', '0512001', '0612002', '0701012', '1101033', '9812021']
OUTLIERS_LOW_POP = ['0005024', '0008032', '0103002', '0104051']


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


def get_weighted_ys(df):
    """For num_issues, assigns weight to type so that we can compare block groups w/o worrying about TYPE"""
    num_issues_total = df.shape[0]
    df_num_issues_by_type = df[['TYPE', 'CASE_ENQUIRY_ID']].groupby('TYPE').count().sort_values('CASE_ENQUIRY_ID', ascending=False)
    df_num_issues_by_type['proportion'] = df_num_issues_by_type.CASE_ENQUIRY_ID / num_issues_total
    d_proportion = df_num_issues_by_type['proportion'].to_dict()    

    df1 = df[['TYPE', 'CASE_ENQUIRY_ID', 'tract_and_block_group']].groupby(['tract_and_block_group', 'TYPE']).count().reset_index()
    df1['NUM_ISSUES_WEIGHTED'] = df1.TYPE.map(d_proportion) * df1.CASE_ENQUIRY_ID

    df2 = df1[['tract_and_block_group', 'NUM_ISSUES_WEIGHTED']].groupby('tract_and_block_group').sum().reset_index()

    return df2


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


def get_count_table(df, by_year=False, weighted=False):
    if by_year:
        assert weighted is False
        df_subset = df[['tract_and_block_group', 'OPEN_DT']]
        df_subset['year'] = df_subset.OPEN_DT.map(lambda x: x.year)
        df_subset.drop('OPEN_DT', axis=1, inplace=True)
        df_subset['NUM_ISSUES'] = 1
        df_subset1 = df_subset.groupby(['tract_and_block_group', 'year']).sum().reset_index()
    else:
        df_subset = df[['tract_and_block_group']]
        df_subset['NUM_ISSUES'] = 1
        df_subset1 = df_subset.groupby('tract_and_block_group').sum().reset_index()        
        
        if weighted:
            df_subset1 = df_subset1.merge(get_weighted_ys(df), on='tract_and_block_group', how='left')
            assert df_subset1.NUM_ISSUES_WEIGHTED.isnull().sum() == 0

    df_subset2 = add_population(df_subset1)

    # NB: dividing by pop not that good bc eg high-density downtown has low pop
    # better to have num_ppl_at_1pm or sth like that

    # this was to make per pop. it performed v badly on Lasso.
    df_subset2['NUM_ISSUES_PER_100_POP'] = df_subset2['NUM_ISSUES'] * 100 / df_subset2['population_total']
    # df_subset2.drop('NUM_ISSUES', axis=1, inplace=True)
    df_subset2['NUM_ISSUES_PER_100_POP'] = df_subset2['NUM_ISSUES_PER_100_POP'].replace(pd.np.inf, pd.np.nan).fillna(df_subset2['NUM_ISSUES_PER_100_POP'].median())

    return df_subset2.drop('population_total', axis=1)
    return df_subset2


def make_dummies(row):
    l = ['Request for Snow Plowing',
         'Schedule a Bulk Item Pickup',
         'Parking Enforcement',
         'Missed Trash/Recycling/Yard Waste/Bulk Item',
         'Graffiti Removal']    
    
    for col in l:
        if row['TYPE'] == col:
            row[col.replace(' ', '').replace('/', '')] = True
        else:
            row[col.replace(' ', '').replace('/', '')] = False
            
    return row    


def get_top_n_table(df, n=4):
    """Gets the 5 most popular categs overall and returns table showing if ea categ is in census block for that yr"""
    df = df.copy()
    df['year'] = df.OPEN_DT.map(lambda x: x.year)    
    aa = df[['year', 'tract_and_block_group', 'TYPE', 'CASE_ENQUIRY_ID']]
    
    # http://stackoverflow.com/questions/27842613/pandas-groupby-sort-within-groups
    df_agg = aa.groupby(['year', 'tract_and_block_group', 'TYPE']).count()
    g = df_agg['CASE_ENQUIRY_ID'].groupby(level=[0,1], group_keys=False)

    ans = g.nlargest(n)    

    cc = ans.reset_index().sort_values(['year', 'tract_and_block_group'])
    top_n = cc[['TYPE', 'year']].groupby('TYPE').count().sort_values('year', ascending=False).reset_index().head().TYPE.tolist()

    trans_groupbys = lambda rows: rows.apply(make_dummies, axis=1)
    ans2 = cc.groupby(['year', 'tract_and_block_group']).apply(trans_groupbys) \
        [['year', 'tract_and_block_group', 'RequestforSnowPlowing', 'ScheduleaBulkItemPickup', 'ParkingEnforcement', \
        'MissedTrashRecyclingYardWasteBulkItem', 'GraffitiRemoval']].drop_duplicates()

    # hopefully the NAs are only in the dummy cols. too lazy to write more specific
    ans2.fillna(False, inplace=True)

    return ans2


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
    return df.drop(cols_to_remove, axis=1)


def drop_duplicates(df, **kwargs):
    return df.drop_duplicates()


def drop_outliers(df, **kwargs):
    outliers = OUTLIERS_LOW_POP + OUTLIERS_COMMERCIAL_INDUSTRIAL + BLOCK_GROUP_BLACKLIST
    df1 = df[~df.tract_and_block_group.isin(outliers)]
    assert df.shape != df1.shape
    return df1


def main(df, by_year=False, **kwargs):
    for fn in [group_table, removing_cols, drop_duplicates, drop_outliers]:
        df = fn(df, by_year=by_year, **kwargs)

    return df


if __name__ == '__main__':
    df_orig = pd.read_pickle('../data/data_from_remove_from_dataset.pkl')
    df = main(df_orig, by_year=False, weighted=False)
    df.to_csv('../data/tableau_Q1_block_group_level.csv', index=False, encoding='utf-8')   
