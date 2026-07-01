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
#Order dataframe
df = df[['squad', 'number','position', 'player', 'date of birth', 'age', 'captain', 'games', 'goals', 'club']]

df.head(50)

# %%
#Starting zodiac analysis
def get_zodiac_sign(date):
    month = date.month
    day = date.day

    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    else:
        return "Pisces"
# %%
df["zodiac sign"] = df["date of birth"].apply(get_zodiac_sign)

df.head()
#%%
#Export to csv
df.to_csv("Transform/fifa_2026_squads.csv", index=False, encoding="utf-8-sig")
# %%
