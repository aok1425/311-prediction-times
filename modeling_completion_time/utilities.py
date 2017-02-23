import pandas as pd

from sklearn.cross_validation import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LinearRegression, LassoCV
from sklearn.cross_validation import ShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import string
from StringIO import StringIO

import statsmodels.api as sm
import statsmodels.formula.api as smf


def make_score(df_results):
    # soooo hacky
    # for backward stepwise selection
    aa = df_results['P>|t|']
    num_less_than_5 = (aa <= 0.05).sum() # assigning 3 pts to them
    num_less_than_10 = (aa <= 0.1).sum() # assigning one point to ea
    score_for_rest = (1 - aa[aa > 0.1]).sum() # 1 - pvalue points for ea
    
    ans = score_for_rest + (num_less_than_10 - num_less_than_5) + num_less_than_5 * 3
    return ans


def remove_one_feature(addtl_cols_to_drop, df_dummified, cols_to_drop):
    assert type(addtl_cols_to_drop) == list
    
    X_train, X_test, y_train, y_test = train_test_split(
        df_dummified.drop(['COMPLETION_HOURS_LOG_10'] + cols_to_drop + addtl_cols_to_drop, axis=1), 
        df_dummified.COMPLETION_HOURS_LOG_10, 
        test_size=0.2, 
        random_state=300
    )

    col_list = ' + '.join(df_dummified.drop(['COMPLETION_HOURS_LOG_10'] + cols_to_drop + addtl_cols_to_drop, axis=1))

    est = smf.ols(
        'COMPLETION_HOURS_LOG_10 ~ {}'.format(col_list), 
        pd.concat([X_train, y_train], axis=1)).fit()

    df_results = pd.read_csv(StringIO(est.summary().tables[1].as_csv()), index_col=0).reset_index()
    df_results.columns = ['coef_name'] + [i.rstrip().lstrip() for i in df_results.columns][1:]

    return make_score(df_results)


def scale(df, y='COMPLETION_HOURS_LOG_10', cols_to_avoid=[]):
    assert y not in df.columns


    # df_dummified.dtypes[df_dummified.dtypes == bool].index

    s = StandardScaler()
    df_new = pd.DataFrame(s.fit_transform(df.drop(cols_to_avoid, axis=1)))
    df_newa = df[cols_to_avoid]
    df_newa.reset_index(drop=True, inplace=True)

    df_new1 = pd.concat([df_new, df_newa], axis=1)
    df_new1.columns = [i for i in df.columns if i != y]
    return df_new1.as_matrix()