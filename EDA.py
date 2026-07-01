#%%
import pandas as pd

#%%
df = pd.read_csv("Transform/fifa_2026_squads.csv")
df.head()
# %%
df.describe()
# %%
pd.crosstab(df['age'], df['goals'])
# %%
df["zodiac sign"].value_counts()
# %%
pd.crosstab(df["squad"], df["zodiac sign"])
# %%
pd.crosstab(df["position"], df["zodiac sign"])
#%%
df.loc[df["captain"] == True, "zodiac sign"].value_counts()
# %%
df.groupby("zodiac sign")["age"].mean()
# %%
