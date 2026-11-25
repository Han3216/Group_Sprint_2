#!/usr/bin/env python
# coding: utf-8

# In[2]:


import ast
import pandas as pd

df = pd.read_csv("filtered_matrix.csv")

#cleaning the list
def parse_list(x):
    if isinstance(x, list):
        return x
    if pd.isna(x) or str(x).strip() in ("", "[]"):
        return []
    try:
        return ast.literal_eval(x)
    except (ValueError, SyntaxError):
        return [m.strip(" '\"") for m in str(x).strip("[]").split(",")]

df["medications"] = df["medications"].apply(parse_list) #apply the cleaning function to the column with medication lists


df["n_drugs"] = df["medications"].str.len()


dates = pd.to_datetime(df["created_utc"], utc=True, errors="coerce")
df["year"] = dates.dt.year.astype("Int64")



# One row per (post, medication)
rows = df.explode("medications").rename(columns={"medications": "drug"})
rows["multi_drug"] = rows["n_drugs"] > 1
rows["label"] = ""                       # to be filled in by hand



rows = rows.reset_index(drop=True)
rows.to_csv("reddit_data.csv", index=False)




print(f"{len(df)} posts -> {len(rows)} (post, drug) rows")
print(rows["drug"].value_counts())
print(rows["multi_drug"].value_counts())


# In[13]:


import re

df1=pd.read_csv("reddit_data_labelled.csv")
rows = df1.explode("drug")



#using the medications dictionary from before
medications = {
    # Antidepressants - SSRIs
    "sertraline": ["sertraline", "zoloft", "lustral"],
    "fluoxetine": ["fluoxetine", "prozac"],
    "escitalopram": ["escitalopram", "lexapro", "cipralex"],
    "citalopram": ["citalopram", "celexa", "cipramil"],
    "paroxetine": ["paroxetine", "paxil", "seroxat"],

    # Other antidepressants
    "venlafaxine": ["venlafaxine", "effexor", "efexor"],
    "duloxetine": ["duloxetine", "cymbalta"],
    "bupropion": ["bupropion", "wellbutrin"],
    "mirtazapine": ["mirtazapine", "remeron", "zispin"],

    # ADHD medications
    "methylphenidate": ["methylphenidate", "ritalin", "concerta"],
    "lisdexamfetamine": ["lisdexamfetamine", "vyvanse", "elvanse"],
    "amphetamine": ["adderall"],

    # Anti-anxiety medications
    "alprazolam": ["alprazolam", "xanax"],
    "diazepam": ["diazepam", "valium"],

    # Mood stabilisers
    "lamotrigine": ["lamotrigine", "lamictal"]
}


def find_brands(drug, text):
    possible_brands = brands_by_drug.get(str(drug).strip().lower(), [])
    text = "" if pd.isna(text) else str(text)

    matches = [
        brand for brand in possible_brands
        if re.search(rf"\b{re.escape(brand)}\b", text, flags=re.IGNORECASE)
    ]
    return "; ".join(matches)


brands_by_drug = {
    drug: [name for name in names if name != drug]
    for drug, names in medications.items()
}


rows["brand_name"] = [
    find_brands(drug, text)
    for drug, text in zip(rows["drug"], rows["body"])
]


# Replace blank brand names with the generic drug name
names = rows["brand_name"].fillna("").str.strip()
names = names.where(names.ne(""), rows["drug"])

# Split "ritalin; concerta" into a list, then make one row per name
rows["brand_name"] = names.str.split("; ")
rows = rows.explode("brand_name", ignore_index=True)




rows.to_csv("reddit_data_with_brands.csv", index=False)







# In[ ]:




