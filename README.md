# Daily Splitter Tool (App 1)

A Streamlit web application that converts reservation-level data into **daily stay entries**.  
This tool is designed for property managers, hotels, serviced apartments, and operations teams who need to analyse revenue on a **per-night basis**.

Upload your Excel file → receive a clean Excel output with:
- Original reservation data  
- Daily-level split of each reservation  
- Revenue per night  
- One row per stay date  

No Python knowledge needed.

---

## 🚀 Features

### ✔ Split reservations into daily rows  
For each reservation, the app automatically generates all stay dates between **Arrival** and **Departure − 1 day**.

### ✔ Calculate revenue per night  
Each reservation’s:
- **Base Revenue**
- **Total Revenue**

is divided by the number of nights, giving a consistent nightly value.

### ✔ Clean Excel output  
The downloaded Excel file includes **two sheets**:
1. **Original Data**  
2. **Daily Split Data**

### ✔ Date formatting  
All dates are formatted as **dd-mm-yyyy**.

---

## 📦 How It Works

1. Upload your `.xlsx` reservation file.
2. The app:
   - Cleans column names
   - Converts Arrival/Departure/Booking Date to proper date format
   - Expands each booking into individual stay dates
   - Computes nightly revenue
3. You download a new Excel file with daily entries.

---

## 🧩 Required Columns  
Your input file must contain these columns:

- `Reservation Number`  
- `Apartment`  
- `Guest Name`  
- `Channel`  
- `Arrival`  
- `Departure`  
- `Booking Date`  
- `Nights`  
- `Base Revenue`  
- `Total Revenue`

---
### Install dependencies
