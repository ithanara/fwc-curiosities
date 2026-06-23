#%%
import pandas as pd
df = pd.read_csv("Extract/fifa_2026_squads.csv")
# %%
#Rename columns
df = df.rename(columns={
    'Selecao': 'squad',
    'No.':'number',
    'Pos.':'position',
    'Player':'player',
    'Caps':'games',
    'Goals':'goals',
    'Club':'club',
    'Captain':'captain'
})

df.head()
#%%
#Strip date of birth and age
df[['date of birth', 'age']] = df['Date of birth (age)'].str.extract(
    r'(.+?)\s*\(aged\s*(\d+)\)'
)

df['date of birth'] = pd.to_datetime(
    df['date of birth'],
    format='%B %d, %Y'
)

df.drop(columns=['Date of birth (age)'], inplace=True)

df.head(200)
#%%
#Drop NaN and last lines

df = df.drop(df.index[1248:])
df.dropna(axis=1, how='all', inplace=True)

df.tail()
#%%
#Tranform numbers to int
df[['number','games','goals','age']] = df[['number','games','goals','age']].astype(int)

df.dtypes
#%%
#Export to csv
df.to_csv("Transform/fifa_2026_squads.csv", index=False, encoding="utf-8-sig")
# %%
