#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pandas as pd
from datetime import datetime, date
import numpy as np

pd.options.display.max_columns = 999


# cleaning functions
def clean_date(x):
    try:
        return datetime.strptime(x, "%d/%m/%y")
    except:
        return pd.NaT


def clean_df_date(df, colname):
    df_clean = df.copy(deep=True)
    df_clean.loc[:, colname].fillna(value="01/01/25", inplace=True)
    df_clean.loc[:, colname] = df_clean.loc[:, colname].apply(lambda x: clean_date(x))
    df_clean.replace(to_replace=clean_date("01/01/25"), value=pd.NaT, inplace=True)
    return df_clean


def calculate_age(row):
    today = date.today()
    born = row["dob"]
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


# ### Read data ###

user_df = pd.read_csv('data/User.csv')
symptom_df = pd.read_csv('data/Symptom.csv')
period_df = pd.read_csv('data/Period.csv')

# ### Clean user_df ###

# get unique user id
unique_users = list(set(user_df["id"]))
active_users = list(set(period_df["User_id"]))
symptom_users = list(set(symptom_df["user_id"]))

# remove inactive users
query = "id in {0}".format(str(active_users))
user_df_clean = user_df.query(query)

# create age feature and format dates
user_df_clean.loc[:, "dob"].fillna(value="01/01/25", inplace=True)
user_df_clean.loc[:, "dob"] = user_df_clean.loc[:, "dob"].apply(lambda x: clean_date(x))
user_df_clean.loc[:, "age"] = user_df_clean.apply(calculate_age, axis=1)
user_df_clean.replace(to_replace=clean_date("01/01/25"), value=pd.NaT, inplace=True)
user_df_clean.loc[user_df_clean.age < 0, 'age'] = np.nan


# ### Clean period_df ###

period_df_nona = period_df.dropna()

# fix wrong format of date
period_df_nona_clean = period_df_nona[~period_df_nona.start_date.str.contains('-')]
period_df_nona_clean = period_df_nona_clean.assign(
    start_date_clean=period_df_nona_clean.start_date
    .apply(lambda x: datetime.strptime(x, '%d/%m/%y')))
period_df_nona_clean = period_df_nona_clean.assign(
    end_date_clean=period_df_nona_clean.end_date
    .apply(lambda x: datetime.strptime(x, '%d/%m/%y')))

# get end of cycle date
cycle_table = pd.merge(period_df_nona_clean, period_df_nona_clean,
                       on='User_id')
cycle_table_filter = cycle_table[(cycle_table.start_date_clean_y > cycle_table.end_date_clean_x)]

# keep only the most relevant possible cycle
cycle_table_filter_2 = cycle_table_filter\
    .sort_values(by=['start_date_clean_x', 'start_date_clean_y'])\
    .drop_duplicates(subset=['User_id', 'start_date_clean_x'], keep='first')
cycle_table_filter_2 = cycle_table_filter_2.assign(
    cycle_length=cycle_table_filter_2
    .apply(lambda x: (x['start_date_clean_y'] - x['start_date_clean_x']).days, axis=1))
cycle_table_filter_2 = cycle_table_filter_2.assign(
    end_cycle=cycle_table_filter_2
    .apply(lambda x: x['start_date_clean_y'] - pd.DateOffset(1) if x['cycle_length'] < 40 else pd.NaT, axis=1))

cols_to_keep = ['User_id', 'start_date_x', 'end_date_x', 'start_date_clean_x', 'end_date_clean_x',
                'cycle_length', 'end_cycle']
rich_period_df = pd.merge(period_df, cycle_table_filter_2[cols_to_keep],
                          left_on=['User_id', 'start_date'],
                          right_on=['User_id', 'start_date_x'], how='left')

rich_period_df = rich_period_df.drop(columns=['start_date_x', 'end_date_x'])
new_col_names = [c.replace('_x', '') for c in rich_period_df.columns]
rich_period_df.columns = new_col_names
rich_period_df_ = clean_df_date(rich_period_df, 'start_date')
rich_period_df__ = clean_df_date(rich_period_df_, 'end_date')
rich_period_df_clean = rich_period_df__.copy()
rich_period_df_clean.loc[rich_period_df_clean.cycle_length>40, 'cycle_length'] = np.nan
cols_to_keep = ['start_date', 'end_date', 'User_id', 'cycle_length', 'end_cycle']
rich_period_df_clean = rich_period_df_clean[cols_to_keep]
rich_period_df_clean.to_csv('data/clean_period.csv', index=False)

# ### Clean symptom_df ###

symptom_df_clean = symptom_df[~symptom_df.date.str.contains('-')]
symptom_df_clean = symptom_df_clean.assign(
    date_clean=symptom_df_clean.date.apply(func=lambda x: datetime.strptime(x, '%d/%m/%y')))
rich_symptoms = pd.merge(symptom_df_clean, rich_period_df_clean, left_on='user_id', right_on='User_id')
rich_symptoms_map = rich_symptoms[(rich_symptoms.date_clean>=rich_symptoms.start_date)&
                                  (rich_symptoms.date_clean<=rich_symptoms.end_cycle)]
rich_symptoms_map = rich_symptoms_map.assign(
    day_of_cycle=rich_symptoms_map.apply(lambda x: (x['date_clean'] - x['start_date']).days, axis=1))
rich_symptoms_map = rich_symptoms_map[['id', 'user_id', 'date_clean',
                                       'start_date', 'end_date',
                                       'cycle_length', 'end_cycle', 'day_of_cycle']]

# ### Merge data ###

# merging symptoms
symptom_df_clean_full = pd.merge(symptom_df_clean, rich_symptoms_map,
                                 left_on=["user_id", "date_clean", "id"],
                                 right_on=["user_id", "date_clean", "id"],
                                 how="left")
symptom_df_clean_full = symptom_df_clean_full[['id', 'user_id', 'acne', 'backache', 'bloating', 'cramp', 'diarrhea',
                                               'dizzy', 'headache', 'mood', 'nausea', 'sore', 'date_clean',
                                               'start_date', 'end_date', 'cycle_length', 'end_cycle', 'day_of_cycle']]
symptom_df_clean_full_uni = symptom_df_clean_full\
    .sort_values(by=['id', 'cycle_length'])\
    .drop_duplicates(subset=['id'], keep='last')
symptom_df_clean_full_uni.to_csv('data/clean_symptom.csv', index=False)

# merging users
df_final = pd.merge(symptom_df_clean_full_uni, user_df_clean,
                    left_on="user_id",
                    right_on="id",
                    how="left")

# drop useless features
df_final["symptom_id"] = df_final["id_x"]
df_final = df_final[['user_id', 'acne', 'backache', 'bloating', 'cramp', 'diarrhea',
                     'dizzy', 'headache', 'mood', 'nausea', 'sore', 'date_clean',
                     'start_date', 'end_date', 'cycle_length', 'end_cycle',
                     'day_of_cycle', 'dob', 'cycle_length_initial',
                     'period_length_initial', 'age', "symptom_id"]]

# add id_cycle
df_final = df_final.sort_values(["user_id", "start_date", "end_cycle"])
df_final.reset_index(inplace=True, drop=True)
cycle_id = []
cycles = []
d_cycles = {}
for i in df_final.index:
    user = df_final.loc[i, 'user_id']
    start = df_final.loc[i, 'start_date']
    end = df_final.loc[i, 'end_cycle']
    if pd.isnull(start) or pd.isnull(end):
        cycle_id.append(np.nan)
    elif str((user, start, end)) in cycles:
        cycle_id.append(d_cycles[str((user, start, end))])
    else:
        cycle_id.append(i)
        d_cycles[str((user, start, end))] = i
        cycles.append(str((user, start, end)))
        i += 1
df_final.loc[:, "cycle_id"] = cycle_id

# save data
df_final.to_csv('data/df_final.csv', index=False)
