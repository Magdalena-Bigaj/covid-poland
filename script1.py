from flask import Flask, render_template

app = Flask(__name__)


@app.route('/plot/')
def plot():
    import requests
    import datetime as dt
    from datetime import timedelta
    import pandas as pd
    from bokeh.io import output_file
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

    r = requests.get("https://opendata.ecdc.europa.eu/covid19/casedistribution/csv")
    raw_data = r.content

    csv_data = pd.read_csv("https://opendata.ecdc.europa.eu/covid19/casedistribution/csv")

    csv_data['dateRep'] = pd.to_datetime(csv_data['dateRep'], format='%d/%m/%Y')

    csv_data.sort_values('dateRep')

    csv_data_poland = csv_data.loc[csv_data['countriesAndTerritories'] == 'Poland']

    curdoc().theme = 'light_minimal'
    p = figure(title='Covid.Poland', plot_width=800, plot_height=400,
               y_range=(0, max(csv_data_poland['cases'] + 200)),
               x_range=((list(csv_data_poland['dateRep']))[-1], (list(csv_data_poland['dateRep']))[0]),
               x_axis_label='time', x_axis_type='datetime')

    p.vbar(csv_data_poland['dateRep'], top=csv_data_poland['cases'], color='#003049', width=timedelta(days=0.8),
           legend_label='cases')

    p.extra_y_ranges = {"deaths": Range1d(start=0, end=max(csv_data_poland['deaths'] + 200))}
    p.line(csv_data_poland['dateRep'], csv_data_poland['deaths'], y_range_name='deaths', color='#d62828',
           legend_label='deaths')
    p.add_layout(LinearAxis(y_range_name="deaths"), 'right')

    p.legend.location = 'top_left'

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]


    return render_template("plot.html", script1=script1, div1=div1, cdn_js=cdn_js)


@app.route('/')
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
