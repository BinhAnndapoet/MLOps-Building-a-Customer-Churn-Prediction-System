import pandas as pd
import numpy as np

df = pd.read_csv('customer_churn_dataset-training-master.csv')

indices = np.array_split(df.index, 10)
splits = [df.loc[idx] for idx in indices]

for i, split_df in enumerate(splits, 1):
    split_df.to_csv(f'train_period_{i}.csv', index=False)