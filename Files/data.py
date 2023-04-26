import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def data_read():
    data = pd.read_csv("data/data.csv")
    return data

def make_data_monthly(data):

    to_keep = ["Natural gas", "Coal", "Oil","Renewables", "Net electricity production", "Wind", "Solar", "Hydro", "Nuclear", "Geothermal", "Total combustible fuels", "Distribution losses"]

    data_filtered = data[data["PRODUCT"].isin(to_keep)]
    data_group = data_filtered.groupby(by=['COUNTRY', 'TIME', "PRODUCT"])["VALUE"].sum().reset_index()
    data_monthly  = data_group.pivot(index=['COUNTRY', 'TIME'], columns='PRODUCT', values='VALUE').reset_index()
    data_monthly["Other_renewable"] = data_monthly["Renewables"] - sum([data_monthly["Geothermal"],data_monthly["Hydro"], data_monthly["Solar"], data_monthly["Wind"]])
    data_monthly["TIME"] = pd.to_datetime(data_monthly.TIME)
    data_monthly.sort_values(by=["COUNTRY", "TIME"], inplace=True)
    return data_monthly

def make_data_yearly(data):
    data_monthly = make_data_monthly(data)
    data_yearly = data_monthly.groupby(["COUNTRY", pd.Grouper(key='TIME', axis=0, freq='Y')]).sum().sort_values(by=["COUNTRY","TIME"]).reset_index()
    data_yearly["%_RENEWABLE_PRODUCED"] = data_yearly["Renewables"] / (data_yearly["Net electricity production"] + data_yearly["Distribution losses"]) * 100
    data_yearly["%_NUCLEAR_PRODUCED"] = data_yearly["Nuclear"] / (data_yearly["Net electricity production"] + data_yearly["Distribution losses"]) * 100
    data_yearly["%_FOSSILE_PRODUCED"] = data_yearly["Total combustible fuels"] / (data_yearly["Net electricity production"] + data_yearly["Distribution losses"]) * 100
    data_yearly["TIME"] = data_yearly["TIME"].apply(lambda x: x.year)
    return data_yearly

def make_data_global_yearly(data):
    data_global = make_data_yearly(data)

    data_global = data_global.groupby(["COUNTRY", "TIME"]).sum().sort_values(by=["COUNTRY","TIME"]).reset_index()
    data_global = data_global.groupby(by="TIME").sum().reset_index()
    return data_global

def make_country_plot_yearly(country, data_yearly):
    mask = data_yearly["COUNTRY"] == country
    data_filtered = data_yearly[mask]

    x = data_filtered["TIME"]
    y_net_electricity = data_filtered["Net electricity production"]
    y_nuclear = data_filtered["Nuclear"]
    y_renewables = data_filtered["Renewables"]
    y_combustible_fuels = data_filtered["Total combustible fuels"]
    y_other = y_net_electricity - y_nuclear - y_renewables - y_combustible_fuels

    trace2 = go.Bar(x=x,y=y_nuclear,name='Nuclear')
    trace3 = go.Bar(x=x,y=y_renewables,name='Renewables')
    trace4 = go.Bar(x=x,y=y_combustible_fuels,name='Total combustible fuels')
    trace5 = go.Bar(x=x,y=y_other,name='Other')

    layout = go.Layout(
        title=f'Electricity Production by Years of {country} (GWh)',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Electricity Production (GWh)'),
        barmode='stack'
    )
    fig = go.Figure(data=[trace2, trace3, trace4, trace5], layout=layout)
    return fig

def make_country_ratio_yearly(country, data_yearly):
    mask = data_yearly["COUNTRY"] == country
    data_filtered = data_yearly[mask]

    y1 = data_filtered["%_RENEWABLE_PRODUCED"]
    y2 = data_filtered["%_NUCLEAR_PRODUCED"]
    y3 = data_filtered["%_FOSSILE_PRODUCED"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_filtered["TIME"], y=y1, mode="lines", name="Renewable energy produced (%)"))
    fig.add_trace(go.Scatter(x=data_filtered["TIME"], y=y2, mode="lines", name="Nuclear energy produced (%)"))
    fig.add_trace(go.Scatter(x=data_filtered["TIME"], y=y3, mode="lines", name="Fossile energy produced (%)"))

    fig.update_layout(title=f'Proportion of energy type generated by {country} (GWh)',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Energy ratio produced (%)'),
        yaxis_range=[0,100]
    )
    return fig

def make_data_rad_ratio(energy_type, data_yearly):
    data_rad = data_yearly[~data_yearly["COUNTRY"].isin(['OECD Americas','OECD Asia Oceania', 'OECD Europe', 'OECD Total','IEA Total' ])].sort_values(by=["TIME",energy_type])
    fig = px.bar_polar(data_rad, r=energy_type, theta="COUNTRY",animation_frame="TIME", title=f"Ratio of {energy_type[2:-9].title()} energy produced by country (%)", width=650, height=650, range_r=[0,100])
    return fig

def make_data_rad_total(energy_type, data_yearly):
    if energy_type == "Fossile":
        energy_type = "Total combustible fuels"

    data_rad = data_yearly[~data_yearly["COUNTRY"].isin(['OECD Americas','OECD Asia Oceania', 'OECD Europe', 'OECD Total','IEA Total' ])].sort_values(by=["TIME",energy_type])
    fig = px.bar_polar(data_rad, r=energy_type, theta="COUNTRY",animation_frame="TIME", title=f"Amount of {energy_type[2:-9].title()} energy produced by country (GWh) (log scale)", width=650, height=650, log_r=True)
    return fig

def make_data_global_plot(data_global, org):
    mask = data_global["COUNTRY"] == org
    data_used = data_global[mask]
    to_display = ["Natural gas", "Coal", "Oil","Renewables", "Net electricity production", "Wind", "Solar", "Hydro", "Nuclear", "Geothermal", "Total combustible fuels"]
    fig = px.line(data_used, x="TIME", y=to_display, title = f"Total energy production of {org} per energy type (GWh)", labels={"value":"energy produced (GWh)", "TIME": "Year", "variable": "Energy type"}, width=1000, height=650)
    return fig
