import streamlit as st
import pandas as pd
import requests
import re
import time
import urllib.parse
from datetime import datetime
from io import BytesIO
from duckduckgo_search import DDGS

# ==========================================
# GOOGLE API IMPORTS
# ==========================================
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
CLIENT_ID = st.secrets["google"]["client_id"]
CLIENT_SECRET = st.secrets["google"]["client_secret"]
REFRESH_TOKEN = st.secrets["google"]["refresh_token"]
MAPS_API_KEY = st.secrets["google"]["maps_api_key"]

DRIVE_FOLDER_ID = "13lWuf9Wls6gzQ4FRNRTJesYXaYmnu-jn"
OSM_USER_AGENT = "DineFinder_Scraper/4.0 (contact@dinefinder.com)"

# High-speed Overpass Endpoints
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

CITY_COORDS_DB = {
    "Patna": (25.5941, 85.1376), "Jaipur": (26.9124, 75.7873), "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946), "Gurgaon": (28.4595, 77.0266), "Delhi": (28.7041, 77.1025),
    "New Delhi": (28.6139, 77.2090), "Bhubaneswar": (20.2961, 85.8245), "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707), "Hyderabad": (17.3850, 78.4867), "Ahmedabad": (23.0225, 72.5714),
    "Pune": (18.5204, 73.8567), "Lucknow": (26.8467, 80.9462), "Chandigarh": (30.7333, 76.7794),
    "Bhopal": (23.2599, 77.4126), "Indore": (22.7196, 75.8577), "Noida": (28.5355, 77.3910)
}

# ALL INDIAN STATES & MAJOR CITIES
LOCATION_MATRIX = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Tirupati", "Kurnool", "Rajamahendravaram"],
    "Arunachal Pradesh": ["Itanagar", "Tawang", "Naharlagun", "Pasighat"],
    "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tezpur"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga", "Purnia", "Chhapra", "Begusarai", "Arrah"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Rajnandgaon", "Raigarh"],
    "Goa": ["Panaji", "Vasco da Gama", "Margao", "Mapusa", "Ponda"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Gandhinagar", "Junagadh"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Rohtak", "Hisar", "Karnal", "Sonipat", "Panchkula"],
    "Himachal Pradesh": ["Shimla", "Dharamshala", "Mandi", "Solan", "Manali", "Kullu"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar", "Hazaribagh"],
    "Karnataka": ["Bangalore", "Mysore", "Mangalore", "Hubli", "Belgaum", "Dharwad", "Gulbarga", "Davangere"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam", "Kannur"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar", "Rewa", "Satna"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Navi Mumbai", "Solapur", "Manmad", "Kolhapur", "Amravati"],
    "Manipur": ["Imphal", "Thoubal", "Kakching", "Ukhrul"],
    "Meghalaya": ["Shillong", "Tura", "Nongstoin", "Jowai"],
    "Mizoram": ["Aizawl", "Lunglei", "Saiha", "Champhai"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung", "Tuensang"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur", "Puri", "Balasore"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Pathankot"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer", "Alwar", "Bhilwara", "Sikar"],
    "Sikkim": ["Gangtok", "Namchi", "Geyzing", "Mangan"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tiruppur", "Erode", "Vellore", "Thoothukudi"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Ramagundam"],
    "Tripura": ["Agartala", "Udaipur", "Dharmanagar", "Kailashahar"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Noida", "Ghaziabad", "Agra", "Varanasi", "Meerut", "Prayagraj", "Gorakhpur", "Mathura", "Bareilly", "Aligarh", "Moradabad"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Roorkee", "Haldwani", "Rudrapur", "Rishikesh"],
    "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Siliguri", "Asansol", "Durgapur", "Kharagpur", "Burdwan", "Malda"],
    "Delhi": ["Delhi", "New Delhi", "Dwarka", "Rohini", "Janakpuri", "Vasant Kunj", "Laxmi Nagar", "Karol Bagh", "Connaught Place"],
    "Jammu and Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla", "Kathua"],
    "Chandigarh": ["Chandigarh"],
    "Puducherry": ["Pondicherry", "Oulgaret", "Karaikal", "Yanam", "Mahe"],
    "Andaman and Nicobar Islands": ["Port Blair"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Daman", "Diu", "Silvassa"],
    "Ladakh": ["Leh", "Kargil"],
    "Lakshadweep": ["Kavaratti", "Agatti"]
}
LOCATION_MATRIX = {state: sorted(cities) for state, cities in sorted(LOCATION_MATRIX.items())}

OSM_TAG_MAPPING = {
    "Restaurants": ('amenity', 'restaurant'),
    "Cafes": ('amenity', 'cafe'),
    "Fine Dining": ('amenity', 'restaurant'),
    "Fast Food": ('amenity', 'fast_food'),
    "Dhabas": ('amenity', 'restaurant'),
    "Bars and Pubs": ('amenity', 'bar'),
    "Hotels with restaurants": ('tourism', 'hotel')
}
SEARCH_CATEGORIES = list(OSM_TAG_MAPPING.keys())

# ==========================================
# STREAMLIT CONFIG & FUTURISTIC STYLES
# ==========================================
st.set_page_config(page_title="Dine Finder", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

if "raw_df" not in st.session_state:
    st.session_state.raw_df = None

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght=400;700;900&family=Inter:wght=300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #090c15; background-image: radial-gradient(circle at 15% 50%, rgba(20, 184, 166, 0.08), transparent 25%), radial-gradient(circle at 85% 30%, rgba(59, 130, 246, 0.08), transparent 25%); }
    .cyber-title { font-family: 'Orbitron', sans-serif; font-size: 3.8rem; font-weight: 900; text-align: center; text-transform: uppercase; letter-spacing: 4px; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #00f2fe 100%); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 3s linear infinite; margin-bottom: -10px; }
    .cyber-subtitle { text-align: center; color: #8b9bb4; font-family: 'Orbitron', sans-serif; font-size: 1rem; letter-spacing: 3px; margin-bottom: 40px; text-transform: uppercase; }
    @keyframes shine { to { background-position: 200% center; } }
    .glass-panel { background: rgba(17, 25, 40, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 30px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5); margin-bottom: 25px; }
    .stButton>button { background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%) !important; color: white !important; font-family: 'Orbitron', sans-serif !important; font-weight: 700 !important; letter-spacing: 1px; border-radius: 8px !important; border: 1px solid rgba(255,255,255,0.2) !important; padding: 12px 28px !important; box-shadow: 0 0 15px rgba(37, 99, 235, 0.4) !important; transition: all 0.3s ease !important; width: 100%; }
    .stButton>button:hover { box-shadow: 0 0 25px rgba(14, 165, 233, 0.7) !important; transform: translateY(-2px) !important; border: 1px solid rgba(255,255,255,0.5) !important; }
    hr { border: 0; height: 1px; background: linear-gradient(90deg, rgba(14,165,233,0) 0%, rgba(14,165,233,0.8) 50%, rgba(14,165,233,0) 100%); margin: 30px 0; }
    .status-badge { display: inline-block; padding: 5px 12px; border-radius: 20px; background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; color: #10b981; font-weight: 600; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS & DRIVE SYSTEM 
# ==========================================
@st.cache_resource
def connect_google_drive():
    try:
        creds = Credentials(None, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        return build("drive", "v3", credentials=creds)
    except Exception: return None

def fetch_vault_history(service, folder_id):
    try:
        query = f"'{folder_id}' in parents and trashed=false and mimeType='text/csv'"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name, modifiedTime, webViewLink)', orderBy='modifiedTime desc').execute()
        return results.get('files', [])
    except Exception: return []

def update_or_create_drive_file(service, new_df, city_name, folder_id, engine_type):
    file_name = f"leads_{engine_type}_{city_name}.csv" 
    try:
        query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if items:
            file_id = items[0]['id']
            request = service.files().get_media(fileId=file_id)
            downloaded = BytesIO()
            downloader = MediaIoBaseDownload(downloaded, request)
            done = False
            while not done: status, done = downloader.next_chunk()
            downloaded.seek(0)
            existing_df = pd.read_csv(downloaded)
            
            merged_df = pd.concat([existing_df, new_df], ignore_index=True)
            merged_df['temp_name'] = merged_df['Business Name'].astype(str).str.strip().str.lower()
            merged_df.drop_duplicates(subset=["temp_name"], keep='last', inplace=True)
            merged_df.drop(columns=['temp_name'], inplace=True)
            
            csv_data = merged_df.to_csv(index=False).encode('utf-8')
            media = MediaIoBaseUpload(BytesIO(csv_data), mimetype='text/csv', resumable=True)
            service.files().update(fileId=file_id, media_body=media).execute()
            return f"Updated! Total leads in {file_name}: {len(merged_df)}"
        else:
            new_df['temp_name'] = new_df['Business Name'].astype(str).str.strip().str.lower()
            new_df.drop_duplicates(subset=["temp_name"], keep='last', inplace=True)
            new_df.drop(columns=['temp_name'], inplace=True)
            
            csv_data = new_df.to_csv(index=False).encode('utf-8')
            media = MediaIoBaseUpload(BytesIO(csv_data), mimetype='text/csv', resumable=True)
            file_metadata = {'name': file_name, 'parents': [folder_id]}
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return f"Created new file: {file_name}!"
    except Exception as e:
        st.error(f"Drive Sync Error: {str(e)}")
        return None

def format_whatsapp_link(phone_str):
    if phone_str == "N/A": return "N/A"
    clean_num = re.sub(r'\D', '', phone_str)
    if len(clean_num) == 10: clean_num = "91" + clean_num
    elif len(clean_num) > 10 and clean_num.startswith("0"): clean_num = "91" + clean_num[1:]
    return f"https://wa.me/{clean_num}"

def backup_web_scraper(business_name, location):
    phone = "N/A"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f'{business_name} {location} contact number', max_results=2))
        page_text = " ".join([res.get('body', '') + " " + res.get('href', '') for res in results])
        patterns = [r'\+91[\-\s]?[6-9]\d{2}[\-\s]?\d{3}[\-\s]?\d{4}', r'\+91\s?\d{10}', r'\b[6-9]\d{2}[\-\s]?\d{3}[\-\s]?\d{4}\b', r'\b0?[6-9]\d{9}\b']
        for p in patterns:
            match = re.search(p, page_text)
            if match:
                phone = match.group(0).strip()
                break
    except Exception: pass
    return phone

# ==========================================
# CORE ENGINES: GOOGLE PLACES & OSM FREE
# ==========================================
def fetch_from_google_places(city, state, selected_categories, max_leads):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": MAPS_API_KEY, "X-Goog-FieldMask": "places.displayName.text,places.formattedAddress,places.nationalPhoneNumber,places.googleMapsUri,nextPageToken"}
    all_records = []
    progress_text = "Establishing uplink to Google API..."
    my_bar = st.progress(0, text=progress_text)
    total_cats = len(selected_categories)

    for i, category in enumerate(selected_categories):
        if len(all_records) >= max_leads: break
        my_bar.progress((i) / total_cats, text=f"Scanning Sector: {category}...")
        payload = {"textQuery": f"{category} in {city}, {state}, India", "languageCode": "en"}
        page_token = ""
        while True:
            if page_token: payload["pageToken"] = page_token
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200: 
                st.error(f"🔴 Google API Error Code: {response.status_code}\nDetails: {response.text}")
                break 
            data = response.json()
            for place in data.get("places", []):
                phone = place.get("nationalPhoneNumber", "N/A")
                if phone == "N/A": continue
                all_records.append({
                    "Business Name": place.get("displayName", {}).get("text", "Unknown"),
                    "Category": category, "Address": place.get("formattedAddress", "N/A"),
                    "Phone": phone, "WhatsApp": format_whatsapp_link(phone),
                    "Google Maps Link": place.get("googleMapsUri", "N/A")
                })
                if len(all_records) >= max_leads: break
            if len(all_records) >= max_leads: break
            page_token = data.get("nextPageToken")
            if not page_token: break
            time.sleep(1)
    my_bar.empty()
    return all_records

def fetch_from_osm_bulk(city, state, selected_categories, max_leads):
    osm_city_translation = {"Gurugram": "Gurgaon", "New Delhi": "New Delhi", "Delhi": "Delhi", "Mumbai City": "Mumbai", "Patna": "Patna"}
    search_city_name = osm_city_translation.get(city, city)
    
    lookup_name = search_city_name.replace(" City", "").strip()
    lat, lon = CITY_COORDS_DB.get(lookup_name, (None, None))
    
    # Auto-fetch coordinates if not in DB
    if not lat:
        try:
            res = requests.get(f"https://nominatim.openstreetmap.org/search?city={city}&state={state}&country=India&format=json&limit=1", headers={"User-Agent": OSM_USER_AGENT}, timeout=10)
            if res.status_code == 200 and res.json():
                lat, lon = float(res.json()[0]['lat']), float(res.json()[0]['lon'])
        except Exception: pass

    unique_tags = list(set([OSM_TAG_MAPPING[c] for c in selected_categories if c in OSM_TAG_MAPPING]))
    radius = 25000 # 25km radius
    
    # 🔥 SUPER OPTIMIZED OVERPASS QUERY (nwr = node, way, relation combined) - Prevent Timeouts
    if lat and lon:
        query_parts = "".join([f'nwr["{k}"="{v}"](around:{radius},{lat},{lon});' for k, v in unique_tags])
        query = f'[out:json][timeout:180];({query_parts});out center;'
    else:
        query_parts = "".join([f'nwr["{k}"="{v}"](area.searchArea);' for k, v in unique_tags])
        query = f'[out:json][timeout:180];area["name"="{search_city_name}"]->.searchArea;({query_parts});out center;'

    osm_fetched_elements = []
    last_error_msg = "Unknown Error"
    
    for url in OVERPASS_ENDPOINTS:
        try:
            res = requests.post(url, data={"data": query}, headers={"User-Agent": OSM_USER_AGENT}, timeout=90)
            if res.status_code == 200:
                data = res.json()
                if data.get("elements"):
                    osm_fetched_elements = data.get("elements", [])
                    break
                else: last_error_msg = f"No data found in {city}."
            elif res.status_code == 429: 
                last_error_msg = "OSM Server Rate Limited. Too many requests."
                time.sleep(2)
            else: last_error_msg = f"OSM Error {res.status_code}"
        except Exception as e:
            last_error_msg = f"Timeout/Connection Error: {str(e)}"
            continue

    if not osm_fetched_elements:
        st.error(f"🔴 **OSM ENGINE FAILED:** {last_error_msg}\n\n*Try selecting fewer 'Target Sectors' (e.g. only Restaurants) or use Google API Pro.*")
        return []

    osm_fetched_elements = osm_fetched_elements[:max_leads]
    all_records = []
    my_bar = st.progress(0, text="Establishing uplink to OSM Servers...")
    total_elements = len(osm_fetched_elements)

    for i, el in enumerate(osm_fetched_elements):
        my_bar.progress((i + 1) / total_elements, text=f"Processing target {i+1} of {total_elements}...")
        tags = el.get("tags", {})
        cat_type = tags.get("amenity", tags.get("tourism", "Establishment")).title()
        b_name = tags.get("name", f"Premium {cat_type}")
        
        phone = tags.get("phone", "N/A")
        if phone == "N/A" and total_elements <= 30: 
            phone = backup_web_scraper(b_name, city)
            
        search_query = urllib.parse.quote_plus(f"{b_name} {city}")
        all_records.append({
            "Business Name": b_name, "Category": cat_type,
            "Address": tags.get("addr:street", f"Local Area, {city}"),
            "Phone": phone, "WhatsApp": format_whatsapp_link(phone),
            "Google Maps Link": f"https://www.google.com/search?q={search_query}"
        })
    my_bar.empty()
    return all_records

# ==========================================
# UI & APPLICATION LAYOUT
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='font-family: Orbitron; color: #00f2fe;'>☁️ CLOUD VAULT</h2>", unsafe_allow_html=True)
    drive_service = connect_google_drive()
    if drive_service: 
        st.markdown("<div class='status-badge'>🟢 SYSTEM ONLINE</div><br><br>", unsafe_allow_html=True)
        st.link_button("📂 ACCESS ROOT DIRECTORY", f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}", use_container_width=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#8b9bb4;'>📜 DATA ARCHIVES</h4>", unsafe_allow_html=True)
        recent_files = fetch_vault_history(drive_service, DRIVE_FOLDER_ID)
        if recent_files:
            file_dict = {f['name']: f.get('webViewLink', f"https://drive.google.com/file/d/{f['id']}/view") for f in recent_files}
            selected_file = st.selectbox("Select Archive File:", ["-- Initialize File --"] + list(file_dict.keys()))
            if selected_file != "-- Initialize File --":
                st.link_button(label=f"👁️ DECRYPT {selected_file}", url=file_dict[selected_file], use_container_width=True)
        else: st.info("Archive empty. No logs found.")
    else: st.markdown("<div class='status-badge' style='color:#ef4444; border-color:#ef4444; background:rgba(239, 68, 68, 0.1)'>🔴 SYSTEM OFFLINE</div>", unsafe_allow_html=True)

st.markdown("<div class='cyber-title'>DINE FINDER</div>", unsafe_allow_html=True)
st.markdown("<div class='cyber-subtitle'>Restaurant, Cafe & Dhaba Search Bot // v1.0</div>", unsafe_allow_html=True)

st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#00f2fe; margin-bottom: 20px;'>⚙️ ENGINE PROTOCOL</h4>", unsafe_allow_html=True)
scraper_engine = st.radio("Select Scraper Engine Mode", ["Google API Pro (Highly Accurate + Auto-Phone)", "OSM Free Bulk Engine (Huge Number of Leads + Verification Link)"], horizontal=True, label_visibility="collapsed")
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#00f2fe; margin-bottom: 20px;'>📍 TARGET COORDINATES</h4>", unsafe_allow_html=True)

ctrl_c1, ctrl_c2 = st.columns([1, 1])
with ctrl_c1: selected_state = st.selectbox("Select State", ["Select State..."] + list(LOCATION_MATRIX.keys()))
with ctrl_c2:
    city_options = ["Select City..."] + LOCATION_MATRIX[selected_state] if selected_state != "Select State..." else ["Select City..."]
    selected_city = st.selectbox("Target City", city_options)

st.markdown("<br>", unsafe_allow_html=True)
selected_categories = st.multiselect("🏷️ TARGET SECTORS", SEARCH_CATEGORIES, default=["Restaurants"])
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#00f2fe;'>⚡ EXTRACTION VOLUME</h4>", unsafe_allow_html=True)
max_leads = st.slider("Target Lead Count", min_value=10, max_value=500, value=100, step=10, label_visibility="collapsed")
st.markdown("</div>", unsafe_allow_html=True)

if st.button("🚀 INITIATE EXTRACTION PROTOCOL"):
    if selected_state == "Select State..." or selected_city == "Select City...":
        st.error("⚠️ Error: Target coordinates not set. Please select a valid State and City.")
    elif not selected_categories:
        st.warning("⚠️ Error: No target sectors selected.")
    else:
        engine_key = "google" if "Google" in scraper_engine else "osm"
        st.session_state.raw_df = None # Reset previous data
        
        with st.spinner("Initializing selected scraper engine pipeline..."):
            if engine_key == "google":
                all_records = fetch_from_google_places(selected_city, selected_state, selected_categories, max_leads)
            else:
                all_records = fetch_from_osm_bulk(selected_city, selected_state, selected_categories, max_leads)
            
            if all_records:
                df = pd.DataFrame(all_records)
                st.session_state.raw_df = df.drop_duplicates(subset=["Business Name"]).reset_index(drop=True)
                st.session_state.current_city = selected_city
                st.success(f"✅ Extraction Successful: Retrieved {len(st.session_state.raw_df)} high-value targets.")
                
                if drive_service:
                    with st.spinner(f"Syncing data matrix to secure cloud vault..."):
                        res = update_or_create_drive_file(drive_service, st.session_state.raw_df, selected_city, DRIVE_FOLDER_ID, engine_key)
                        if res: st.success(f"☁️ Vault Sync Complete: {res}")
            else:
                # If all_records is empty, we just do nothing here. The error is already handled inside the functions!
                pass 

if st.session_state.raw_df is not None and not st.session_state.raw_df.empty:
    display_df = st.session_state.raw_df
    engine_key = "google" if "Google" in scraper_engine else "osm"
    
    st.markdown("<br><h3 style='color:#92FE9D; font-family:Orbitron;'>📊 ACQUIRED TARGET DATA</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])
    with col1: st.download_button("💾 DOWNLOAD OFFLINE BACKUP", display_df.to_csv(index=False).encode('utf-8'), f"backup_{engine_key}_{st.session_state.current_city}.csv", "text/csv")
    
    st.markdown("<div style='border: 1px solid rgba(0, 242, 254, 0.3); border-radius: 12px; overflow: hidden; box-shadow: 0 0 20px rgba(0,242,254,0.1); padding: 5px; background: rgba(0,0,0,0.4);'>", unsafe_allow_html=True)
    st.dataframe(display_df, use_container_width=True, height=500, hide_index=True, column_config={"WhatsApp": st.column_config.LinkColumn("💬 COMMS", display_text="Open WhatsApp"), "Google Maps Link": st.column_config.LinkColumn("📍 INTEL", display_text="View Intel/Map")})
    st.markdown("</div>", unsafe_allow_html=True)