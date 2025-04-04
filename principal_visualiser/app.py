import streamlit as st
import pandas as pd

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from principal_visualiser.mapper import fetch_companies_from_csv, plot_on_map

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
    csv_path = 'principal_visualiser/company_leads_with_ars.csv'
    df = pd.read_csv(csv_path, encoding='utf-8')
    return df['principal_rep_name'].dropna().unique()

principal_names = load_principal_names()

principal_name = st.selectbox("Enter Principal Company Name", options=[""] + list(principal_names))

show_all_companies = st.button("Show All Companies")

if show_all_companies:
    principal_name = ""

if principal_name:
    try:
        locations = fetch_companies_from_csv(principal_name)
        
        if locations:
            principal_reg_num = locations[0]['regulatory_number']
            
            st.markdown(f"""
            ## Appointed Representatives
            **Principal Company:** {principal_name}  
            **Principal FCA Number:** {principal_reg_num}
            """, unsafe_allow_html=True)
            
            plot_on_map(locations, "temp_map.html")
            try:
                with open("temp_map.html", "r") as file:
                    map_html = file.read()
                st.components.v1.html(map_html, height=1600, width=2500, scrolling=True)
            except FileNotFoundError:
                st.error("Map file not found.")

            st.subheader("Appointed Representative Details")
            df = pd.DataFrame(locations)
            df = df[['name', 'regulatory_number', 'company_number', 'address', 'postcode', 'website']]
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
        with open("/Users/pakhibamdev/work/dec_2024/distro/alphaloops-distro/principal_visualiser/adviser_locations.html", "r") as file:
            default_map_html = file.read()
        st.components.v1.html(default_map_html, height=1600, width=2500, scrolling=True)
    except FileNotFoundError:
        st.error("Default map file not found.")

st.markdown("<div style='text-align: center; margin-top: 50px;'>Made with ❤️ in 2025 by AlphaLoops</div>", unsafe_allow_html=True)
