# this takes data_w_descs.pkl and census_data_aggregated.pkl

from __future__ import division
import pandas as pd
import shapegeocode
from datetime import datetime
import re

from transform_census_variables import transform_census_variables
from adding_zipcodes import adding_zipcodes


def get_tract_block_group(lat, long_, shp_obj):
    d = gc.geocode(lat, long_)
    return d['TRACTCE'] + d['BLKGRPCE']


def add_census_tract(df):
    gc = shapegeocode.geocoder('../data/shape-files/cb_2015_25_bg_500k.shp')
    df['tract_and_block_group'] = df[['LATITUDE', 'LONGITUDE']].apply(lambda row: get_tract_block_group(row['LATITUDE'], row['LONGITUDE'], gc), axis=1)
    return df


def add_census_data(df):
    df_census = pd.read_pickle('../data/census_data_aggregated.pkl')
    df_final = df.merge(df_census, on='tract_and_block_group', how='left')
    return df


def convert_datetime(df):
    to_datetime = lambda d: datetime.strptime(d, '%m/%d/%Y %H:%M:%S %p') if type(d) != float else pd.np.NaN
    df['OPEN_DT'] = df['OPEN_DT'].apply(lambda datetime_text: to_datetime(datetime_text))
    df['CLOSED_DT'] = df['CLOSED_DT'].apply(lambda datetime_text: to_datetime(datetime_text))
    df['TARGET_DT'] = df['TARGET_DT'].apply(lambda datetime_text: to_datetime(datetime_text))
    return df


def add_descriptions(df):
    df_descs = pd.read_pickle('../data/data_w_descs.pkl')
    df_descs = df_descs[['CASE_ENQUIRY_ID', 'description']]
    new_df = pd.merge(df, df_descs, on='CASE_ENQUIRY_ID')
    return new_df


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


def main():
    df = pd.read_pickle('../data/data_w_descs.pkl')

    for fn in [add_census_tract, add_census_data, convert_datetime, add_descriptions, add_completion_time, \
        make_booleans, fill_nas, adding_is_description, transform_census_variables, adding_zipcodes]:
        df = fn(df)

    df.to_pickle('../data/data_from_add_to_dataset.pkl')


if __name__ == '__main__':
    main()