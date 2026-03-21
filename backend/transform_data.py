import pandas as pd 
import numpy as np 
import math
from sklearn.preprocessing import OneHotEncoder 
from sklearn.preprocessing import LabelEncoder

def new_column(df,name,formula):
    try:
        df[name] = df.eval(formula)
        return df
    except Exception as e:
        print(e)
        
def normalize(df,column,method):
    try:
        min_  = df[column].min()
        max_ = df[column].max()
        mean_ = df[column].mean()
        if method == "minmax":
            df[column] = (df[column] - min_) / (max_ - min_)
        elif method == "zscore":
            df[column] = (df[column] - mean_) / df[column].std()
        return df
    except:
        print(e)
        

def encode(df, column, method, drop_first):
    try:
        if method == "onehot":
            encoder = OneHotEncoder(sparse_output=False)
            encoded = encoder.fit_transform(df[[column]])
            new_cols = encoder.get_feature_names_out([column])
            encoded_df = pd.DataFrame(encoded, columns=new_cols, index=df.index)
            df = df.drop(columns=[column])
            if drop_first == "true":
                encoded_df = encoded_df.iloc[:, 1:]
            df = pd.concat([df, encoded_df], axis=1)
        elif method == "label":
            encoder = LabelEncoder()
            df[column] = encoder.fit_transform(df[column])
        return df
    except Exception as e:
        print(e)
        

def bin_numaric(df, column, bins, labels):
    try:
        bins = int(bins)
        if labels:
            labels = [l.strip() for l in labels.split(',')]
            if len(labels) != bins:
                print(f"Labels count {len(labels)} must match bins {bins}")
                return df
            df[column] = pd.cut(df[column], bins=bins, labels=labels)
        else:
            df[column] = pd.cut(df[column], bins=bins)
        df[column] = df[column].astype(str)
        return df
    except Exception as e:
        print(e)
        

def extract_datetime(df,column,extract):
    try:
        df[column] = pd.to_datetime(df[column],errors='coerce')
        if extract == "year":
           df["year"] = df[column].dt.year  
           return df
        elif extract == "month" :
           df["month"] = df[column].dt.month
           return df
        elif extract == "day"  :
           df["day"] = df[column].dt.day
           return df
        elif extract == "weekday" :
           df["weekday"] = df[column].dt.weekday
           return df
        elif extract == "hour":
           df["hour"] = df[column].dt.hour
           return df
    except Exception as e:
        print(e)
        

def apply_maths(df,column,operation):
    try:
        valid_options = ["log","sqrt","abs","round","square"]
        ops = {
            "log":    np.log,
            "sqrt":   np.sqrt,
            "abs":    np.abs,
            "square": np.square,
            "round":  np.round
                }
        if operation in valid_options:
            df[column] = df[column].apply(ops[operation])
            return df
    except Exception as e:
        print(e)
        