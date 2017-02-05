import pandas as pd

def dummify_cols_and_baselines(df, cols):
    baseline_cols = []
    
    for i, column in enumerate(cols):
        baseline = sorted(df[column].unique())[-1]
        print baseline, 'is baseline', i, len(cols)
        baseline_cols += [baseline]
        dummy = pd.get_dummies(df[column]).rename(columns=lambda x: column+'_'+str(x)).iloc[:,0:len(df[column].unique())-1]
        df = df.drop(column, axis=1) #Why not inplace? because if we do inplace, it will affect the df directly
        df = pd.concat([df, dummy], axis=1)
        
    return df, baseline_cols


def make_alphas(start, stop):
	lst = pd.np.logspace(start, stop, pd.np.abs(stop - start) + 1)
	return [[i] for i in lst]


def replace(group, stds):
    # http://stackoverflow.com/questions/29740216/remove-outliers-3-std-and-replace-with-np-nan-in-python-pandas
    group[pd.np.abs(group - group.median()) > stds * group.std()] = pd.np.nan
    return group


def remove_outliers_by_type(df, y_col, std_devs=3):
    group_column = 'TYPE'
    df = df.copy()
    df.loc[:, y_col] = df[[y_col, 'TYPE']].groupby(group_column).transform(lambda g: replace(g, std_devs))
    return df.dropna(subset=[y_col])