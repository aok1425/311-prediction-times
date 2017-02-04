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
    row['zipcode'] = d[(row['LATITUDE'], row['LONGITUDE'])]
    return row


def add_my_zip_codes(df):
    mapping = make_mapping_dict(df)
    df['zipcode'] = df.apply(lambda row: get_zipcode(row, mapping))
    df.zipcode = df.zipcode.fillna(df.LOCATION_ZIPCODE)
    return df