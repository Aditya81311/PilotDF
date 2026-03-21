import plotly.express as px
import plotly.utils
import plotly.io as pio
import json
import pandas as pd
import numpy as np

def generate_chart(df,options):
    df = df.copy()
    try:
        if options["chart_type"] == "bar":
            plot =  px.bar(df,x = options["x"],y=options["y"],title=options["title"])

        if options["chart_type"] == "line":
            plot =  px.line(df,x = options["x"],y=options["y"],title=options["title"]
            ,orientation=options["orientation"])

        if options["chart_type"] == "scatter":
            plot =  px.scatter(df,x = options["x"],y=options["y"],title=options["title"])

        if options["chart_type"] == "histogram":
            plot =  px.histogram(df,x = options["x"],nbins=options["bins"],title=options["title"])

        if options["chart_type"] == "pie":
            plot =  px.pie(df,names=options["x"],
            values=options["y"],title=options["title"])

        return pio.to_html(plot, full_html=False, include_plotlyjs='cdn')
    except Exception as e:
        print(e)

