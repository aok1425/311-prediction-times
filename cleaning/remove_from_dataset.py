from __future__ import division
import pandas as pd
from zipcode_mapping import zipcode_mapping
from tqdm import tqdm


def clean_sources(df):
    df = df[df.Source.isin(['Constituent Call', 'Self Service', 'Citizens Connect App', 'Twitter'])]
    return df


def remove_null_ys(df):
    return df.dropna(subset=['CLOSED_DT'])


def drop_invalid_issues(df):
    exclusion_str = r'(duplicate of|administrative|never closed|invalid|no basis)'
    df1 = df[~df.CLOSURE_REASON.str.contains(exclusion_str, case=False, na=False)]
    return df1


def drop_duplicate_rows(df):
    return df.drop_duplicates()


def impute_where_no_census_data(df):
    """
    My plan is to impute with the statistics of the neighboring Census block group. 
    There are some areas where these statistics would change drastically upon crossing the street, 
    but from my local knowledge they are relatively few.
    """
    df = df.copy()
    df.sort_values('tract_and_block_group', inplace=True)
    df[[col for col in df.columns if 'race' in col or 'poverty' in col]] = df[[col for col in df.columns if 'race' in col or 'poverty' in col]] \
        .apply(lambda row: row.fillna(method='bfill'))
    df.sort_values('CASE_ENQUIRY_ID', inplace=True, ascending=False)
    return df


def drop_neg_ys(df):
    return df[df.COMPLETION_HOURS_LOG_10.notnull()]


def drop_cols(df):
    cols_to_drop = ['OnTime_Status', 
        'CASE_STATUS', 
        'CLOSURE_REASON', 
        'QUEUE',
        'Location', 
        'fire_district', 
        'pwd_district', 
        'city_council_district',
        'police_district',
        'neighborhood_services_district',
        'ward',
        'precinct',
        'land_usage',
        'TARGET_DT',
        'Department',
        'REASON', 
        'Property_ID',
        'CASE_TITLE',
        'SUBJECT',
        'neighborhood',
        'LOCATION_STREET_NAME',
        'ClosedPhoto',
        'Geocoded_Location',
        'is_issue_unresolved']

    return df.drop(cols_to_drop, axis=1)


def drop_internal_rows(df):
    df1 = df[~df.TYPE.str.contains('internal', case=False)]    
    df2 = df1[~df1.Source.isin(('City Worker App', 'Employee Generated', 'Maximo Integration'))]
    return df2


def add_my_zipcode_col(df):
    df['neighborhood_from_zip'] = df.zipcode.map(zipcode_mapping)
    return df


def drop_incorrect_latlongs(df):
    """
    Some lat/longs are incorrect. They are given the default location of City Hall.
    This affects Census block group, Census data, and imputed zipcode for NaNs.
    Since address is still given, we could impute via Google Maps API, but there are 42495 such rows.
    For the sake of time, I will regettably drop them and do a quick EDA on what they are, in case dropping them might bias our results.
    """
    df_offending = df[df.neighborhood.notnull()][df.neighborhood_from_zip != df.neighborhood][df.LATITUDE == 42.3594]
    offending_case_enquiry_ids = df_offending['CASE_ENQUIRY_ID']
    new_df = df[~df.CASE_ENQUIRY_ID.isin(offending_case_enquiry_ids)]
    return new_df


def main(input_path):
    df = pd.read_pickle(input_path)  

    for fn in tqdm([drop_duplicate_rows, clean_sources, remove_null_ys, drop_invalid_issues, drop_incorrect_latlongs,
        impute_where_no_census_data, drop_neg_ys, drop_cols, drop_internal_rows, add_my_zipcode_col]):
        df = fn(df)

    return df   


if __name__ == '__main__':
    input_path = '../data/data_from_add_to_dataset.pkl'
    df = main(input_path)
    df.to_pickle('../data/data_from_remove_from_dataset.pkl') 