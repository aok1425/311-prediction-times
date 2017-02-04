from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, precision_score, recall_score, accuracy_score


def make_mapping_dict(df, neighbors=5):
    # train model
    X = df[df.LOCATION_ZIPCODE.notnull()][['LATITUDE', 'LONGITUDE']]
    y = df[df.LOCATION_ZIPCODE.notnull()].LOCATION_ZIPCODE
    X_desired = df[df.LOCATION_ZIPCODE.isnull()][['LATITUDE', 'LONGITUDE']]

    clf = KNeighborsClassifier(n_neighbors=neighbors)
    clf.fit(X, y)

    # make mapping
    y_desired = clf.predict(X_desired)
    X_desired['zip_imputed'] = y_desired
    mapping = X_desired.set_index(['LATITUDE', 'LONGITUDE']).to_dict()['zip_imputed']
    return mapping


def get_zipcode(row, d):
    return d[(row['LATITUDE'], row['LONGITUDE'])]


def add_my_zipcodes(df):
    d = make_mapping_dict(df)
    df['zipcode'] = df.LOCATION_ZIPCODE.copy()
    df.zipcode.ix[df.zipcode.isnull()] = df[df.zipcode.isnull()].apply(lambda row: get_zipcode(row, d), axis=1)
    return df
