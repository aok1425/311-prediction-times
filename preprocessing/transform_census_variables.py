from __future__ import division
import pandas as pd
from datetime import datetime
import re


class CensusVariablesTransformer(object):
    def __init__(self, df):
        self.df = df


    def get_bedroom(self, txt):
        if txt[-1] == '+':
            return 6 # I chose this arbitrarily over 5
        else:
            return int(txt[-1])


    def get_rent(self, txt):
        if txt[-1] == '+':
            return 3750
        else:
            regex = re.compile(r'rent_(\d+)_(\d+)')
            match = regex.search(txt)
            low, high = [int(i) for i in match.groups()]
            return int((high + low) / 2) + 1


    def get_income(self, txt):
        if txt[-1] == '+':
            return 250000
        else:
            regex = re.compile(r'income_(\d+)_(\d+)')
            match = regex.search(txt)
            low, high = [int(i) for i in match.groups()]
            return int((high + low) / 2) + 1        


    def get_value(self, txt):
        if txt[-1] == '+':
            return 2.5e6
        else:
            regex = re.compile(r'value_(\d+)_(\d+)')
            match = regex.search(txt)
            low, high = [int(i) for i in match.groups()]
            return int((high + low) / 2) + 1        


    def transform_categ_mode(self, df, category):
        if category in ('race', 'poverty'):
            raise Exception('not gonna transform those categs')
        
        d = {
            'bedroom': 'bedroom_total_ppl', 
            'school': 'school_total', 
            'rent': 'rent_total', 
            'income': 'income_total', 
            'value': 'value_total',
            'housing': 'housing_total'
        }
        assert category in d.keys()
        
        category_total_col = d[category]
        category_cols = [col for col in df.columns if category + '_' == col[:len(category) + 1]]
        categ_df = df[category_cols]
        categ_df_wo_total = categ_df[[col for col in categ_df.columns if col != category_total_col]]
        categ_df_wo_total_div_by_total = categ_df_wo_total.truediv(df[category_total_col], axis='rows')
        
        max_categ_df = categ_df_wo_total.idxmax(axis=1)
        new_df = df.drop(category_cols, axis=1)    
        
        if category == 'bedroom':
            new_df[category] = max_categ_df.map(lambda txt: self.get_bedroom(txt))
        elif category == 'school':
            new_df[category] = max_categ_df.map(lambda txt: txt.replace('school_', ''))
        elif category == 'rent':
            new_df[category] = max_categ_df.map(lambda txt: self.get_rent(txt))
        elif category == 'income':
            new_df[category] = max_categ_df.map(lambda txt: self.get_income(txt))
        elif category == 'value':
            new_df[category] = max_categ_df.map(lambda txt: self.get_value(txt)) 
        elif category == 'housing':
            new_df[category] = max_categ_df.map(lambda txt: txt[8:])

        new_df[category + '_std_dev'] = categ_df_wo_total_div_by_total.std(axis=1)
            
        return new_df


    def transform_poverty_race(self, df, category):
        df = df.copy()
        assert category in ('race', 'poverty')
        d = {
            'poverty': 'poverty_total_pop', 
            'race': 'race_total'
        } 
        
        total_col_name = d[category]
        new_df = df[[col for col in df.columns if category + '_' == col[:len(category) + 1]]]
        df_transformed_values = zip(*new_df.apply(
            lambda row: [row[list(new_df.columns).index(col)] / row[total_col_name] for col in new_df.columns if col != total_col_name],
            axis=1)
        )    
        
        if category == 'poverty':
            df['poverty_pop_below_poverty_level'], \
                df['poverty_pop_w_public_assistance'], \
                df['poverty_pop_w_food_stamps'], \
                df['poverty_pop_w_ssi'] = df_transformed_values
        elif category == 'race':
            df['race_white'], \
                df['race_black'], \
                df['race_asian'], \
                df['race_hispanic'], \
                df['race_other'] = df_transformed_values

        return df.drop(total_col_name, axis=1)


    def run(self):
        # TODO: look into the below dropna
        new_df = self.transform_categ_mode(self.df.dropna(subset=['housing_own']), 'school')
        # new_df = self.transform_categ_mode(self.df, 'school')

        for categ in ['housing', 'bedroom', 'value', 'rent', 'income']:
            new_df = self.transform_categ_mode(new_df, categ)

        for categ in ['race', 'poverty']:
            new_df = self.transform_poverty_race(new_df, categ)

        return new_df


def transform_census_variables(df):
    cvt = CensusVariablesTransformer(df)
    return cvt.run()
