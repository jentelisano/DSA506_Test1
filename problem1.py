import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Problem 1
st.title("Problem 1 - JFK Flight Route Explorer")

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

# Dashboard Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌍 Route Map",
    "🏆 Top Destinations",
    "🥧 Domestic vs. International",
    "🛫 Airline Analysis",
    "🧠 Summary Insights"
])

with tab1:
    st.subheader("Global Map of Direct Routes from JFK")

    # Define JFK coordinates
    jfk_lat = 40.6413
    jfk_lon = -73.7781

    # Prepare flight paths
    flight_paths = jfk_routes[['Dst_IATA', 'City', 'Country', 'Latitude', 'Longitude']].dropna().copy()
    flight_paths['Src_Lat'] = jfk_lat
    flight_paths['Src_Lon'] = jfk_lon

    # Create map
    fig_map = go.Figure()

    for _, row in flight_paths.iterrows():
        fig_map.add_trace(go.Scattergeo(
            locationmode='country names',
            lon=[row['Src_Lon'], row['Longitude']],
            lat=[row['Src_Lat'], row['Latitude']],
            mode='lines',
            line=dict(width=1, color='blue'),
            opacity=0.3,
        ))

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
with tab2:
    st.subheader("Top 10 Destination Airports from JFK")

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
    ax.set_title('Top 10 Destination Airports from JFK (by Route Frequency)')
    ax.set_xlabel('Number of Unique Routes')
    ax.set_ylabel('Destination Airport')
    st.pyplot(fig_bar)

# Domestic vs. International
with tab3:
    st.subheader("Domestic vs. International Flights from JFK")

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
with tab4:
    st.subheader("Airline Route Frequency vs. Destination Reach from JFK")

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

with tab5:
    st.markdown("""
    ## ✈️ Summary Insights
    
    This exploratory analysis of flight route data from JFK International Airport reveals several key patterns:
    
    - **Global Reach**: JFK connects to over 150 destinations worldwide, with a strong concentration in Europe, Latin America, and major U.S. cities.
    - **Top Routes**: The most frequently served destinations include **London (LHR)**, **Paris (CDG)**, and **New Orleans (MSY)**—highlighting JFK's strategic blend of international and domestic routes.
    - **International Focus**: Approximately **65% of routes** are international, reinforcing JFK's role as a major global gateway.
    - **Airline Diversity**: The route map and frequency analysis show a wide range of airline operators. A few major carriers dominate in terms of both route volume and destination reach.
    - **Operational Footprint**: The airline scatterplot illustrates differences in scale and strategy—some carriers operate many routes to many places, while others focus on a small number of destinations.
    
    Taken together, the data highlights JFK as one of the most globally connected airports in the world, serving as a vital hub for both transatlantic and domestic air traffic.
    """)



