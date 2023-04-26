from Files.data import make_data_yearly, data_read, make_country_plot_yearly, make_country_ratio_yearly, make_data_rad_ratio, make_data_rad_total, make_data_global_plot
import streamlit as st

data = data_read()

if "but1" not in st.session_state:
    st.session_state["but1"] = False
if "but2" not in st.session_state:
    st.session_state["but2"] = False
if "but3" not in st.session_state:
    st.session_state["but3"] = False

def click(key0, key1, key2):
    st.session_state[key0] = True
    st.session_state[key1] = False
    st.session_state[key2] = False
    placeholder.empty()

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.sidebar.header("Additional info")
placeholder = st.sidebar.empty()
placeholder.markdown("""
                     The data has been sourced from the IEA and covers the dates from 2020 to 2022. The data only contains 53 countries.\n
                     The dataset is missing some key countries (like Russia or the Middle East) which production's capabilities would have changed some balance presented here.\n
                     This is an exercise for me to practice data visualisation and should be viewed as such.\n
                     The dataset can be found here https://www.iea.org/data-and-statistics/data-tools/monthly-electricity-statistics
                     """)

st.header("Energy production visualisation")
st.text(" ")

col_but1, col_but2, col_but3 = st.columns(3)
col_but1.button("Country charts", key="button1", on_click=click, args=("but1","but2","but3"))
col_but2.button("Global ratio charts", key="button2", on_click=click, args=("but2","but1","but3"))
col_but3.button("Global charts", key="button3", on_click=click, args=("but3","but1","but2"))

data_yearly = make_data_yearly(data)
#------------------------------------------------------------------------------------------
if st.session_state["but1"] is True:
    placeholder.markdown("View the breakdown of the energy produced by a country per year.")
    country_list = data_yearly["COUNTRY"].unique()
    country = st.selectbox("Country selector",country_list,key="dropdown1")

    col1, col2 = st.columns(2)
    col1.plotly_chart(make_country_plot_yearly(country, data_yearly), use_container_width=True)
    col2.plotly_chart(make_country_ratio_yearly(country, data_yearly))

#--------------------------------------------------------------------------------------------
if st.session_state["but2"] is True:
    placeholder.markdown("View the type of energy produced by country as a ratio of the country's total production (left) and its actual value (right) per year.")
    energy_dict = {"Renewables": "%_RENEWABLE_PRODUCED", "Nuclear":"%_NUCLEAR_PRODUCED", "Fossile":"%_FOSSILE_PRODUCED"}
    energy_type = st.selectbox("Energy type",energy_dict.keys(),key="dropdown2")

    col1, col2 = st.columns(2)
    col1.plotly_chart(make_data_rad_ratio(energy_dict[energy_type], data_yearly))
    col2.plotly_chart(make_data_rad_total(energy_type, data_yearly))

#----------------------------------------------------------------------------------------------
if st.session_state["but3"] is True:
    placeholder.markdown("""
                         View the total energy production at a continent or global level (for participating countries).\n
                         You can click on the entry in the legend of the graph to toggle them on or off.""")
    list_org = ['OECD Americas','OECD Asia Oceania', 'OECD Europe', 'OECD Total','IEA Total']
    org = st.selectbox("Country selector",list_org,key="dropdown2")

    st.plotly_chart(make_data_global_plot(data_yearly,org))
