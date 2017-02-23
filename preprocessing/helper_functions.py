from __future__ import division
import pandas as pd
from sklearn.metrics import r2_score
from IPython.display import Image
from sklearn.tree import export_graphviz
import subprocess
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm


def dummify_cols_and_baselines(df, cols, chosen_col_i=1):
    baseline_cols = []
    
    for i, column in enumerate(cols):
        baseline = sorted(df[column].unique())[-chosen_col_i]
        print baseline, 'is baseline', i, len(cols)
        baseline_cols += [baseline]
        dummy = pd.get_dummies(df[column]).rename(columns=lambda x: column+'_'+str(x)).iloc[:,0:len(df[column].unique()) - chosen_col_i]
        df = df.drop(column, axis=1) #Why not inplace? because if we do inplace, it will affect the df directly
        df = pd.concat([df, dummy], axis=1)
        
    return df, baseline_cols


def make_alphas(start, stop):
    ans = []
    lst = pd.np.logspace(start, stop, pd.np.abs(stop - start) + 1)
    for num in lst:
        ans.append(num)
        ans.append(num * 3)

    return [[i] for i in ans[:-1]]


def replace(group, stds):
    # http://stackoverflow.com/questions/29740216/remove-outliers-3-std-and-replace-with-np-nan-in-python-pandas
    group[pd.np.abs(group - group.median()) > stds * group.std()] = pd.np.nan
    return group


def remove_outliers_by_type(df, y_col, std_devs=3):
    group_column = 'TYPE'
    df = df.copy()
    df.loc[:, y_col] = df[[y_col, 'TYPE']].groupby(group_column).transform(lambda g: replace(g, std_devs))
    return df.dropna(subset=[y_col])


def adjusted_r2(y_true, y_pred, num_features):
    r2 = r2_score(y_true, y_pred)
    r2_q = 1 - r2
    aa = num_features / (y_true.shape[0] - num_features - 1)
    return r2 - r2_q * aa


# TODO: add this to add_to_dataset.py
def transform_school(df):
    """Make it numeric instead of categorical, as there is some ordinal meaning"""
    df.school = df.school.str.extract(r'(\d\d?)').astype(int)
    return df


def choose_race_mode(df):
    # didn't use bc didn't chg R2, and less interpretable/
    # I want my webapp to show a mix of options, not just mode
    cols_race = [i for i in df.columns if 'race' in i]
    df['race_most_common'] = df[cols_race].idxmax(axis=1)
    ans = df.drop(cols_race, axis=1)
    return ans


def need_more_alphas(result_table):
    """Make sure we don't need to look at more alphas,
    by checking that min and max alphas don't correspond to the highest score."""
    scores = result_table.loc['mean_test_score'].tolist()
    highest_score = max(scores)
    
    if scores[0] == highest_score:
        return True
    elif scores[-1] == highest_score:
        if scores[-1] == scores[-2]:
            return False
        else:
            return True
    else:
        return False    


def visualize_tree(tree, feature_names):
    """Create tree png using graphviz.

    Args
    ----
    tree -- scikit-learn DecsisionTree.
    feature_names -- list of feature names.
    """
    with open("dt.dot", 'w') as f:
        export_graphviz(tree, out_file=f, feature_names=feature_names)

    command = ["dot", "-Tpng", "dt.dot", "-o", "dt.png"]
    subprocess.check_call(command)
        
    return Image('dt.png')


def get_vif(exog, exog_label_or_idx):
    """Now works w DataFrames, and adds the intercept column."""
    assert type(exog) == pd.DataFrame
    assert type(exog_label_or_idx) in (str, int)
    
    if type(exog_label_or_idx) == str:
        exog_idx = list(exog.columns).index(exog_label_or_idx)
    else:
        exog_idx = exog_label_or_idx
    
    exog_w_intercept = sm.add_constant(exog.as_matrix(), prepend=False)
    return variance_inflation_factor(exog_w_intercept, exog_idx)


def get_vifs(df, response):
    """Input the df and response column, and get the variance inflation factors for each of the predictors."""
    answer = {}
    cols = [i for i in df.columns if i != response]
    
    for col in cols:
        answer[col] = get_vif(df.drop(response, axis=1), col)
    
    return pd.Series(answer).sort_values(ascending=False)    