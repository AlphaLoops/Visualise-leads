import folium
import pandas as pd
import pgeocode
import os

# Geo lookup for UK postcodes
geo = pgeocode.Nominatim("GB")

def fetch_companies_from_csv(principal_name: str = None) -> list:
    """Fetch companies from CSV, optionally filtering by principal name."""
    csv_path = os.path.join(os.path.dirname(__file__), 'company_leads_with_ars.csv')
    
    # Read the CSV file using pandas
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    # Filter out rows without postcodes
    df = df[df['postcode'].notna() & df['postcode'].str.strip().astype(bool)]
    
    # Filter by principal name if provided
    if principal_name:
        # Find all companies where this principal is listed as their representative
        ar_companies = df[df['principal_rep_name'] == principal_name]
        
        if not ar_companies.empty:
            # Mark AR companies
            ar_companies['is_principal'] = False
            
            # Find the principal company
            principal_company = df[df['name'] == principal_name]
            if not principal_company.empty:
                principal_company['is_principal'] = True
                # Combine principal and AR companies
                df = pd.concat([principal_company, ar_companies])
            else:
                df = ar_companies  # Only ARs if no principal found
        else:
            df = pd.DataFrame()  # No ARs found, return empty DataFrame
    
    # Process locations
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
        }
        locations.append(location_data)
    
    return locations

def plot_on_map(locations: list, filename: str = "company_locations_map.html", highlight_index: int = None) -> None:
    """Plot companies on a map and save to an HTML file."""
    uk_center = [54.7023545, -3.2765753]
    m = folium.Map(location=uk_center, zoom_start=6)

    for loc in locations:
        # Handle missing website URL
        website = str(loc.get('website', '')).strip()
        website_link = f'<a href="{website}" target="_blank">{website}</a>' if website and website != 'nan' else ''

        # Customize popup with detailed information and larger font size
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
        
        # Determine color based on company type
        color = "red" if loc['is_principal'] else "blue"
        fillColor = "lightcoral" if loc['is_principal'] else "#4682B4"
        
        folium.CircleMarker(
            location=[loc["lat"], loc["lng"]],
            radius=8,  # Increased radius for larger dots
            popup=popup,
            color=color,
            fill=True,
            fillColor=fillColor,
            fill_opacity=1.0,  # Solid color
            weight=3,  # Stroke weight for the boundary
        ).add_to(m)

    m.save(filename)
    print(f"[✓] Map saved to {filename} with {len(locations)} companies plotted.")