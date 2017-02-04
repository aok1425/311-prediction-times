from preprocessing.add_to_dataset import main as add_to_dataset
from cleaning.remove_from_dataset import main as remove_from_dataset

df = add_to_dataset('data/data_w_descs.pkl')
df.to_pickle('data/data_from_add_to_dataset.pkl')

df1 = main('data/data_from_add_to_dataset.pkl')
df1.to_pickle('data/data_from_remove_from_dataset.pkl') 