import pandas as pd 
import math
def get_data(df,rows,page):
    start = (page - 1) * rows
    end = start + rows
    try:
        description =  df.describe()
        columns_ = df.columns.tolist()
        df_slice = df.iloc[start:end].where(pd.notna(df.iloc[start:end]), None)
        data = df_slice.values.tolist()
        # Clean any remaining nan/numpy types
        data = [
        [None if (isinstance(v, float) and math.isnan(v)) else v for v in row]
        for row in data
        ]
        total_rows = df.shape[0]
        total_pages = math.ceil(total_rows / rows)
        return {
             "data": data,
             "columns": columns_,
             "total_rows": total_rows,
             "page": page,
             "rows_per_page": rows,
             "total_pages": total_pages
            }
    except Exception as e:
        print(e)
        