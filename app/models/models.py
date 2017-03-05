from __future__ import division
from sklearn.externals import joblib
import pandas as pd
from collections import defaultdict
import json
from utilities import add_population, transform_dataset
import math
from sample_row import sample_row, col_order
from subprocess import Popen

import os, sys
sys.path.append(os.path.join(os.path.dirname('.'), "../"))
from outliers import outliers


# CATEGORY_GROUPS_IN_QUESTION = {
#   'Animal Control': ['Pick up Dead Animal'],
#   'Abandoned Vehicles': ['Abandoned Vehicles', 'Abandoned Bicycle'],
#   'Rodent Removal': ['Rodent Activity', 'Bed Bugs', 'Mice Infestation - Residential'],
#   'Living Conditions': ['Unsatisfactory Living Conditions', 'Poor Conditions of Property', 'Unsanitary Conditions - Establishment', 'Illegal Occupancy', 'Heat - ,Excessive  Insufficient'],
#   'Graffiti Removal': ['Graffiti Removal']
# }


def get_model():
  return None
  file = 'static/q2_rf_model.pkl'
  if os.path.isfile(file):
    return joblib.load(file)
  else:
    Popen(['wget', 'https://s3.amazonaws.com/aok1425/q2_rf_model.pkl', 'static/'])
    return joblib.load(file)
 

def get_preds_for_all_trees(model, X_test_row):
    """So that I can get a quasi-prediction interval from them."""
    # assert type(model) == GridSearchCV
    assert X_test_row.shape[0] == 1
    
    trees = model.best_estimator_.steps[-1][-1].estimators_
    preds = []
    
    for tree in trees:
        pred = tree.predict(X_test_row)
        preds.append(pred)
        
    return pd.np.array(preds)


def make_pred(request_form_dict, model):
  row = sample_row.copy()
  d = dict(request_form_dict)

  for k,v in d.items():
    v = v[0]
    if k == 'source':
      row['Source_' + v] = 1
    elif k == 'issue':
      row['TYPE_' + v] = 1
    elif k == 'neighborhood':
      row['neighborhood_from_zip_' + v] = 1

  print [ij for ij in row.items() if ij[1] == 1]
  aa = sum(row.values())
  print aa

  if aa == 0:
    return 'sthwrong'

  # row = sample_row
  pred = model.predict(pd.DataFrame([row])[col_order])[0]
  print pred
  return pred


def index_to_dict(lst):
    d = {}
    
    for e in lst:
        d[e['TYPE']] = e['num_issues']
        
    return d


def store_in_dict(df_mini, d):
    """Helper for make_top_n_dict"""
    years =  df_mini.year.drop_duplicates()
    assert years.shape[0] == 1
    year = years.iloc[0]
    
    block_groups = df_mini.tract_and_block_group.drop_duplicates()
    assert block_groups.shape[0] == 1
    block_group = block_groups.iloc[0]
    
    d_ans = index_to_dict(df_mini.set_index(['year', 'tract_and_block_group']).to_dict('records'))
    d[block_group][year] = d_ans


def store_in_dict_for_all_yrs(df_mini, d):
    """Helper for make_top_n_dict"""
    block_groups = df_mini.tract_and_block_group.drop_duplicates()
    assert block_groups.shape[0] == 1
    block_group = block_groups.iloc[0]
    
    d_ans = index_to_dict(df_mini.set_index(['tract_and_block_group']).to_dict('records'))
    d[block_group] = d_ans


def make_top_n_dict_for_all_yrs(df, n=5):
  # TODO: this shld be the same as transform_for_num_issues_pred.main()
  # make a single source of truth
  """
  For map, returns top 5 categs by year by loc

  Returns:
  {tract: {top 5 categs and their nums}},
  {tract: total nums for _all_ categs}
  """
  df['num_issues'] = 1

  ## starting the groupbys
  aa = df[['tract_and_block_group', 'TYPE', 'num_issues']].sort_values(['tract_and_block_group'])

  # http://stackoverflow.com/questions/27842613/pandas-groupby-sort-within-groups
  df_agg = aa.groupby(['tract_and_block_group', 'TYPE']).count()
  g = df_agg['num_issues'].groupby(level=0, group_keys=False)
  ans = g.nlargest(n)    

  cc = ans.reset_index().sort_values(['tract_and_block_group'], ascending=[False])

  ## putting into dict
  d = defaultdict(defaultdict) # 2 levels
  cc.groupby(['tract_and_block_group']).apply(lambda df_mini: store_in_dict_for_all_yrs(df_mini, d))

  ## dict for total nums
  d_totals = df_agg.groupby(level=0).sum().to_dict()['num_issues']

  ans = {
    'top_n_all_yrs': d,
    'top_n_all_yrs_totals': d_totals
  }

  return ans


def make_top_n_dict(df, n=5):
  """For map, returns top 5 categs by year by loc"""
  df['year'] = df.OPEN_DT.map(lambda x: x.year)
  df.drop('OPEN_DT', inplace=True, axis=1)
  df['num_issues'] = 1

  ## starting the groupbys
  aa = df[['year', 'tract_and_block_group', 'TYPE', 'num_issues']].sort_values(['year', 'tract_and_block_group'])

  # http://stackoverflow.com/questions/27842613/pandas-groupby-sort-within-groups
  df_agg = aa.groupby(['year', 'tract_and_block_group', 'TYPE']).count()
  g = df_agg['num_issues'].groupby(level=[0,1], group_keys=False)
  ans = g.nlargest(n)    

  cc = ans.reset_index().sort_values(['year', 'tract_and_block_group'], ascending=[False, False])

  ## putting into dict
  d = defaultdict(defaultdict) # 2 levels
  cc.groupby(['year', 'tract_and_block_group']).apply(lambda df_mini: store_in_dict(df_mini, d))

  ## dict for total_nums
  d_totals = df_agg.groupby(level=[1,0]).sum().to_dict()['num_issues']
  totals_by_year = defaultdict(defaultdict)

  for k in d_totals:
      tract_and_block_group = k[0]
      year = k[1]
      
      totals_by_year[tract_and_block_group][year] = d_totals[k]

  ans = {
    'top_n_by_yr': d,
    'top_n_by_yr_totals': totals_by_year
  }

  return ans


def incorporate_totals_into_orig_dict(d, d_totals_by_yr):
  for k in d_totals_by_yr['top_n_all_yrs']:
    d['top_n_by_yr'][k]['all_years'] = d_totals_by_yr['top_n_all_yrs'][k]

  d_totals_by_yr.pop('top_n_all_yrs')
  d.update(d_totals_by_yr)
  assert len(d.keys()) == 3

  return d


def make_q1_json():
  df_orig = pd.read_pickle('../data/data_from_remove_from_dataset.pkl')
  df = df_orig[['OPEN_DT', 'TYPE', 'tract_and_block_group']]
  d = make_top_n_dict(df)
  d2 = make_top_n_dict_for_all_yrs(df)
  d3 = incorporate_totals_into_orig_dict(d, d2)

  with open('static/top_5_types_by_yr_loc.json', 'w') as data_file:    
    json.dump(d3, data_file, ensure_ascii=False)  


# # TODO: make this feed directly into make_q1_json()
def make_q1_json(*args, **kwargs):
  with open('static/top_5_types_by_yr_loc.json') as data_file:    
    data = json.load(data_file)

  return data


# TODO: fix the names of the below; maybe put into class or module

def make_total_issues_by_year(issues_by_year):
    total_issues_by_year = {}

    for k,v in issues_by_year.iteritems():
        total_issues_by_year['total_issues_{}'.format(k)] = v

    return total_issues_by_year


def transform_issues_by_year_per_1000(d, population_dict, tract_and_block_group):
    new_d = defaultdict(defaultdict)

    for year in d:
      for issue_k, issue_v in d[year].iteritems():
        try:
          new_value = int(round(issue_v / population_dict[tract_and_block_group] * 1000))
        except OverflowError:
          new_value = None

        new_d[year][issue_k] = new_value

    return new_d


def add_geojson(top_dict, population_dict, census_dict, completion_time_means_dict, completion_time_stds_dict):
    """Returns dict, not JSON"""
    with open("static/boston_census_block_groups.geojson") as data_file:    
        geojson = json.load(data_file)    
        
    new_features = []

    for feature in geojson['features']:
        id_ = feature['properties']['tract_and_block_group']

        if id_ in top_dict['top_n_by_yr'] and id_ not in outliers:
            # original stuff
            feature['properties']['issues_by_year'] = top_dict['top_n_by_yr'][id_]
            feature['properties'].update(make_total_issues_by_year(top_dict['top_n_by_yr_totals'][id_]))            
            feature['properties']['total_issues_all_years'] = top_dict['top_n_all_yrs_totals'][id_]

            feature['properties']['issues_by_year_per_1000'] = transform_issues_by_year_per_1000(
                feature['properties']['issues_by_year'],
                population_dict,
                id_
            )

            # per capita stuff and adding population
            feature['properties']['pop'] = population_dict[id_]

            for col in [col for col in feature['properties'] if 'total_issues_' in col]:
              try:
                new_value = int(round(feature['properties'][col] / population_dict[id_] * 1000))
              except OverflowError:
                new_value = None              
              feature['properties'][col + '_per_1000'] = new_value

            # adding census vars
            for census_var in census_dict:
              if id_ in census_dict[census_var]:
                feature['properties'][census_var] = census_dict[census_var][id_]

            # adding q2 means and std devs
            if id_ in completion_time_means_dict:
              for k,v in completion_time_means_dict[id_].items():
                feature['properties']['completion_time_mean_' + k] = v

            if id_ in completion_time_stds_dict:
              for k,v in completion_time_stds_dict[id_].items():
                if math.isnan(v):
                  v = 0
                feature['properties']['completion_time_std_' + k] = v


            new_features.append(feature)
            
    geojson['features'] = new_features
    
    return geojson


def make_census_vars_dict(chosen_cols=['income']):
  """
  Returns (example):
  {'bedroom': {'0511011': 2, '1004002': 3},
   'income': {'0511011': 112500, '1004002': 112500}}  
  """
  df_orig = pd.read_pickle('../data/data_from_remove_from_dataset.pkl')  
  df_transformed = transform_dataset(df_orig)
  # chosen_cols = ['race_white', 'race_black', 'race_asian', 'race_hispanic', 'race_other', 'poverty_pop_below_poverty_level', 'earned_income_per_capita', 'poverty_pop_w_public_assistance', 'poverty_pop_w_food_stamps', 'poverty_pop_w_ssi', 'school', 'school_std_dev', 'housing', 'housing_std_dev', 'bedroom', 'bedroom_std_dev', 'value', 'value_std_dev', 'rent', 'rent_std_dev', 'income', 'income_std_dev', 'Source', 'Property_Type']
  ans = df_transformed[chosen_cols + ['tract_and_block_group']].set_index('tract_and_block_group').to_dict()

  with open('static/census_data.json', 'w') as data_file:    
    json.dump(ans, data_file, ensure_ascii=False) 

  return ans


# TODO: make this feed directly into the one above
def make_census_vars_dict(*args, **kwargs):
  with open('static/census_data.json') as data_file:    
    data = json.load(data_file)

  return data


def make_dict1():
  with open('static/q2_means.json') as data_file:    
    data = json.load(data_file)

  return data  


def make_dict2():
  with open('static/q2_std.json') as data_file:    
    data = json.load(data_file)

  return data  


def make_q1_map_json():
    d1 = make_q1_json()
    population_dict = add_population(df=None, just_dict=True)
    census_dict = make_census_vars_dict()
    completion_time_means_dict = make_dict1()
    completion_time_stds_dict = make_dict2()
    d2 = add_geojson(d1, population_dict, census_dict, completion_time_means_dict, completion_time_stds_dict)
    return d2


if __name__ == '__main__':
  model = get_model()
  print make_pred(sample_row, model)