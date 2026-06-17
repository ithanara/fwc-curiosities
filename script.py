#%%
import pdfplumber
import pandas as pd
import re
import warnings

warnings.filterwarnings("ignore")

#%%
#Descobrir em qual página está cada seleção
squads = []
with pdfplumber.open("Data/2026_FIFA_World_Cup_squads.pdf") as pdf:

    for i, page in enumerate(pdf.pages):
        text = page.extract_text()

        if not text:
            continue

        match = re.search(r'([^\n]+)\nCoach:', text)

        if match:
            squad = match.group(1).strip()

            squads.append({
                "page": i,
                "squad": squad
            })
df_pages = pd.DataFrame(squads)
df_pages
# %%
#Pegar um time inteiro e criar uma tabela
rows = []
with pdfplumber.open("Data/2026_FIFA_World_Cup_squads.pdf") as pdf:
    pages = pdf.pages[1:3]
    for page in pages:
        tables = page.extract_tables()

        for table in tables:
            for line in table:
                rows.append(line)
print(len(rows))
print(rows[:5])
# %%
header = rows[0]

df_czech = pd.DataFrame(
    rows[1:],
    columns=header
)

df_czech["Squad"] = "Czech Republic"
df_czech
# %%
df_czech.to_csv(
    "Groups/A_czech.csv",
    index=False,
    encoding="utf-8-sig"
)
# %%
