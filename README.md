# ⚡ Dine Finder: Advanced Lead Extraction Bot

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-Places_API-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**Dine Finder** is a high-speed, automated data extraction web application designed to scout, map, and consolidate leads for restaurants, cafes, fine-dining spots, and other hospitality sectors across major Indian cities. 

Developed during my mid-internship milestone at **Iota Design and Innovation Lab Pvt. Ltd.**, this tool solves real-world data engineering challenges like server timeouts, rate limits, and seamless cloud data syncing.

---

## 🚀 Key Features

* **Dual Extraction Engines:** * **Google API Pro:** Utilizes the Google Places API (New) for highly accurate data, including verified phone numbers and precise map links.
* **OSM Free Bulk Engine:** Leverages highly optimized `nwr` (Node, Way, Relation) queries on the Overpass API for extracting bulk datasets without hitting strict rate limits.
* **☁️ Cloud Vault Sync:** Automatically uploads, merges, and de-duplicates newly scraped data into a secure Google Drive CSV database.
* **📱 Comms Integration:** Auto-formats extracted phone numbers into direct 1-click WhatsApp chat links.
* **🛡️ Smart Error Handling:** Built-in safeguards against 504 Gateway Timeouts, automated request cooling, and IP rate limiting.
* **🖥️ Futuristic UI:** A responsive, cyber-themed user interface built entirely with Streamlit.

---

## 🛠️ Tech Stack

* **Backend & Logic:** Python 3
* **Frontend UI:** Streamlit
* **Data Processing:** Pandas
* **APIs Used:** * Google Places API (New)
  * Google Drive API v3 (for Cloud Sync)
  * OpenStreetMap (OSM) Overpass API
* **Other Libraries:** `requests`, `duckduckgo_search`, `google-api-python-client`

---

## ⚙️ Local Installation & Setup

**1. Clone the repository:**
```bash
# Clone this repository to your local machine
git clone [https://github.com/rajeevvv018/dine-finder.git](https://github.com/rajeevvv018/dine-finder.git)
cd dine-finder

**2. Install the required dependencies:**
pip install -r requirements.txt

**3. Configure Environment Secrets:**
Create a folder named .streamlit in the root directory and add a file named secrets.toml. Add your API keys securely:

Ini, TOML
[google]
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
refresh_token = "YOUR_DRIVE_REFRESH_TOKEN"
maps_api_key = "YOUR_PLACES_API_KEY"

**4. Boot up the Application:**
Run the following command in your terminal or use the provided start.bat script:
streamlit run streamlit_app.py
