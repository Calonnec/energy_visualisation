import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

def data_read():
    data = pd.read_csv("data/INT-Export-01-09-2024_15-54-20.csv").replace(["--","ie"],0)
    return data

def make_data(data):
    to_remove = ['Generation (billion kWh)', 'Nuclear (billion kWh)',
       'Fossil fuels (billion kWh)', 'Renewables (billion kWh)',
       'Hydroelectricity (billion kWh)',
       'Non-hydroelectric renewables (billion kWh)',
       'Geothermal (billion kWh)',
       'Solar, tide, wave, fuel cell (billion kWh)',
       'Tide and wave (billion kWh)', 'Solar (billion kWh)',
       'Wind (billion kWh)', 'Biomass and waste (billion kWh)',
       'Hydroelectric pumped storage (billion kWh)',
       'Consumption (billion kWh)']

    to_remove_2 = ['Hydroelectricity (billion kWh)',
       'Non-hydroelectric renewables (billion kWh)',
       'Geothermal (billion kWh)',
       'Solar, tide, wave, fuel cell (billion kWh)',
       'Tide and wave (billion kWh)', 'Solar (billion kWh)',
       'Wind (billion kWh)', 'Biomass and waste (billion kWh)',
       'Hydroelectric pumped storage (billion kWh)']

    data = data.rename(columns={"Unnamed: 0" : "items"})
    data["items"] = data["items"].str.strip()

    country_list = data[~data["items"].isin(to_remove)]["items"].to_list()
    country_index = {}
    for country in country_list:
        country_idx = data[data["items"] == country].index.tolist()[0]
        country_index[country] = country_idx

    data_country = {}
    for country, idx in country_index.items():
        data_df = data.iloc[idx:idx+15][1:15]
        data_country[country] = data_df[~data_df["items"].isin(to_remove_2)]

    data_em = pd.DataFrame(columns=['Generation (billion kWh)', 'Nuclear (billion kWh)', 'Fossil fuels (billion kWh)', 'Renewables (billion kWh)', 'Consumption (billion kWh)'])
    for country in list(data_country.keys())[1:]:
        data_country_test = data_country[country].copy().T
        data_country_test.columns = data_country_test.iloc[0]
        data_country_test = data_country_test.tail(-1).reset_index().rename(columns={"index": "year"})
        data_country_test.insert(0,"country",country)
        data_em = pd.concat([data_em,data_country_test])
    data_em = data_em.reset_index(drop=True)
    test = data_em.drop(["country", "year"], axis=1).apply(pd.to_numeric)
    test.insert(0,"country",data_em["country"])
    test.insert(1,"year",data_em["year"])
    data_em = test
    data_graph = data_em.copy()
    data_graph["%_produced_fossil"] = data_graph["Fossil fuels (billion kWh)"]/data_graph["Generation (billion kWh)"]
    data_graph["%_produced_Nuclear"] = data_graph["Nuclear (billion kWh)"]/data_graph["Generation (billion kWh)"]
    data_graph["%_produced_Renewables"] = data_graph["Renewables (billion kWh)"]/data_graph["Generation (billion kWh)"]
    mask = (data_graph["country"] == 'Former Czechoslovakia') |(data_graph["country"] == 'Former Serbia and Montenegro')|(data_graph["country"] == 'Former U.S.S.R.')|(data_graph["country"] == 'Former Yugoslavia')
    data_graph[mask] = data_graph[mask].replace(0,np.NaN)

    return data_graph

def make_global_map(data_graph,year, power):
    fig = px.choropleth(
    data_graph,
    locations=data_graph[data_graph["year"] == str(year)]["country"],  # Use the country names as locations
    locationmode='country names',  # Set the location mode to country names
    color=data_graph[data_graph["year"] == str(year)][power],  # Specify the column to use for coloring
    color_continuous_scale='Viridis',  # Choose a color scale
    title='Choropleth Map'
)
    return fig

def make_bar_graph(data_graph, country, percent):
    data_filtered = data_graph[data_graph["country"] == country]

    if percent == "raw value":
        title = 'Electricity Production (billion kWh)'
        x = data_filtered["year"]
        y_net_electricity = data_filtered["Generation (billion kWh)"]
        y_nuclear = data_filtered["Nuclear (billion kWh)"]
        y_renewables = data_filtered["Renewables (billion kWh)"]
        y_combustible_fuels = data_filtered["Fossil fuels (billion kWh)"]
        y_other = y_net_electricity - y_nuclear - y_renewables - y_combustible_fuels
    else:
        title = 'Electricity Production (%)'
        x = data_filtered["year"]
        #y_net_electricity = data_filtered["Generation (billion kWh)"]
        y_nuclear = 100*data_filtered["%_produced_Nuclear"]
        y_renewables = 100*data_filtered["%_produced_Renewables"]
        y_combustible_fuels = 100*data_filtered["%_produced_fossil"]
        y_other = 100 - y_nuclear - y_renewables - y_combustible_fuels

    #trace1 = go.Bar(x=x,y=y_net_electricity,name='Net electricity production')
    trace2 = go.Bar(x=x,y=y_nuclear,name='Nuclear')
    trace3 = go.Bar(x=x,y=y_renewables,name='Renewables')
    trace4 = go.Bar(x=x,y=y_combustible_fuels,name='Total combustible fuels')
    trace5 = go.Bar(x=x,y=y_other,name='Other')

    layout = go.Layout(
        title=f'Electricity Production by Years of {country}',
        xaxis=dict(title='Year'),
        yaxis=dict(title=title),
        barmode='stack'
    )
    fig = go.Figure(data=[trace2, trace3, trace4, trace5], layout=layout)
    return fig

def make_line_graph(data_graph, country):

    data_filtered = data_graph[data_graph["country"] == country]
    y1 = data_filtered["Renewables (billion kWh)"]
    y2 = data_filtered["Nuclear (billion kWh)"]
    y3 = data_filtered["Fossil fuels (billion kWh)"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_filtered["year"], y=y1, mode="lines", name="Renewable energy produced"))
    fig.add_trace(go.Scatter(x=data_filtered["year"], y=y2, mode="lines", name="Nuclear energy produced"))
    fig.add_trace(go.Scatter(x=data_filtered["year"], y=y3, mode="lines", name="Fossile energy produced"))

    fig.update_layout(title=f'Proportion of energy type generated by {country} (GWh)',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Energy ratio produced (billion kWh)'))

    return fig
