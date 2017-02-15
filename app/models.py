from sklearn.externals import joblib
import pandas as pd
from collections import defaultdict
import json


sample_row = {'Source_Citizens Connect App': 1,
  'Source_Self Service': 0,
  'TYPE_Abandoned Bicycle': 0,
  'TYPE_Abandoned Building': 0,
  'TYPE_Abandoned Vehicles': 0,
  'TYPE_Animal Found': 0,
  'TYPE_Animal Generic Request': 0,
  'TYPE_Animal Lost': 0,
  'TYPE_Bed Bugs': 0,
  'TYPE_Bicycle Issues': 0,
  'TYPE_Breathe Easy': 0,
  'TYPE_Building Inspection Request': 0,
  'TYPE_Call Log': 0,
  'TYPE_Carbon Monoxide': 0,
  'TYPE_Catchbasin': 0,
  'TYPE_Checkin': 0,
  'TYPE_Chronic Dampness/Mold': 0,
  'TYPE_Construction Debris': 0,
  'TYPE_Contractors Complaint': 0,
  'TYPE_Cross Metering - Sub-Metering': 0,
  'TYPE_Egress': 0,
  'TYPE_Electrical': 0,
  'TYPE_Empty Litter Basket': 0,
  'TYPE_Equipment Repair': 0,
  'TYPE_Exceeding Terms of Permit': 0,
  'TYPE_General Comments For An Employee': 0,
  'TYPE_General Comments For a Program or Policy': 0,
  'TYPE_General Lighting Request': 0,
  'TYPE_Graffiti Removal': 0,
  'TYPE_Heat - Excessive  Insufficient': 0,
  'TYPE_Highway Maintenance': 0,
  'TYPE_Housing Discrimination Intake Form': 0,
  'TYPE_Illegal Auto Body Shop': 0,
  'TYPE_Illegal Dumping': 0,
  'TYPE_Illegal Occupancy': 0,
  'TYPE_Illegal Posting of Signs': 0,
  'TYPE_Illegal Rooming House': 0,
  'TYPE_Illegal Use': 0,
  'TYPE_Illegal Vending': 0,
  'TYPE_Improper Storage of Trash (Barrels)': 0,
  'TYPE_Install New Lighting': 0,
  'TYPE_Item Price Missing': 0,
  'TYPE_Lead': 0,
  'TYPE_Litter Basket Maintenance': 0,
  'TYPE_Maintenance - Homeowner': 0,
  'TYPE_Maintenance Complaint - Residential': 0,
  'TYPE_Major System Failure': 0,
  'TYPE_Mice Infestation - Residential': 0,
  'TYPE_Missed Trash/Recycling/Yard Waste/Bulk Item': 0,
  'TYPE_Missing Sign': 0,
  'TYPE_Needle Pickup': 0,
  'TYPE_New Sign  Crosswalk or Pavement Marking': 0,
  'TYPE_New Tree Requests': 0,
  'TYPE_No Price on Gas/Wrong Price': 0,
  'TYPE_No-Tow Complaint Confirmation': 0,
  'TYPE_Notification': 0,
  'TYPE_OCR Front Desk Interactions': 0,
  'TYPE_Overcrowding': 0,
  'TYPE_Overflowing or Un-kept Dumpster': 0,
  'TYPE_Park Improvement Requests': 0,
  'TYPE_Park Maintenance Requests': 0,
  'TYPE_Parking Enforcement': 0,
  'TYPE_Parking on Front/Back Yards (Illegal Parking)': 0,
  'TYPE_Parks Lighting/Electrical Issues': 0,
  'TYPE_Pavement Marking Maintenance': 0,
  'TYPE_Pest Infestation - Residential': 0,
  'TYPE_Pick up Dead Animal': 0,
  'TYPE_Pigeon Infestation': 0,
  'TYPE_Plumbing': 0,
  'TYPE_Poor Conditions of Property': 0,
  'TYPE_Product Short Measure': 0,
  'TYPE_Protection of Adjoining Property': 0,
  'TYPE_Public Works General Request': 0,
  'TYPE_Recycling Cart Inquiry': 0,
  'TYPE_Recycling Cart Return': 0,
  'TYPE_Request for Pothole Repair': 0,
  'TYPE_Request for Recycling Cart': 0,
  'TYPE_Request for Snow Plowing': 1,
  'TYPE_Request for Snow Plowing (Emergency Responder)': 0,
  'TYPE_Requests for Street Cleaning': 0,
  'TYPE_Requests for Traffic Signal Studies or Reviews': 0,
  'TYPE_Roadway Repair': 0,
  'TYPE_Rodent Activity': 0,
  'TYPE_Scale Not Visible': 0,
  'TYPE_Scanning Overcharge': 0,
  'TYPE_Schedule a Bulk Item Pickup': 0,
  'TYPE_Short Measure - Gas': 0,
  'TYPE_Sidewalk Repair': 0,
  'TYPE_Sign Repair': 0,
  'TYPE_Space Savers': 0,
  'TYPE_Squalid Living Conditions': 0,
  'TYPE_Sticker Request': 0,
  'TYPE_Street Light Knock Downs': 0,
  'TYPE_Street Light Outages': 0,
  'TYPE_Student Move-in Issues': 0,
  'TYPE_Traffic Signal Inspection': 0,
  'TYPE_Traffic Signal Repair': 0,
  'TYPE_Transportation General Request': 0,
  'TYPE_Trash on Vacant Lot': 0,
  'TYPE_Tree Emergencies': 0,
  'TYPE_Tree Maintenance Requests': 0,
  'TYPE_Tree in Park': 0,
  'TYPE_Unsafe Dangerous Conditions': 0,
  'TYPE_Unsatisfactory Living Conditions': 0,
  'TYPE_Unsatisfactory Utilities - Electrical  Plumbing': 0,
  'TYPE_Unshoveled Sidewalk': 0,
  'TYPE_Upgrade Existing Lighting': 0,
  'TYPE_Utility Call-In': 0,
  'TYPE_WC Call Log': 0,
  'TYPE_Water in Gas - High Priority': 0,
  'TYPE_Work w/out Permit': 0,
  'TYPE_Working Beyond Hours': 0,
  'neighborhood_from_zip_East Boston': 0,
  'neighborhood_from_zip_North End': 0,
  'queue_wk_open': 1}


def get_model():
  return joblib.load('../data/model_completion_time.pkl')


def get_model():
  return joblib.load('model_completion_time.pkl')  


def make_pred(request_form_dict, model):
  row = {'Source_Citizens Connect App': 0,
    'Source_Self Service': 0,
    'TYPE_Abandoned Bicycle': 0,
    'TYPE_Abandoned Building': 0,
    'TYPE_Abandoned Vehicles': 0,
    'TYPE_Animal Found': 0,
    'TYPE_Animal Generic Request': 0,
    'TYPE_Animal Lost': 0,
    'TYPE_Bed Bugs': 0,
    'TYPE_Bicycle Issues': 0,
    'TYPE_Breathe Easy': 0,
    'TYPE_Building Inspection Request': 0,
    'TYPE_Call Log': 0,
    'TYPE_Carbon Monoxide': 0,
    'TYPE_Catchbasin': 0,
    'TYPE_Checkin': 0,
    'TYPE_Chronic Dampness/Mold': 0,
    'TYPE_Construction Debris': 0,
    'TYPE_Contractors Complaint': 0,
    'TYPE_Cross Metering - Sub-Metering': 0,
    'TYPE_Egress': 0,
    'TYPE_Electrical': 0,
    'TYPE_Empty Litter Basket': 0,
    'TYPE_Equipment Repair': 0,
    'TYPE_Exceeding Terms of Permit': 0,
    'TYPE_General Comments For An Employee': 0,
    'TYPE_General Comments For a Program or Policy': 0,
    'TYPE_General Lighting Request': 0,
    'TYPE_Graffiti Removal': 0,
    'TYPE_Heat - Excessive  Insufficient': 0,
    'TYPE_Highway Maintenance': 0,
    'TYPE_Housing Discrimination Intake Form': 0,
    'TYPE_Illegal Auto Body Shop': 0,
    'TYPE_Illegal Dumping': 0,
    'TYPE_Illegal Occupancy': 0,
    'TYPE_Illegal Posting of Signs': 0,
    'TYPE_Illegal Rooming House': 0,
    'TYPE_Illegal Use': 0,
    'TYPE_Illegal Vending': 0,
    'TYPE_Improper Storage of Trash (Barrels)': 0,
    'TYPE_Install New Lighting': 0,
    'TYPE_Item Price Missing': 0,
    'TYPE_Lead': 0,
    'TYPE_Litter Basket Maintenance': 0,
    'TYPE_Maintenance - Homeowner': 0,
    'TYPE_Maintenance Complaint - Residential': 0,
    'TYPE_Major System Failure': 0,
    'TYPE_Mice Infestation - Residential': 0,
    'TYPE_Missed Trash/Recycling/Yard Waste/Bulk Item': 0,
    'TYPE_Missing Sign': 0,
    'TYPE_Needle Pickup': 0,
    'TYPE_New Sign  Crosswalk or Pavement Marking': 0,
    'TYPE_New Tree Requests': 0,
    'TYPE_No Price on Gas/Wrong Price': 0,
    'TYPE_No-Tow Complaint Confirmation': 0,
    'TYPE_Notification': 0,
    'TYPE_OCR Front Desk Interactions': 0,
    'TYPE_Overcrowding': 0,
    'TYPE_Overflowing or Un-kept Dumpster': 0,
    'TYPE_Park Improvement Requests': 0,
    'TYPE_Park Maintenance Requests': 0,
    'TYPE_Parking Enforcement': 0,
    'TYPE_Parking on Front/Back Yards (Illegal Parking)': 0,
    'TYPE_Parks Lighting/Electrical Issues': 0,
    'TYPE_Pavement Marking Maintenance': 0,
    'TYPE_Pest Infestation - Residential': 0,
    'TYPE_Pick up Dead Animal': 0,
    'TYPE_Pigeon Infestation': 0,
    'TYPE_Plumbing': 0,
    'TYPE_Poor Conditions of Property': 0,
    'TYPE_Product Short Measure': 0,
    'TYPE_Protection of Adjoining Property': 0,
    'TYPE_Public Works General Request': 0,
    'TYPE_Recycling Cart Inquiry': 0,
    'TYPE_Recycling Cart Return': 0,
    'TYPE_Request for Pothole Repair': 0,
    'TYPE_Request for Recycling Cart': 0,
    'TYPE_Request for Snow Plowing': 0,
    'TYPE_Request for Snow Plowing (Emergency Responder)': 0,
    'TYPE_Requests for Street Cleaning': 0,
    'TYPE_Requests for Traffic Signal Studies or Reviews': 0,
    'TYPE_Roadway Repair': 0,
    'TYPE_Rodent Activity': 0,
    'TYPE_Scale Not Visible': 0,
    'TYPE_Scanning Overcharge': 0,
    'TYPE_Schedule a Bulk Item Pickup': 0,
    'TYPE_Short Measure - Gas': 0,
    'TYPE_Sidewalk Repair': 0,
    'TYPE_Sign Repair': 0,
    'TYPE_Space Savers': 0,
    'TYPE_Squalid Living Conditions': 0,
    'TYPE_Sticker Request': 0,
    'TYPE_Street Light Knock Downs': 0,
    'TYPE_Street Light Outages': 0,
    'TYPE_Student Move-in Issues': 0,
    'TYPE_Traffic Signal Inspection': 0,
    'TYPE_Traffic Signal Repair': 0,
    'TYPE_Transportation General Request': 0,
    'TYPE_Trash on Vacant Lot': 0,
    'TYPE_Tree Emergencies': 0,
    'TYPE_Tree Maintenance Requests': 0,
    'TYPE_Tree in Park': 0,
    'TYPE_Unsafe Dangerous Conditions': 0,
    'TYPE_Unsatisfactory Living Conditions': 0,
    'TYPE_Unsatisfactory Utilities - Electrical  Plumbing': 0,
    'TYPE_Unshoveled Sidewalk': 0,
    'TYPE_Upgrade Existing Lighting': 0,
    'TYPE_Utility Call-In': 0,
    'TYPE_WC Call Log': 0,
    'TYPE_Water in Gas - High Priority': 0,
    'TYPE_Work w/out Permit': 0,
    'TYPE_Working Beyond Hours': 0,
    'neighborhood_from_zip_East Boston': 0,
    'neighborhood_from_zip_North End': 0,
    'queue_wk_open': 0}

  d = dict(request_form_dict)

  for k,v in d.items():
    v = v[0]
    if k == 'source':
      v = 'Source_' + v
    elif k == 'issue':
      v = 'TYPE_' + v
    elif k == 'neighborhood':
      v = 'neighborhood_from_zip_' + v

    if v in row:
      row[v] = 1

  # row = sample_row
  pred = model.predict(pd.DataFrame([row]))[0]
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


def make_top_n_dict(n=5):
  """For map, returns top 5 categs by year by loc"""
  df = pd.read_pickle('../data/data_from_remove_from_dataset.pkl')[['OPEN_DT', 'TYPE', 'tract_and_block_group']]
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
  return d


# TODO: uncomment the below
def make_top_n_dict(*args, **kwargs):
  with open('static/top_5_types_by_yr_loc.json') as data_file:    
    data = json.load(data_file)

  return data


if __name__ == '__main__':
  model = get_model()
  print make_pred(sample_row, model)