import streamlit as st
import requests
import bs4
import json
import pandas as pd
import pycountry
import plotly.express as px


def get_flag(country_name):
    try:
        country_code = pycountry.countries.lookup(country_name).alpha_2
        return ''.join([chr(0x1F1E6 + ord(char) - ord('A')) for char in country_code.upper()])
    except LookupError:
        return ""

def get_medal_data():
    response = requests.get("https://olympics.com/en/paris-2024/medals", headers={"User-Agent": "Mozilla/5.0"})
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    data = json.loads(soup.find("script", id="__NEXT_DATA__").string)
    table = data['props']['pageProps']['initialMedals']['medalStandings']['medalsTable']

    countries = []
    for row in table:
        medals = next(m for m in row["medalsNumber"] if m["type"] == "Total")
        country_name = row["description"]
        country_flag = get_flag(country_name)
        countries.append({
            "Country": f"{country_flag} {country_name}",
            "Gold": medals['gold'],
            "Silver": medals['silver'],
            "Bronze": medals['bronze'],
            "Total": medals['total']
        })

    return pd.DataFrame(countries)

def show_home_page():
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Welcome to the Olympics 2024 Paris </h1>
           
        </div>
        """,
        unsafe_allow_html=True
    )
    
 
    image_path = r"C:\Users\Ehsaan\Desktop\python project\2024_Summer_Olympics_logo.svg.png"  
    st.image(image_path, caption="Olympic Rings", use_column_width=True)

def show_medals_page():
    st.title("Olympic Medal Standings")

    st.markdown("""
    Live Medals Ranking
    """)

    medal_data = get_medal_data()

    # Ranking options
    ranking_criterion = st.selectbox(
        "Select ranking criteria:",
        ("Total", "Gold", "Silver", "Bronze")
    )

    # Sort data based on selected criterion
    sorted_data = medal_data.sort_values(by=ranking_criterion, ascending=False).reset_index(drop=True)

    # Add ranking column starting at 1
    sorted_data.index = sorted_data.index + 1
    sorted_data.index.name = 'Rank'

    # Display the data with full container width
    st.dataframe(sorted_data, use_container_width=True)

    # Plot a bar chart with Plotly
    st.subheader(f"Medal Counts by Country - Ranked by {ranking_criterion}")
    bar_chart = px.bar(
        sorted_data,
        x='Country',
        y=ranking_criterion,
        title=f"Medal Counts by Country - Ranked by {ranking_criterion}",
        labels={'Country': 'Country', ranking_criterion: 'Number of Medals'},
        width=1200,  
        height=500   
    )
    st.plotly_chart(bar_chart, use_container_width=True)

def main():
    # Sidebar for navigation
    page = st.sidebar.radio("Navigation", ["Home", "Medals"])

    if page == "Home":
        show_home_page()
    elif page == "Medals":
        show_medals_page()

if __name__ == '__main__':
    main()
