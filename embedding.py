import pandas as pd
df  = pd.read_csv('')
print(df.head())
df = df.set_index(["Header"])
print(f"{len(df)} rows in the data.")
print(df.head(1).to_markdown())

