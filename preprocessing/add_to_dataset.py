# this takes data_w_descs.pkl and census_data_aggregated.pkl

from __future__ import division
import pandas as pd
import shapegeocode
from datetime import datetime
import re
from tqdm import tqdm

from transform_census_variables import transform_census_variables
from adding_zipcodes import add_my_zipcodes
from zipcode_mapping import zipcode_mapping


def get_tract_block_group(lat, long_, shp_obj):
    d = shp_obj.geocode(lat, long_)
    return d['TRACTCE'] + d['BLKGRPCE']


def add_census_tract(df):
    gc = shapegeocode.geocoder('../data/shape-files/cb_2015_25_bg_500k.shp')
    df['tract_and_block_group'] = df[['LATITUDE', 'LONGITUDE']].apply(lambda row: get_tract_block_group(row['LATITUDE'], row['LONGITUDE'], gc), axis=1)
    return df


def add_census_data(df):
    df_census = pd.read_pickle('../data/census_data_aggregated.pkl')
    df_final = df.merge(df_census, on='tract_and_block_group', how='left')
    df_final = df_final.rename(index=str, columns={'income_per_capita': 'earned_income_per_capita'}) # for transform_census_variables
    return df_final


def convert_datetime(df):
    to_datetime = lambda d: datetime.strptime(d, '%m/%d/%Y %H:%M:%S %p') if type(d) != float else pd.np.NaN

    for col in ['OPEN_DT', 'CLOSED_DT', 'TARGET_DT']:
        if df.dtypes[col] != pd.np.dtype('datetime64[ns]'):
            df[col] = df[col].map(to_datetime)

    return df


def add_descriptions(df):
    if 'description' not in df.columns:
        df_descs = pd.read_pickle('../data/data_w_descs.pkl')
        df_descs = df_descs[['CASE_ENQUIRY_ID', 'description']]
        new_df = pd.merge(df, df_descs, on='CASE_ENQUIRY_ID', how='left')
        return new_df
    else:
        return df


def add_completion_time(df):
    df['COMPLETION_TIME'] = (df.CLOSED_DT - df.OPEN_DT).apply(lambda x: x / pd.np.timedelta64(1, 'h'))
    return df


def make_booleans(df):
    df['is_issue_unresolved'] = df.CLOSED_DT.isnull()
    df['SubmittedPhoto'] = df['SubmittedPhoto'].notnull()    
    return df


def fill_nas(df):
    df.Property_Type = df.Property_Type.fillna('other')    
    return df


def adding_is_description(df):
    df['is_description'] = df.description.notnull()
    return df


def add_queue_for_past_wk(df):
    df_queue = pd.read_csv('../data/feat_queue_wk.csv')
    df1 = df.merge(df_queue, on='case_enquiry_id', how='left')
    return df1


def add_my_neighborhoods(df):
    df['neighborhood_from_zip'] = df.zipcode.map(zipcode_mapping)
    return df


def main(input_path):
    df = pd.read_pickle(input_path)

    for fn in tqdm([convert_datetime, add_descriptions, add_completion_time, \
        make_booleans, fill_nas, add_census_tract, add_queue_for_past_wk, \
        add_census_data, adding_is_description, add_my_zipcodes, add_my_neighborhoods, transform_census_variables]):
        df = fn(df)

    return df


if __name__ == '__main__':
    input_path = '../data/data_w_descs.pkl'
    df = main(input_path)
    # df.to_hdf('../data/data_from_add_to_dataset.h5', key='data_from_add_to_dataset')
    df.to_pickle('../data/data_from_add_to_dataset.pkl')    
