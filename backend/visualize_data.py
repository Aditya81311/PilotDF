import plotly.express as px
import plotly.utils
import plotly.io as pio
import json
import pandas as pd
import numpy as np

def generate_chart(df,options):
    df = df.copy()
    x = options["x"]
    y = options["y"]
    title = options["title"]
    color_by = options["color_by"]
    bins = options["bins"]
    orientation = options["orientation"]
    try:
        if options["chart_type"] == "bar":
            plot =  px.bar(df,x =x,y=y,title=title,color = color_by,orientation=orientation)

        if options["chart_type"] == "line":
            plot =  px.line(df,x =x,y=y,title=title,color=color_by)

        if options["chart_type"] == "scatter":
            plot =  px.scatter(df,x =x,y=y,title=title,color=color_by)

        if options["chart_type"] == "histogram":
            plot =  px.histogram(df,x =x,nbins=bins,title=title)

        if options["chart_type"] == "pie":
            plot =  px.pie(df,names=x,
            values=y,title=title)
        
        if options["chart_type"] == "box":
            plot = px.box(df,x=x,y=y,title=title)

        return pio.to_html(plot, full_html=False, include_plotlyjs=True,div_id=f"chart_{id(plot)}")
    except Exception as e:
        print(e)

