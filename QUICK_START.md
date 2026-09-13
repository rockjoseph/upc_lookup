# 🧴 BBW UPC Scanner - Quick Start Guide

Welcome to your Bath & Body Works Price Tracker app! This guide will get you up and running in 5 minutes.

## What This App Does

- **Scan UPC Codes** - Enter any Bath & Body Works product UPC barcode
- **Get Product Details** - Automatically fetches product name, price, image, and availability  
- **Track Prices** - Build a spreadsheet of products you're monitoring
- **Export to Excel** - Download your price-tracking data as an `.xlsx` file you can edit anywhere

## Prerequisites

Make sure you have:
- **Python 3.10+** ([Download here](https://www.python.org/downloads/))
- **Node.js 18+** ([Download here](https://nodejs.org/))
- **A web browser** (Chrome, Firefox, Safari, Edge)

## Installation (First Time Only)

### 1️⃣ Install Backend Dependencies

Open your terminal and navigate to the project folder:

```bash
cd backend
python3 -m venv .venv

# On Windows:
# .venv\Scripts\activate

# On Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2️⃣ Install Frontend Dependencies

In a **new terminal** window, from the project root:

```bash
cd frontend
npm install
```

## Running the App

### Terminal 1: Start the Backend API

```bash
cd backend
source .venv/bin/activate  # Or: .venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

✨ **API docs available at:** http://localhost:8000/docs

### Terminal 2: Start the Frontend (in a new window)

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v... ready in ... ms

➜  Local:   http://localhost:5173/
```

### 3️⃣ Open the App

🎉 **Open your browser to:** http://localhost:5173

You're all set!

---

## How to Use the App

### Scanning a UPC Code

1. **Look at a Bath & Body Works product** and find the barcode (usually on the back or bottom)
2. **Enter the UPC number** in the search field (should be 8-14 digits)
3. **Select "UPC / Barcode"** from the dropdown (or leave it on "Auto-detect")
4. **Click "Search"**
5. **See the product details** - name, price, image, and in-stock status
6. **Click "Add / Update in Excel"** to save it to your spreadsheet

### Alternative Search Methods

- **By Product URL** - Copy and paste a full product link from bathandbodyworks.com
- **By Name/Keyword** - Type the product name (e.g., "Mahogany Teakwood")

### Working with Your Excel Spreadsheet

#### Creating a New Spreadsheet
- A blank spreadsheet is created automatically when you open the app
- Or click **"New Spreadsheet"** to start fresh

#### Using an Existing Spreadsheet
- Click **"Upload .xlsx"** and select your existing Bath & Body Works price-tracking sheet
- All matching products will be found by SKU or product name and updated with new prices
- New products you search for will be appended to the bottom

#### Downloading Your Data
- Click **"Download Updated Excel"** to save your spreadsheet
- Use Excel, Google Sheets, or any spreadsheet app to view or further edit it

---

## Understanding the Product Card

When you search for a product, you'll see:

```
┌─────────────────────────────────────────────┐
│ [Product Image]    Product Name             │
│                    SKU: XXXXX              │
│                    Price: $XX.XX            │
│                    Original: $XX.XX         │
│                    🏷️ Promotion Tag        │
│                    🟢 In Stock / Out       │
│                    [Add/Update] [View URL] │
└─────────────────────────────────────────────┘
```

---

## Tips & Tricks

### 🎯 Pro Tips

1. **Exact UPC Matches** - If a UPC returns multiple results, the app will show you a list to pick from
2. **Price History** - Download your spreadsheet regularly to track price changes over time
3. **Bulk Import** - Upload your existing Excel spreadsheet to continue tracking where you left off
4. **Real-Time Sync** - Each product is fetched fresh from Bath & Body Works' site, so prices are always current

### ⚡ Performance Notes

- Searches are **rate-limited** to be polite to Bath & Body Works' servers (2.5 seconds minimum between requests)
- Recent searches are **cached** for 5 minutes, so searching the same product again is instant
- If a page is slow to load, the app will automatically try JavaScript rendering as a fallback

---

## Troubleshooting

### "No matching product found"
- Double-check the UPC code - make sure you have the correct 8-14 digit number
- Try searching by product name instead
- Visit bathandbodyworks.com directly to find the product URL and search by that

### "Failed to fetch / Connection error"
- Make sure the **backend is running** (check Terminal 1)
- Check that you're using `http://localhost:8000` (not https)
- Try refreshing the page

### "Multiple matches found"
- The app sometimes finds 2-8 possible products for a UPC or keyword
- Click on the one you want from the list
- This is normal behavior for search-based lookups

### Excel file won't upload
- Make sure it's a `.xlsx` file (Excel format, not CSV or Google Sheets export)
- Verify the file has a sheet named `Prices` with columns: SKU/UPC, Product Name, Original Price, Current Sale Price, Promo Deal, Last Checked Date/Time, Product URL

---

## What's Next?

### Commands You'll Use Frequently

**Start the app:**
```bash
# Terminal 1: Backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

**Stop the app:**
- Press `Ctrl+C` in both terminals

**Update dependencies** (if needed):
```bash
# Backend
pip install -r requirements.txt --upgrade

# Frontend
npm update
```

---

## Architecture Overview

Your app is built with:
- **Backend**: Python + FastAPI (handles product scraping and Excel management)
- **Frontend**: React + Vite + Tailwind CSS (fast, responsive UI)
- **Data**: Openpyxl (reads/writes Excel files)
- **Scraping**: BeautifulSoup + requests (fetches product data from Bath & Body Works)

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for technical details.

---

## Questions or Issues?

Check the logs in your terminal windows for detailed error messages. The backend logs all requests and errors, which helps debug any issues.

**Happy tracking!** 🧴✨
