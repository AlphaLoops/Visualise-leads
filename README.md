# Company Location Mapper

This project visualizes company locations on a map using Streamlit and Folium. It allows users to view appointed representatives and principal companies.

## Setup

1. **Clone the repository:**

   ```bash
   git clone git@github.com:AlphaLoops/Visualise-leads.git
   cd Visualise-leads
   ```

2. **Install the required packages:**

   Make sure you have Python installed. Then, run:
   From inside the `Visualise-leads/principal_visualiser` directory:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   Start the Streamlit app by running:
   From inside the `Visualise-leads` directory:
   ```bash
   streamlit run principal_visualiser/app.py
   ```

## Files

- `app.py`: The main Streamlit application file.
- `mapper.py`: Contains functions to fetch company data and plot it on a map.
- `adviser_locations.html`: Static map file created by Fred, displayed when no company is selected.
- `company_leads_with_ars_with_introducers.csv`: CSV file containing company data.

## Usage

- **Enter Principal Company Name**: Use the dropdown to select a principal company and view its appointed representatives.
- **Show All Companies**: Click this button to view all companies on the map.
- **Default View**: If no company is selected, the app displays a static map created by Fred.

## Notes

- Ensure the `company_leads_with_ars_with_introducers.csv` file is in the `principal_visualiser` directory.
- Adjust file paths in the code if necessary.

