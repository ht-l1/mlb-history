import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

DB_PATH = "mlb_history.db"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    stats = pd.read_sql_query("SELECT * FROM stats", conn)
    events = pd.read_sql_query("SELECT * FROM events", conn)
    years = pd.read_sql_query("SELECT * FROM years", conn)
    conn.close()
    return stats, events, years

def main():
    st.title("MLB History Dashboard")
    st.markdown("""
        **Welcome to the MLB History Dashboard**  
        Use the sidebar to select a year and league to view home run leader statistics and MLB events.  
        - **Year**: Choose a season from 2020 to 2025.  
        - **League**: Filter by American League, National League, or both.  
        - **Event Type**: Select an event type (e.g., World Series) to view specific events.  
        The charts and tables display home run leaders and event details for the selected filters.
    """)


    stats, events, years = load_data()

    st.sidebar.header("Filter Options")
    selected_year = st.sidebar.selectbox("Select Year", sorted(stats['year'].unique(), reverse=True))
    selected_league = st.sidebar.radio("Select League", ["All", "American League", "National League"])

    filtered_stats = stats[stats['year'] == selected_year]
    if selected_league != "All":
        filtered_stats = filtered_stats[filtered_stats['league'] == selected_league]

    st.subheader("Home Run Trends")
    st.markdown("This chart shows the average home run leader values for American and National Leagues from 2020 to 2025.")
    line_data = stats.groupby(['year', 'league'])['leader_value'].mean().reset_index()
    chart = alt.Chart(line_data).mark_line(point=True).encode(
        x='year:O',
        y='leader_value:Q',
        color='league:N',
        tooltip=['year', 'league', 'leader_value']
    ).properties(width=700, height=400)
    st.altair_chart(chart)


    st.subheader(f"Home Run Leaders ({selected_year})")
    st.markdown("This table displays the top home run leader values for the selected year and league, along with the number of teams.")
    st.dataframe(filtered_stats)

    st.subheader(f"Home Run Leaders Comparison ({selected_year})")
    bar_data = filtered_stats[['league', 'leader_value']].copy()
    bar_chart = alt.Chart(bar_data).mark_bar().encode(
        x='league:N',
        y='leader_value:Q',
        color=alt.Color('league:N', scale=alt.Scale(domain=['American League', 'National League'], range=['#1f77b4', '#ff7f0e'])),
        tooltip=['league', 'leader_value']
    ).properties(width=300, height=300)
    st.altair_chart(bar_chart)

    st.subheader("MLB Events")
    st.markdown("This table lists MLB events (e.g., World Series, All-Star Game, Season Start) for the selected year and event type, including their descriptions and categories.")
    selected_event_type = st.selectbox("Event Type", sorted(events['event_type'].unique()))
    event_filtered = events[(events['event_type'] == selected_event_type) & (events['year'] == selected_year)]
    st.write(event_filtered)

    st.subheader(f"Event Category Distribution ({selected_year})")
    st.markdown("This pie chart shows the distribution of MLB event categories (Championship, Exhibition, Regular Season) for the selected year, indicating the number of events in each category.")
    pie_data = events[events['year'] == selected_year].groupby('category').size().reset_index(name='count')
    pie_chart = alt.Chart(pie_data).mark_arc().encode(
        theta=alt.Theta(field='count', type='quantitative'),
        color=alt.Color(field='category', type='nominal', scale=alt.Scale(range=['#2ca02c', '#d62728', '#9467bd'])),
        tooltip=['category', 'count']
    ).properties(width=300, height=300)
    st.altair_chart(pie_chart)

    st.markdown("Built with Streamlit")

if __name__ == "__main__":
    main()