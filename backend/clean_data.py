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
        return {"status":"success","df":df}
    except Exception as e:
        print(e)
        return {"status":"error","error":e}

def drop_rows(df,scope,columnn = None):
    try:
        if scope == "any":
            df = df.dropna(how = "any")
        elif scope == "all":
            df = df.dropna(how = "all")
        elif columnn:
            df = df.dropna(subset = [columnn])
        return {"status":"success","df":df}
    except Exception as e:
        print(e)
        return {"status":"error","error":e}

def drop_column(df,column):
    try:
        df = df.drop(columns = column)
        return {"status":"success","df":df}
    except Exception as e:
        print(e)
        return {"status":"error","error":e}

def rename_column(df,column,name):
    try:
        df = df.rename(columns = {column:name})
        return {"status":"success","df":df}
    except Exception as e:
        print(e)
        return {"status":"error","error":e}

def remove_duplicates(df,keep):
    try:
        if keep =="first":
            df = df.drop_duplicates()
        if keep =="last":
            df = df.drop_duplicates(keep = "last")
        return {"status":"success","df":df}
    except Exception as e:
        print(e)
        return {"status":"error","error":e}

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
        return {"status":"success","df":df}
    except Exception as e:
        e =  f"Cannot convert to {type_}"
        print(e)
        return {"status":"error","error":e}

def replace_val(df,column, find_val, replace_val, exact_match):
    try:
        if exact_match == True:
            df[column] = df[column].replace(find_val,replace_val)
        if exact_match == False:
            df[column] = df[column].str.replace(rf'{find_val}', replace_val, regex=True)
        return {"status":"success","df":df}
    except Exception as e:
        print(e)
        return {"status":"error","error":e}

def trim_space(df,column):
    try:
        if pd.api.types.is_string_dtype(df[column]):
            df[column] = df[column].str.strip()
        else:
            return f"Column {column} is not a string column"
        return {"status":"success","df":df}
    except Exception as e:
        print(e)
        return {"status":"error","error":e}

def change_case(df,column,case):
    try:
        if pd.api.types.is_string_dtype(df[column]):
            if case == "upper":
                df[column] = df[column].str.upper()
            if case == "lower":
                df[column] = df[column].str.lower()
            if case == "title":
                df[column] = df[column].str.title()
        return {"status":"success","df":df}
    except Exception as e:
        print(e)
        return {"status":"error","error":e}

def reorder_columns(df, new_order):
    # only keep columns that actually exist in df
    valid_order = [col for col in new_order if col in df.columns.tolist()]
    # add any missing columns at the end
    for col in df.columns:
        if col not in valid_order:
            valid_order.append(col)
    return df[valid_order]