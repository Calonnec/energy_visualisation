from Files.data_update import data_read, make_data, make_global_map, make_bar_graph, make_line_graph
import streamlit as st

data = data_read()

if "but1" not in st.session_state:
    st.session_state["but1"] = False
if "but2" not in st.session_state:
    st.session_state["but2"] = False

def click(key0, key1):
    st.session_state[key0] = True
    st.session_state[key1] = False
    #placeholder.empty()

st.set_page_config(layout="centered", initial_sidebar_state="expanded")

st.sidebar.header("Additional info")
placeholder = st.sidebar.empty()
placeholder.markdown("""
                     Select an option to start.
                      """)
on = st.sidebar.toggle("view data source", key="tog1")
if on:
    st.sidebar.write("Data source: https://www.eia.gov/international/data/world/electricity/electricity-generation?pd=2&p=00000020000000000000000000000fvu&u=1&f=A&v=column&a=-&i=none&vo=value&t=C&g=00000000000000000000000000000000000000000000000001&l=249-ruvvvvvfvtvnvv1vrvvvvfvvvvvvfvvvou20evvvvvvvvvvvvvvs&s=315532800000&e=1609459200000&vb=146&ev=false")

st.header("Energy production visualisation")
st.text(" ")

col_but1, col_but2 = st.columns(2)
col_but1.button("Global map", key="button1", on_click=click, args=("but1","but2"))
col_but2.button("Country charts", key="button2", on_click=click, args=("but2","but1"))

data_graph = make_data(data)
#------------------------------------------------------------------------------------------
if st.session_state["but2"] is True:
    placeholder.markdown("View the breakdown of the energy produced by a country per year.\n You can view either the raw value (in bilion of kWh) or in proportion of the total energy produced (in %).")
    country_list = data_graph["country"].unique()
    col_sel1, col_sel2 = st.columns(2)
    country = col_sel1.selectbox("Country selector",country_list,key="dropdown1")
    percent = col_sel2.selectbox("Display type",["raw value", "percent"],key="dropdown2")

    st.plotly_chart(make_bar_graph(data_graph,country, percent), use_container_width=True)
    st.plotly_chart(make_line_graph(data_graph, country))

#--------------------------------------------------------------------------------------------
if st.session_state["but1"] is True:
    placeholder.markdown("View on the world map the energy production for each country. You can select the type of energy and type of representation.")
    energy_perc = ["Renewables", "Nuclear", "Fossile"]
    energy_raw = ["Total produced","Nucluear produced", "Fossil produced", "Renewables produced"]
    energy_dict = {"Renewables": "%_produced_Renewables", "Nuclear":"%_produced_Nuclear", "Fossile":"%_produced_fossil", "Total produced": "Generation (billion kWh)","Nucluear produced": "Nuclear (billion kWh)", "Fossil produced": "Fossil fuels (billion kWh)", "Renewables produced" : "Renewables (billion kWh)"}

    year_list = data_graph["year"].unique()
    col_sel3, col_sel4, col_sel5 = st.columns(3)
    year = col_sel3.selectbox("Year",year_list,key="dropdown3")
    type_en = col_sel4.selectbox("Display type", ["Raw", "percent"],key="dropdown4")
    if type_en == "Raw":
        power = col_sel5.selectbox("Energy type",energy_raw,key="dropdown5")
    else: power = col_sel5.selectbox("Energy type",energy_perc,key="dropdown6")

    st.plotly_chart(make_global_map(data_graph,year, energy_dict[power]), use_container_width=True)

#----------------------------------------------------------------------------------------------
