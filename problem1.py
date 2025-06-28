import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Page config
st.set_page_config(page_title="DSA506 Dashboard", layout="wide")

# Sidebar navigation
st.sidebar.title("📊 DSA506 Dashboards")
page = st.sidebar.radio("Select a problem:", ["Problem 1: JFK Flights", "Problem 2: University Dashboard", "Problem 3 (coming soon)"])

# =======================
# Problem 1
# =======================
if page == "Problem 1: JFK Flights":
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
        st.subheader("Top Destination Airports from JFK")
    
        # User selects how many destinations to display
        top_n = st.slider("Select number of top destinations to display:", min_value=3, max_value=20, value=10)
    
        # Filter top destinations
        top_dests = jfk_routes['Dst_IATA'].value_counts().head(top_n).reset_index()
        top_dests.columns = ['Dst_IATA', 'Flight_Count']
    
        # Merge to get location info
        top_dests = top_dests.merge(
            airports[['IATA', 'City', 'Country']],
            left_on='Dst_IATA', right_on='IATA',
            how='left'
        )
        top_dests['Label'] = top_dests['City'] + ', ' + top_dests['Country'] + ' (' + top_dests['Dst_IATA'] + ')'
    
        # Chart
        fig_bar, ax = plt.subplots(figsize=(10, 0.5 * top_n))
        sns.barplot(data=top_dests, y='Label', x='Flight_Count', palette='Blues_d', ax=ax)
        ax.set_title(f"Top {top_n} Destination Airports from JFK (by Route Frequency)")
        ax.set_xlabel('Number of Routes')
        ax.set_ylabel('Destination')
        st.pyplot(fig_bar)
    
    # Domestic vs. International
    with tab3:
        st.subheader("Domestic vs. International Flights")
    
        # Add domestic flag
        jfk_routes['is_domestic'] = jfk_routes['Country'] == 'United States'
    
        # Selection radio
        flight_filter = st.radio("Select view:", options=["All", "Domestic Only", "International Only"])
    
        if flight_filter == "Domestic Only":
            domestic = jfk_routes[jfk_routes['is_domestic']].dropna()
            city_counts = domestic['City'].value_counts().head(10).reset_index()
            city_counts.columns = ['City', 'Count']
    
            fig_domestic, ax = plt.subplots()
            ax.pie(city_counts['Count'], labels=city_counts['City'], autopct='%1.1f%%', startangle=90)
            ax.set_title("Top 10 Domestic Cities by Route Count")
            st.pyplot(fig_domestic)
    
        elif flight_filter == "International Only":
            international = jfk_routes[~jfk_routes['is_domestic']].dropna()
            country_counts = international['Country'].value_counts().head(10).reset_index()
            country_counts.columns = ['Country', 'Count']
    
            fig_international, ax = plt.subplots()
            ax.pie(country_counts['Count'], labels=country_counts['Country'], autopct='%1.1f%%', startangle=90)
            ax.set_title("Top 10 International Countries by Route Count")
            st.pyplot(fig_international)
    
        else:
            # Default view: Domestic vs. International %
            dom_int_counts = jfk_routes['is_domestic'].value_counts().reset_index()
            dom_int_counts.columns = ['is_domestic', 'count']
            dom_int_counts['label'] = dom_int_counts['is_domestic'].map({True: 'Domestic', False: 'International'})
    
            fig_all, ax = plt.subplots()
            ax.pie(dom_int_counts['count'], labels=dom_int_counts['label'], autopct='%1.1f%%', startangle=90, colors=['skyblue', 'salmon'])
            ax.set_title("All Flights: Domestic vs. International")
            st.pyplot(fig_all)
    
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

# =======================
# Problem 2 
# =======================
elif page == "Problem 2: University Dashboard":
    st.title("Problem 2 - University Admissions Dashboard")

    # Load the data
    df = pd.read_csv("university_student_dashboard_data.csv")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Admissions Overview",
        "🔁 Retention Trends",
        "😊 Student Satisfaction",
        "🏛️ Enrollment by Department",
        "📊 Spring vs. Fall Comparison",
        "🧠 Summary Insights"
    ])

    with tab1:
        st.subheader("Applications, Admissions, and Enrollments Over Time")
        df_grouped = df.groupby(['Year']).sum().reset_index()
        fig = px.line(df_grouped, x="Year", y=["Applications", "Admitted", "Enrolled"],
                      markers=True, title="Trends Over Time")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Retention Rate Trends")
        fig = px.line(df, x="Year", y="Retention Rate (%)", color="Term",
                      title="Retention Rate by Term")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Student Satisfaction Trends")
        fig = px.line(df, x="Year", y="Student Satisfaction (%)", color="Term",
                      title="Satisfaction Score by Term")
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Enrollment Breakdown by Department")
    
        department_cols = ["Engineering", "Business", "Arts", "Science"]
        valid_depts = [col for col in department_cols if col in df.columns]
    
        if valid_depts:
            long_df = df.melt(id_vars=["Year", "Term"], value_vars=valid_depts,
                              var_name="Department", value_name="Enrollment")
            fig = px.bar(long_df, x="Year", y="Enrollment", color="Department", barmode="group",
                         facet_col="Term", title="Department Enrollment per Term")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Department enrollment columns not found in dataset.")

    with tab5:
        st.subheader("Compare Spring vs. Fall")
        metric = st.selectbox("Select Metric", ["Applications", "Admitted", "Enrolled", "Retention Rate (%)", "Student Satisfaction (%)"])
        fig = px.line(df, x="Year", y=metric, color="Term", markers=True, title=f"{metric} by Term")
        st.plotly_chart(fig, use_container_width=True)

    with tab6:
        st.subheader("Key Insights")
        st.markdown("""
        - 📈 **Applications, admissions, and enrollments** have increased steadily over the years.
        - 🔁 **Retention rates** show improvement, particularly in Fall terms.
        - 😊 **Student satisfaction** remains higher in Fall compared to Spring.
        - 🏛️ **Engineering and Business** departments have the largest enrollments.
        - 📊 **Spring vs. Fall** trends show stronger metrics overall in Fall.
        """)

# =======================
# Problem 3 placeholder
# =======================
elif page == "Problem 3 (coming soon)":
    st.title("Problem 3")
    st.info("Coming soon!")





