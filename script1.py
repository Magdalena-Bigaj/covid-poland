from flask import Flask, render_template, render_template_string
from datetime import datetime, timedelta
import functools
import requests
import datetime as dt
from datetime import timedelta
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.io import output_file, output_notebook
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Range1d, LinearAxis
from bokeh.layouts import row, column, gridplot
from bokeh.models.widgets import Tabs, Panel
from bokeh.themes import built_in_themes
from bokeh.io import curdoc
from bokeh.embed import components
from bokeh.resources import CDN

app = Flask(__name__)


def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_cache(func):
        func = functools.lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


@timed_lru_cache(43200)
# @functools.lru_cache()
def read_cases():
    csv_data = pd.read_csv("https://opendata.ecdc.europa.eu/covid19/casedistribution/csv")
    return csv_data


@app.route('/')
def index():
    csv_data = read_cases()

    csv_data['dateRep'] = pd.to_datetime(csv_data['dateRep'], format='%d/%m/%Y')

    csv_data.sort_values('dateRep')

    csv_data_poland = csv_data.loc[csv_data['countriesAndTerritories'] == 'Poland']

    curdoc().theme = 'light_minimal'
    r = list(csv_data_poland['dateRep'])
    y_range_margin = 200

    p = figure(title='Covid.Poland', plot_width=800, plot_height=400, background_fill_color= '#edf2f4', border_fill_color= '#D9E4E8',
               y_range=(0, max(csv_data_poland['cases_weekly'] + y_range_margin)),
               x_range=(r[-1], r[0]),
               x_axis_label='time', x_axis_type='datetime')

    p.vbar(csv_data_poland['dateRep'], top=csv_data_poland['cases_weekly'], color='#003049', width=timedelta(weeks=0.8),
           legend_label='cases_weekly')

    p.extra_y_ranges = {"deaths_weekly": Range1d(start=0, end=max(csv_data_poland['deaths_weekly'] + y_range_margin))}
    p.line(csv_data_poland['dateRep'], csv_data_poland['deaths_weekly'], y_range_name='deaths_weekly', color='#d62828',
           legend_label='deaths_weekly')
    p.add_layout(LinearAxis(y_range_name="deaths_weekly"), 'right')

    p.legend.location = 'top_left'

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]

    count_cases=("{:,d}".format(int(sum(csv_data_poland['cases_weekly']))))

    return render_template("index.html", script1=script1, div1=div1, cdn_js=cdn_js, count_cases= count_cases)



if __name__ == "__main__":
    app.run(debug=True)
