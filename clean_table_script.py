#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pandas as pd
from datetime import datetime
import numpy as np
pd.options.display.max_columns = 999

# read data
user_df = pd.read_csv('data/User.csv')
symptom_df = pd.read_csv('data/Symptom.csv')
period_df = pd.read_csv('data/Period.csv')


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


### clean period_df
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
rich_period_df_clean.to_csv('clean_period.csv', index=False)

# attempt to complete missing data




### clean symptom_df
symptom_df_clean = symptom_df[~symptom_df.date.str.contains('-')]
symptom_df_clean = symptom_df_clean.assign(date_clean=symptom_df_clean.date.apply(func=lambda x: datetime.strptime(x, '%d/%m/%y')))
