import folium
import pandas as pd
import pgeocode
import os

from principal_visualiser.constants import FILE_NAME

# Geo lookup for UK postcodes
geo = pgeocode.Nominatim("GB")

def fetch_companies_from_csv(principal_name: str = None) -> tuple[list, pd.DataFrame]:
    """
    Fetch companies from CSV.
    
    - Reads 'company_leads_with_ars_no_introducers.csv'.
    - Filters out rows with missing/empty postcodes.
    - Optionally filters by principal name.
    - Uses GPS coordinates or looks up by postcode.
    
    Args:
        principal_name (str, optional): Filter by principal name.
    
    Returns:
        tuple: List of location data, DataFrame of principal row.
    """
    csv_path = os.path.join(os.path.dirname(__file__), FILE_NAME)
    df = pd.read_csv(csv_path, encoding='utf-8')
    df = df[df['postcode'].notna() & df['postcode'].str.strip().astype(bool)]

    if principal_name:
        principal_row = df[df['name'] == principal_name]
        selected_rows = df[(df['principal_rep_name'] == principal_name)]
        df = selected_rows

    locations = []
    for _, company in df.iterrows():
        # Use provided GPS coordinates if available, otherwise look up from postcode
        if pd.notna(company['gps_latitude']) and pd.notna(company['gps_longitude']):
            lat = float(company['gps_latitude'])
            lng = float(company['gps_longitude'])
        else:
            # Look up coordinates from postcode
            try:
                postcode_info = geo.query_postal_code(company['postcode'])
                if not pd.isna(postcode_info['latitude']) and not pd.isna(postcode_info['longitude']):
                    lat = postcode_info['latitude']
                    lng = postcode_info['longitude']
                else:
                    continue  # Skip if no valid coordinates found
            except Exception as e:
                print(f"Error looking up postcode {company['postcode']}: {e}")
                continue
        
        location_data = {
            "name": company['name'],
            "postcode": company['postcode'],
            "lat": lat,
            "lng": lng,
            "regulatory_number": company['regulatory_number'],
            "principal_rep_name": company.get('principal_rep_name', ''),
            "principal_rep_reg_number": company.get('principal_rep_reg_number', ''),
            "is_principal": company.get('is_principal', False),
            "website": company.get('website', ''),
            "company_number": company.get('company_number', ''),
            "address": company.get('address', ''),
            "services": company.get('services', ''),
            "AR_relationship": company.get('AR_relationship', '')
        }
        locations.append(location_data)
    
    return locations, principal_row

import folium
import pandas as pd
import pgeocode
import os

from principal_visualiser.constants import FILE_NAME

# Geo lookup for UK postcodes
geo = pgeocode.Nominatim("GB")

def fetch_companies_from_csv(principal_name: str = None) -> tuple[list, pd.DataFrame]:
    csv_path = os.path.join(os.path.dirname(__file__), FILE_NAME)
    df = pd.read_csv(csv_path, encoding='utf-8')
    df = df[df['postcode'].notna() & df['postcode'].str.strip().astype(bool)]

    if principal_name:
        principal_row = df[df['name'] == principal_name]
        selected_rows = df[(df['principal_rep_name'] == principal_name)]
        df = selected_rows

    locations = []
    for _, company in df.iterrows():
        if pd.notna(company['gps_latitude']) and pd.notna(company['gps_longitude']):
            lat = float(company['gps_latitude'])
            lng = float(company['gps_longitude'])
        else:
            try:
                postcode_info = geo.query_postal_code(company['postcode'])
                if not pd.isna(postcode_info['latitude']) and not pd.isna(postcode_info['longitude']):
                    lat = postcode_info['latitude']
                    lng = postcode_info['longitude']
                else:
                    continue
            except Exception as e:
                print(f"Error looking up postcode {company['postcode']}: {e}")
                continue
        
        location_data = {
            "name": company['name'],
            "postcode": company['postcode'],
            "lat": lat,
            "lng": lng,
            "regulatory_number": company['regulatory_number'],
            "principal_rep_name": company.get('principal_rep_name', ''),
            "principal_rep_reg_number": company.get('principal_rep_reg_number', ''),
            "is_principal": company.get('is_principal', False),
            "website": company.get('website', ''),
            "company_number": company.get('company_number', ''),
            "address": company.get('address', ''),
            "services": company.get('services', ''),
            "AR_relationship": company.get('AR_relationship', '')
        }
        locations.append(location_data)
    
    return locations, principal_row

def plot_on_map(locations: list, filename: str = "company_locations_map.html", highlight_index: int = None) -> None:
    uk_center = [54.7023545, -3.2765753]
    m = folium.Map(location=uk_center, zoom_start=6)

    for loc in locations:
        website = str(loc.get('website', '')).strip()
        website_link = f'<a href="{website}" target="_blank">{website}</a>' if website and website != 'nan' else ''

        popup_html = f"""
        <div style="font-size: 18px; white-space: normal;">
            <strong>{loc['name']}</strong><br>
            FCA Number: {loc['regulatory_number']}<br>
            Company Number: {loc.get('company_number', 'N/A')}<br>
            Postcode: {loc['postcode']}<br>
            {website_link}
        </div>
        """
        popup = folium.Popup(folium.Html(popup_html, script=True), parse_html=True, max_width=300)
        
        # Determine color based on AR relationship
        if 'AR_relationship' in loc and loc['AR_relationship'] == 'Introducer':
            color = "darkorange"
            fillColor = "darkorange"
            fill_opacity = 0.8
        else:
            color = "blue"
            fillColor = "#4682B4"
            fill_opacity = 1.0
        
        folium.CircleMarker(
            location=[loc["lat"], loc["lng"]],
            radius=8,
            popup=popup,
            color=color,
            fill=True,
            fillColor=fillColor,
            fill_opacity=fill_opacity,
            weight=3,
        ).add_to(m)

    legend_html = """
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 180px; height: 110px; 
     background-color: white; z-index:9999; font-size:14px;
     border:2px solid grey; border-radius:5px;">
     &nbsp; <strong>AR Relationship Types</strong> <br>
     &nbsp; <i class="fa fa-circle" style="color:darkorange"></i>&nbsp; Introducer <br>
     &nbsp; <i class="fa fa-circle" style="color:blue"></i>&nbsp; Full <br>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(filename)
    print(f"[✓] Map saved to {filename} with {len(locations)} companies plotted.")