import yaml
import pandas as pd

# Load schema
with open(r"D:\NetworkSecurity\data_schema\schema.yaml", "r") as f:
    schema = yaml.safe_load(f)

import os
import pandas as pd

base_path = "Artifacts"
# Get the first subfolder (e.g., 08_20...)
subfolder = os.listdir(base_path)[0]  
file_path = os.path.join(base_path, subfolder, "data_ingestion", "ingested", "train.csv")

df = pd.read_csv(file_path)
print(df.head())



# Compare columns
print("Columns in dataset:", df.columns.tolist())
print("Columns in schema:", list(schema["columns"].keys()))
print(df.head())   # shows first 5 rows
print(df.shape)    # shows number of rows & columns

