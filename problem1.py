import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Mapping the routes
st.title("Problem 1 - JFK Flight Route Explorer")
st.subheader("1. Global Map of Direct Routes from JFK")

# Load data
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

# Top destinations
st.subheader("2. Top 10 Destination Airports from JFK")

# Preprocess top destinations
top_dests = jfk_routes['Dst_IATA'].value_counts().head(10).reset_index()
top_dests.columns = ['Dst_IATA', 'Flight_Count']

# Merge to get city/country
top_dests = top_dests.merge(
    airports[['IATA', 'City', 'Country']],
    left_on='Dst_IATA', right_on='IATA',
    how='left'
)
top_dests['Label'] = top_dests['City'] + ', ' + top_dests['Country'] + ' (' + top_dests['Dst_IATA'] + ')'

# Seaborn plot to matplotlib
fig_bar, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=top_dests, y='Label', x='Flight_Count', palette='Blues_d', ax=ax)
ax.set_title('Top 5 Destination Airports from JFK (by Route Frequency)')
ax.set_xlabel('Number of Unique Routes')
ax.set_ylabel('Destination Airport')
st.pyplot(fig_bar)

# Domestic vs. International
st.subheader("3. Domestic vs. International Flights from JFK")

# Add the domestic filter
jfk_routes['is_domestic'] = jfk_routes['Country'] == 'United States'

# Count and plot as pie chart
dom_int_counts = jfk_routes['is_domestic'].value_counts().reset_index()
dom_int_counts.columns = ['is_domestic', 'count']
dom_int_counts['label'] = dom_int_counts['is_domestic'].map({True: 'Domestic', False: 'International'})

# Pie chart
fig_pie, ax = plt.subplots()
ax.pie(dom_int_counts['count'], labels=dom_int_counts['label'], autopct='%1.1f%%', startangle=90, colors=['skyblue', 'lightcoral'])
st.pyplot(fig_pie)

# Top airlines
# Prepare data
airline_stats = jfk_routes.groupby('Airline').agg(
    route_count=('Dst_IATA', 'count'),
    unique_dests=('Dst_IATA', 'nunique')
).reset_index()

# Interactive scatterplot with labels
fig_airline = px.scatter(
    airline_stats,
    x='route_count',
    y='unique_dests',
    text='Airline',  # shows airline code on hover
    labels={
        'route_count': 'Total Routes from JFK',
        'unique_dests': 'Unique Destinations Served'
    },
    title='Airline Route Frequency vs. Destination Reach from JFK',
    width=800,
    height=500
)

fig_airline.update_traces(marker=dict(size=8, color='royalblue'), textposition='top center')
fig_airline.update_layout(showlegend=False)

st.plotly_chart(fig_airline, use_container_width=True)

st.markdown("""
**Interpretation:**  
This interactive scatterplot shows each airline as a point, where:
- X-axis = number of routes it operates from JFK
- Y-axis = number of unique destinations served

Hover over a point to see the airline code. This helps identify which carriers have broad vs. narrow networks out of JFK.
""")

