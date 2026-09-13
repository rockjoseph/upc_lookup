# 🚀 GET STARTED IN 5 MINUTES

Your **Bath & Body Works UPC Scanner** app is **100% ready to use**! Here's the fastest way to start:

---

## ✅ What You Have

Your app is **fully built** and includes:

- 📱 **UPC Code Scanning** - Enter barcode numbers directly
- 🖼️ **Product Images** - See what you're tracking
- 💰 **Price Tracking** - Monitor sales and promotions
- 📊 **Excel Export** - Download your data anytime

---

## ⚡ Quick Start (3 Steps)

### Step 1: Start the Backend

Open a terminal and run:

```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt  # only needed first time
uvicorn app.main:app --reload --port 8000
```

**You should see:**
```
Uvicorn running on http://127.0.0.1:8000
Application startup complete
```

### Step 2: Start the Frontend

Open a **new terminal** and run:

```bash
cd frontend
npm install  # only needed first time
npm run dev
```

**You should see:**
```
VITE v... ready in ... ms
➜ Local:   http://localhost:5173/
```

### Step 3: Open the App

🎉 Open your browser to: **http://localhost:5173**

---

## 🎯 Try It Out (2 Minutes)

### Scan a UPC Code

1. Find a Bath & Body Works product (or look up a product on their website)
2. Get the **UPC code** (the barcode number - 8-14 digits)
3. **Paste it** in the search box
4. Hit **Enter** or click **Search**
5. **See the product details** - name, price, image, availability
6. Click **"Add / Update in Excel"** to save it

### Example UPCs to Try

If you want to test without a physical product:

- `031965005612` - Mahogany Teakwood
- `079655019107` - Warm Vanilla Sugar
- `312505123456` - (Generic product)

---

## 📚 Documentation

All the docs you need are in the repo:

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[QUICK_START.md](QUICK_START.md)** | Setup & basic usage | 10 min |
| **[USAGE_EXAMPLE.md](USAGE_EXAMPLE.md)** | Real-world scenarios | 15 min |
| **[FEATURES.md](FEATURES.md)** | Complete feature list | 20 min |
| **[DEVELOPER.md](DEVELOPER.md)** | Technical details | 30 min |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | System design | 15 min |

---

## 🎮 Common Actions

### Search by Product Name
Instead of UPC, try typing a product name:
- Type: `Mahogany Teakwood`
- Select: "Name / Keyword"
- Click: Search
- Pick the product you want

### Search by Product URL
Find a product on bathandbodyworks.com:
- Copy the URL
- Paste in search box
- Click: Search

### Export to Excel
Track products in a spreadsheet:
- Search and add products
- Click: "Download Updated Excel"
- Open file in Excel/Google Sheets
- Edit and re-upload later

### Continue Tracking
If you have an existing spreadsheet:
- Click: "Upload .xlsx"
- Search for updated prices
- Click: "Add / Update in Excel"
- Click: "Download Updated Excel"

---

## 🐛 Troubleshooting

### "Can't connect to backend"
- Make sure you ran Step 1 (backend server running on port 8000)
- Try: http://localhost:8000/docs (should show API documentation)

### "Can't find product"
- Double-check the UPC code digits
- Try searching by product name instead
- Visit bathandbodyworks.com to verify product exists

### "Port already in use"
- Backend: `lsof -i :8000` then kill the process
- Frontend: `lsof -i :5173` then kill the process

---

## 🔗 Quick Links

- 🌐 **App URL**: http://localhost:5173
- 📖 **API Docs**: http://localhost:8000/docs
- 📁 **Backend Code**: `backend/app/`
- 🎨 **Frontend Code**: `frontend/src/`
- 🛠️ **Configuration**: `backend/app/config.py`

---

## 📱 Using with Mobile/Barcode Scanner

If you have a **barcode scanner device** (physical or app):

1. Open the search field
2. Point scanner at barcode
3. Scanner types the UPC automatically
4. Press Enter
5. Result appears instantly

**Most barcode scanners work like a keyboard** - they just type the numbers and press Enter.

---

## 💡 Tips for Best Results

✅ **Do:**
- Copy exact product URLs from bathandbodyworks.com
- Use complete UPC codes (all 12-14 digits)
- Download your Excel file regularly for backup
- Re-upload previous Excel to continue tracking

❌ **Don't:**
- Use incomplete UPC codes
- Mix Bath & Body Works products with other brands
- Expect instant results on slow connections
- Share your session between different computers

---

## 🎓 Learn More

Ready to dive deeper? Check out:

1. **Want quick start?** → [QUICK_START.md](QUICK_START.md)
2. **Want examples?** → [USAGE_EXAMPLE.md](USAGE_EXAMPLE.md)
3. **Want all features?** → [FEATURES.md](FEATURES.md)
4. **Want technical details?** → [DEVELOPER.md](DEVELOPER.md)

---

## ✨ What's Included

Your app automatically:
- ✅ Fetches product names from Bath & Body Works
- ✅ Gets product images
- ✅ Checks current prices and sales
- ✅ Tracks promotions (Buy 3 Get 1, 50% Off, etc.)
- ✅ Shows stock availability (In Stock / Out of Stock)
- ✅ Exports to Excel format
- ✅ Caches searches for speed
- ✅ Rate-limits requests (polite to BBW's servers)

---

## 🚀 Next Steps

1. **Start the app** (follow the 3 steps above)
2. **Try scanning a UPC** or searching by name
3. **Download your first spreadsheet**
4. **Come back to track more products**

---

## 🆘 Need Help?

**Issue:** App won't start  
**Solution:** Check both backend and frontend are running in different terminals

**Issue:** Product not found  
**Solution:** Try searching by name instead of UPC

**Issue:** Want to understand everything?  
**Solution:** Read [QUICK_START.md](QUICK_START.md) - it covers everything

---

## 🎉 You're Ready!

Your app is **fully functional** and ready for:
- Tracking Bath & Body Works prices
- Building Excel spreadsheets
- Monitoring sales and promotions
- Managing product inventories

**Now go track some products!** 🧴✨

---

**Questions?** Check the docs or review the [troubleshooting section](QUICK_START.md#troubleshooting).

**Want to extend it?** Read [DEVELOPER.md](DEVELOPER.md) for technical setup.

**Happy tracking!** 💚
