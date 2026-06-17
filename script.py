#%%
import pdfplumber

#%%
with pdfplumber.open("Data/2026_FIFA_World_Cup_squads.pdf") as pdf:
    page = pdf.pages[1]
    tables = page.extract_tables()
    
    for table in tables:
        for line in table:
            print(line)
# %%
