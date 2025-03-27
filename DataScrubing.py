import os

import pandas as pd

stocks_folder = 'Stocks'

for file_name in os.listdir(stocks_folder):
    if file_name.endswith('.csv'):
        file_path = os.path.join(stocks_folder, file_name)

        df = pd.read_csv(file_path, skiprows=[1])
        df.to_csv(file_path, index=False, float_format='%.2f')
        print(f"Cleaned {file_name}")
