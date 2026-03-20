import pandas as pd 
import numpy as np 
import math


def clean_null(df,column,method,custom_val = None):
    try:
        if method == "mean":
             df[column] = df[column].fillna(df[column].mean())
        elif method == "median": 
            df[column] = df[column].fillna(df[column].median())
        elif method == "mode": 
            df[column] = df[column].fillna(df[column].mode()[0])
        elif method == "custom": 
            df[column] = df[column].fillna(custom_val)
        else: 
            return df
        return df
    except Exception as e:
        print(e)

def drop_rows(df,scope,columnn = None):
    try:
        if scope == "any":
            df = df.dropna(how = "any")
        elif scope == "all":
            df = df.dropna(how = "all")
        elif columnn:
            df = df.dropna(subset = [columnn])
        return df
    except Exception as e:
        print(e)

def drop_column(df,column):
    try:
        df = df.drop(columns = column)
        return df
    except Exception as e:
        print(e)

def rename_column(df,column,name):
    try:
        df = df.rename(columns = {column:name})
        return df
    except Exception as e:
        print(e)

def remove_duplicates(df,keep):
    try:
        if keep =="first":
            df = df.drop_duplicates()
        if keep =="last":
            df = df.drop_duplicates(keep = "last")
        return df
    except Exception as e:
        print(e)

def change_dtype(df,column,type_):
    try:
        type_map = {
            "int": "int64",
            "float": "float64",
            "str": "object",
            "datetime": "datetime64[ns]"
        }
        mapped = type_map.get(type_, type_)
        if type_ == "datetime":
            df[column] = pd.to_datetime(df[column])
        else :
            df[column] = df[column].astype(mapped)
        return df
    except Exception as e:
        error =  f"Cannot convert to {type_}"
        return error

def replace_val(df,column, find_val, replace_val, exact_match):
    try:
        if exact_match == True:
            df[column] = df[column].replace(find_val,replace_val)
        if exact_match == False:
            df[column] = df[column].str.replace(rf'{find_val}', replace_val, regex=True)
        return df
    except Exception as e:
        print(e)

def trim_space(df,column):
    try:
        if pd.api.types.is_string_dtype(df[column]):
            df[column] = df[column].str.strip()
        else:
            return f"Column {column} is not a string column"
        return df
    except Exception as e:
        print(e)

def change_case(df,column,case):
    try:
        if pd.api.types.is_string_dtype(df[column]):
            if case == "upper":
                df[column] = df[column].str.upper()
            if case == "lower":
                df[column] = df[column].str.lower()
            if case == "title":
                df[column] = df[column].str.title()
        return df
    except Exception as e:
        print(e)

def reorder_columns(df, new_order):
    # validate all columns exist
    if set(new_order) != set(df.columns.tolist()):
        raise ValueError("Column mismatch — new_order must contain all existing columns.")
    return df[new_order]