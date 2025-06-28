import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

st.title("JFK Flight Route Explorer")
st.subheader("1. Global Map of Direct Routes from JFK")

# Load data from source
routes_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
airports_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

routes = pd.read_csv(routes_url, header=None, names=[
    'Airline','Airline_ID','Src_IATA','Src_Airport_ID',
    'Dst_IATA','Dst_Airport_ID','Codeshare','Stops','Equipment'
])

airports = pd.read_csv(airports_url, header=None, names=[
    'Airport_ID','Name','City','Country','IATA','ICAO',
    'Latitude','Longitude','Altitude','Timezone','DST',
    'Tz_db','Type','Source'
])

# Filter for JFK
jfk_routes = routes[routes['Src_IATA'] == 'JFK'].copy()

# Merge destination coordinates
jfk_routes = jfk_routes.merge(
    airports[['IATA', 'City', 'Country', 'Latitude', 'Longitude']],
    left_on='Dst_IATA', right_on='IATA',
    how='left'
)

# Define JFK coordinates
jfk_lat = 40.6413
jfk_lon = -73.7781

# Filter and prepare flight_paths (assumes jfk_routes is preloaded)
flight_paths = jfk_routes[['Dst_IATA', 'City', 'Country', 'Latitude', 'Longitude']].dropna().copy()
flight_paths['Src_Lat'] = jfk_lat
flight_paths['Src_Lon'] = jfk_lon

fig_map = go.Figure()

# Lines
for _, row in flight_paths.iterrows():
    fig_map.add_trace(go.Scattergeo(
        locationmode='country names',
        lon=[row['Src_Lon'], row['Longitude']],
        lat=[row['Src_Lat'], row['Latitude']],
        mode='lines',
        line=dict(width=1, color='blue'),
        opacity=0.3,
    ))

# Markers
fig_map.add_trace(go.Scattergeo(
    lon=flight_paths['Longitude'],
    lat=flight_paths['Latitude'],
    mode='markers',
    marker=dict(size=4, color='red'),
    text=flight_paths['City'] + ', ' + flight_paths['Country'],
    hoverinfo='text'
))

fig_map.update_layout(
    title_text='Direct Flight Paths from JFK',
    showlegend=False,
    geo=dict(
        scope='world',
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(243, 243, 243)',
        countrycolor='rgb(204, 204, 204)',
    )
)

st.plotly_chart(fig_map, use_container_width=True)
