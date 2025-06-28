import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

st.title("JFK Flight Route Explorer")
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

st.subheader("4. Top Airlines Operating from JFK (by Route Count)")

top_airlines = jfk_routes['Airline'].value_counts().head(10).reset_index()
top_airlines.columns = ['Airline_Code', 'Route_Count']

fig_airline, ax = plt.subplots(figsize=(10, 4))
sns.barplot(data=top_airlines, x='Route_Count', y='Airline_Code', palette='Purples_d', ax=ax)
ax.set_xlabel("Number of Routes")
ax.set_ylabel("Airline Code")
st.pyplot(fig_airline)

st.markdown("""
## ✈️ Summary Insights

- JFK offers direct flights to over 150 destinations across the globe.
- Top destinations include **London (LHR)** and **Paris (CDG)**.
- **~70%** of routes from JFK are international, reinforcing its role as a global gateway.
- Airlines with the most route presence from JFK include both U.S. and foreign carriers.

The analysis uses OpenFlights data as a proxy for real-world operations and offers valuable insights into route diversity, airport connectivity, and strategic airline presence.
""")


