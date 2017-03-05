# This needs to be manually synced w its true location in ../preprocessing. Argh.
import pandas as pd

BLOCK_GROUP_BLACKLIST = ["9807001", "9818001", "0303003", "0701018", "9811003"] # these are parks or South Station
OUTLIERS_COMMERCIAL_INDUSTRIAL = ['0102034', '0107013', '0512001', '0612002', '0701012', '1101033', '9812021']
OUTLIERS_LOW_POP = ['0005024', '0008032', '0103002', '0104051']
OUTLIERS_POP_0 = [u'9811002', u'9815011', u'9810001', u'9811001', u'9816001', u'9817001', u'9812011', u'9815021']


def transform_dataset():
	crazy_text = "If you are seeing this now it means that you are getting the Census dict to feed to the API endpoint not \
		from the JSON file, but you are re-creating it yourself. Well, this fn was supposed to come from the main repo \
		that's on GitHub, and which Heroku doesn't have access to. I guess you could copy it out of there. Good luck."

	# original code on top of models.py
	# import os, sys
	# sys.path.append(os.path.join(os.path.dirname('.'), "../preprocessing"))
	# from transform_for_num_issues_pred import add_population, BLOCK_GROUP_BLACKLIST, OUTLIERS_COMMERCIAL_INDUSTRIAL, OUTLIERS_LOW_POP, OUTLIERS_POP_0
	# from transform_for_num_issues_pred import main as transform_dataset		
	raise Exception(crazy_text)

# This some real hacky stuff here
# supposed to be imported from ../preprocessing/transform_for_q1_civic_participation.py
def add_population(df, just_dict=False):
    # will use race_total as proxy for pop for Census block group
    # just_dict is for making the API endpoint
    df_pop = pd.read_csv('static/ACS_15_5YR_B03002_with_ann.csv', header=1)
    df_pop.insert(0, 'tract_and_block_group', df_pop['Id2'].apply(lambda id_: str(id_)[-7:]))
    df_pop = df_pop[['tract_and_block_group', 'Estimate; Total:']]
    df_pop = df_pop.rename(index=str, columns={'Estimate; Total:': 'population_total'})
    
    if just_dict:
        ans = df_pop.set_index('tract_and_block_group')['population_total'].to_dict()
        return ans

    new_df = pd.merge(df, df_pop, on='tract_and_block_group', how='left')

    return new_df	