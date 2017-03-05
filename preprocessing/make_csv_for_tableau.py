import pandas as pd
import os, sys
sys.path.append(os.path.join(os.path.dirname('.'), "../preprocessing"))
from transform_for_q1_civic_participation import main as transform_dataset, group_table, removing_cols

df_orig = pd.read_pickle('../data/data_from_remove_from_dataset.pkl')
df = transform_dataset(df_orig)
df.to_csv('../data/data_for_tableau.csv', index=False, encoding='utf-8')