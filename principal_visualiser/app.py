import streamlit as st
import pandas as pd

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from principal_visualiser.mapper import fetch_companies_from_csv, plot_on_map
from principal_visualiser.constants import FILE_NAME

st.set_page_config(layout="wide")

st.image("principal_visualiser/logo.png", width=400)
st.title("Company Location Mapper")

st.markdown("""
    <style>
    .stTextInput, .stButton, .stDataFrame, .stMarkdown, .stSubheader {
        font-size: 32px;
    }
    .stTitle {
        font-size: 32px;
    }
    .stTextInput > div > div > input {
        width: 100% !important;
    }
    .main {
        zoom: 1.2;
    }
    .scrollable-table {
        overflow-y: auto;
        height: 400px;
        width: 100%;
    }
    table {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

def load_principal_names() -> list:
    """Load unique principal names from the CSV file."""
    csv_path = f'principal_visualiser/{FILE_NAME}'
    df = pd.read_csv(csv_path, encoding='utf-8')
    return df['principal_rep_name'].dropna().unique()

principal_names = load_principal_names()

principal_name = st.selectbox("Enter Principal Company Name", options=[""] + list(principal_names))

show_all_companies = st.button("Show All Companies")


if show_all_companies:
    principal_name = ""

if principal_name or show_all_companies:
    try:
        locations, principal_row = fetch_companies_from_csv(principal_name)

        st.markdown(f"""
        ## Principal Company Details  
        **Name:** {principal_row.iloc[0]['name']}  
        **FCA Number:** {principal_row.iloc[0]['regulatory_number']}  
        **Address:** {principal_row.iloc[0]['address']}  
        **Postcode:** {principal_row.iloc[0]['postcode']}  
        **Website:** {principal_row.iloc[0]['website']}  
        """, unsafe_allow_html=True)

        # Add a filter for AR type
        ar_type_filter = st.selectbox("Filter by AR Type", options=["All", "Introducer", "Full"])

        total_ars_count = len(locations)
        total_full_relationship_ars = sum(1 for loc in locations if loc.get('AR_relationship') == 'Full')
        total_introductory_relationship_ars = total_ars_count - total_full_relationship_ars
        
        # Filter locations based on AR type
        if ar_type_filter == "Introducer":
            locations = [loc for loc in locations if loc.get('AR_relationship') == 'Introducer']
        elif ar_type_filter == "Full":
            locations = [loc for loc in locations if loc.get('AR_relationship') == 'Full']
        
        if locations:
            # Calculate AR statistics
            total_ars = len(locations)
            full_relationship_ars = sum(1 for loc in locations if loc.get('AR_relationship') == 'Full')
            introductory_relationship_ars = total_ars - full_relationship_ars

            st.markdown(f"""
            ### Authorised Representatives  
            **Total ARs:** {total_ars_count}  
            **ARs with Full Relationship:** {total_full_relationship_ars}  
            **ARs with Introductory Relationship:** {total_introductory_relationship_ars}  
            """, unsafe_allow_html=True)

            # Plot the map
            plot_on_map(locations, "temp_map.html")
            try:
                with open("temp_map.html", "r") as file:
                    map_html = file.read()
                st.components.v1.html(map_html, height=1600, width=2500, scrolling=True)
            except FileNotFoundError:
                st.error("Map file not found.")

            # Display the table
            st.subheader("Appointed Representative Details")
            df = pd.DataFrame(locations)
            df = df[['name', 'regulatory_number', 'company_number', 'address', 'postcode', 'website', 'AR_relationship']]
            df['name'] = df['name'].apply(lambda x: f"<strong>{x}</strong>")
            df['website'] = df['website'].fillna('').apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>' if x else '')
            df = df.fillna('')
            st.markdown('<div class="scrollable-table">' + df.to_html(escape=False, index=False) + '</div>', unsafe_allow_html=True)

        else:
            st.warning("No locations found for this principal company name.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

else:
    try:
        with open("principal_visualiser/adviser_locations.html", "r") as file:
            default_map_html = file.read()
        st.components.v1.html(default_map_html, height=1600, width=2500, scrolling=True)
    except FileNotFoundError:
        st.error("Default map file not found.")

st.markdown("<div style='text-align: center; margin-top: 50px;'>Made with ❤️ in 2025 by AlphaLoops</div>", unsafe_allow_html=True)
