# 📖 Usage Example - Complete Walkthrough

This guide walks you through a real example of using the Bath & Body Works UPC Scanner app.

## Scenario: Building Your Fall Product Tracker

You want to track 5 Bath & Body Works products during the fall season and monitor their prices weekly.

---

## Step 1: Start the App

**Terminal 1 (Backend):**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

**Open your browser:** http://localhost:5173

You should see:
```
🧴 BBW Price Tracker
Look up Bath & Body Works prices and sync them straight to your Excel sheet.

[Search box] [Search Type ▼] [Search button]
Excel Spreadsheet
- New Spreadsheet button
- Upload .xlsx button
- (Empty table - ready for data)
```

---

## Step 2: Search for Your First Product by UPC

Let's say you have a **Mahogany Teakwood** product in front of you.

**The barcode shows:** `031965005612`

1. **Click in the search box**
2. **Type or paste:** `031965005612`
3. **Check the dropdown:** Should be on "Auto-detect" (or select "UPC / Barcode")
4. **Click "Search"**

**Result:** (2-3 seconds later)

```
Product Card appears:
┌─────────────────────────────────────────┐
│ [Product Image]  Mahogany Teakwood      │
│                  SKU: 1234567           │
│                  💰 $14.50 (was $27.50) │
│                  🏷️  Buy 3 Get 1 Free   │
│                  🟢 In Stock            │
│ [Add/Update] [View on bathandbodyworks] │
└─────────────────────────────────────────┘
```

---

## Step 3: Add the Product to Your Spreadsheet

**Click:** "Add / Update in Excel"

**You'll see:**
- Button changes to: "Saving..."
- After 1 second: "✓ Saved to Excel"

**Excel table updates to show:**

| SKU/UPC | Product Name | Original | Sale Price | Promo | Last Checked | URL |
|---------|--------------|----------|-----------|-------|--------------|-----|
| 1234567 | Mahogany Teakwood | $27.50 | $14.50 | Buy 3 Get 1 Free | 2024-09-13 14:32 | https://... |

✅ **First product tracked!**

---

## Step 4: Search for More Products

Let's add a second product. This time, let's **search by name** instead of UPC.

1. **Click in the search box** (it clears automatically after each search)
2. **Type:** `Warm Vanilla Sugar`
3. **Keep dropdown on:** "Auto-detect" (or select "Name / Keyword")
4. **Click "Search"**

**Result:** Multiple matches found!

```
Candidate List appears:
┌──────────────────────────────────────┐
│ Choose a product:                    │
├──────────────────────────────────────┤
│ [Image] Warm Vanilla Sugar Lotion    │
│ [Image] Warm Vanilla Sugar Mist      │
│ [Image] Warm Vanilla Sugar Soap      │
│ [Image] Warm Vanilla Sugar Candle    │
└──────────────────────────────────────┘
```

5. **Click on:** "Warm Vanilla Sugar Mist" (your favorite)

**Result:** (1-2 seconds)

```
Product Card appears with full details:
┌─────────────────────────────────────────┐
│ [Image]  Warm Vanilla Sugar Mist        │
│          SKU: 7654321                   │
│          💰 $11.50 (was $16.50)        │
│          🟢 In Stock                    │
│ [Add/Update] [View on bathandbodyworks] │
└─────────────────────────────────────────┘
```

6. **Click:** "Add / Update in Excel"

**Excel table now shows:**

| SKU/UPC | Product Name | Original | Sale Price | Last Checked |
|---------|--------------|----------|-----------|--------------|
| 1234567 | Mahogany Teakwood | $27.50 | $14.50 | 2024-09-13 14:32 |
| 7654321 | Warm Vanilla Sugar Mist | $16.50 | $11.50 | 2024-09-13 14:35 |

✅ **Two products tracked!**

---

## Step 5: Use Product URL Search

Now you're browsing bathandbodyworks.com and found another great deal.

1. **Copy the product URL** from your browser:
   ```
   https://www.bathandbodyworks.com/p/fall-collection-candle/123456.html
   ```

2. **Back in the app, click the search box**
3. **Paste the URL:**
   ```
   https://www.bathandbodyworks.com/p/fall-collection-candle/123456.html
   ```

4. **Dropdown automatically shows:** "Product URL" (or leave on Auto-detect)
5. **Click "Search"**

**Result:** (2-3 seconds, fetches directly)

```
Product Card appears:
[Product Image] Mahogany Autumn Candle
[SKU, Price, Promo, Stock info]
[Add/Update button]
```

6. **Click:** "Add / Update in Excel"

**Excel table now shows 3 products!**

---

## Step 6: Update an Existing Product

Let's say you checked back next week and want to see if the **Mahogany Teakwood** price changed.

1. **Search again for:** `031965005612` (same UPC)
2. **New results show:**

```
Product Card:
Mahogany Teakwood
SKU: 1234567
💰 $10.50 (was $27.50)  ← PRICE DROPPED!
🏷️  Buy 3 Get 1 Free
🟢 In Stock
```

3. **Click:** "Add / Update in Excel"

**Important:** The app automatically updates the **existing row** for SKU 1234567:

| SKU/UPC | Product Name | Original | Sale Price | Last Checked |
|---------|--------------|----------|-----------|--------------|
| 1234567 | Mahogany Teakwood | $27.50 | **$10.50** ← Updated | **2024-09-20 15:45** ← Updated |
| 7654321 | Warm Vanilla Sugar Mist | $16.50 | $11.50 | 2024-09-13 14:35 |
| ... | ... | ... | ... | ... |

✅ **Price history preserved! Original price stayed the same, only current price updated.**

---

## Step 7: Download Your Spreadsheet

Now you have 5 products tracked and want to save your data.

1. **Click:** "Download Updated Excel"
2. **A file downloads:** `BBW_Prices_[datetime].xlsx`
3. **Open it in Excel, Google Sheets, or any spreadsheet app**

**You can:**
- ✏️ Edit prices manually (e.g., add notes)
- 📊 Create charts of price trends
- 📤 Share with friends
- 🔄 Re-upload next week to continue tracking

---

## Step 8: Continue Tracking Next Week

Next week, you want to check prices again on your tracked products.

**Option A: Start Fresh**
```
1. Click "New Spreadsheet"
2. Search for each product again
3. Click "Add / Update in Excel" each time
```

**Option B: Continue from Last Week's Sheet (Recommended)**
```
1. Click "Upload .xlsx"
2. Select: BBW_Prices_[datetime].xlsx
3. Search for products you want to re-check
4. Click "Add / Update in Excel"
5. Only prices/dates update - your original data stays
6. Download updated file
```

---

## Complete Example: Final Spreadsheet

After a few weeks of tracking, your spreadsheet might look like:

| SKU/UPC | Product Name | Original | Sale Price | Promo Deal | Last Checked | URL |
|---------|--------------|----------|-----------|-----------|--------------|-----|
| 031965005612 | Mahogany Teakwood Mist | $27.50 | $9.50 | Buy 3 Get 1 | 2024-09-27 14:32 | https://... |
| 987654321 | Warm Vanilla Sugar Mist | $16.50 | $11.50 | - | 2024-09-27 14:35 | https://... |
| 111222333 | Fresh Cut Lilacs Candle | $26.00 | $18.50 | 50% Off | 2024-09-27 14:38 | https://... |
| 444555666 | Mahogany Teakwood Lotion | $15.00 | $12.00 | - | 2024-09-27 14:40 | https://... |
| 777888999 | Autumn Wreath 3-Wick | $45.00 | $29.99 | Buy 2 Get 1 | 2024-09-27 14:42 | https://... |

**Insights from this data:**
- 📉 Mahogany Teakwood prices dropping (great time to buy!)
- 💰 Buy 3 Get 1 deals very common this season
- 📊 Larger products (candles) on deeper discounts

---

## Keyboard Shortcuts

**Quick Tip:** You don't need to click "Search" button!

- **Type UPC → Press Enter** → Search runs automatically
- **Type product name → Press Enter** → Search runs automatically  
- **Type URL → Press Enter** → Search runs automatically

---

## Common Workflows

### Workflow 1: Quick Check (5 minutes)
```
1. Enter UPC code
2. See product + price
3. Click "Add / Update"
4. Repeat 2-3 times
5. Done!
```

### Workflow 2: Building a Wishlist (30 minutes)
```
1. Browse bathandbodyworks.com
2. Find products you like
3. Copy each URL
4. Paste in search box
5. Click "Add / Update" for each
6. Download file
```

### Workflow 3: Weekly Price Check (10 minutes)
```
1. Upload last week's .xlsx file
2. Re-search 5-10 products
3. Prices auto-update in spreadsheet
4. Download updated file
5. Compare week-to-week
```

### Workflow 4: Bulk Import from Existing Tracker
```
1. Have old spreadsheet with products
2. Click "Upload .xlsx"
3. Search for each product again
4. New prices populate existing rows
5. Download updated version
```

---

## Tips for Success

✅ **Do:**
- Enter complete UPC codes (8-14 digits)
- Use product URLs directly from bathandbodyworks.com
- Download your spreadsheet regularly for backup
- Re-upload previous week's file to preserve price history
- Check prices at consistent times for better trend data

❌ **Don't:**
- Make typos in UPC codes (app will search, but may not find exact match)
- Use incomplete URLs
- Share sessions across computers (create new sessions instead)
- Expect results faster than 2-3 seconds (polite rate limiting in place)

---

## Troubleshooting Scenarios

### Scenario: UPC search returns no results

**What happened:**
- UPC might not be valid
- Bath & Body Works might not carry this product online
- UPC might be for a different retailer

**Solution:**
- Double-check digits (look at product again)
- Try searching by product name instead
- Search bathandbodyworks.com directly to confirm product exists online

### Scenario: Multiple products shown for UPC

**What happened:**
- This UPC might match multiple products
- Site search returned similar products

**Solution:**
- Click on the one that matches your product (check image/name)
- If none match, try searching by product URL instead

### Scenario: Price seems wrong or outdated

**What happened:**
- Site may have changed prices since last check
- Product may be out of stock now
- Cache might be showing old data

**Solution:**
- Click "New Spreadsheet" to clear cache
- Search again to get fresh data from BBW's site
- Check bathandbodyworks.com directly to compare

---

## Excel File Management

### Re-opening Your File
```
1. App starts with blank session
2. Click "Upload .xlsx"
3. Select your BBW_Prices_*.xlsx file
4. Previous session loaded ✓
```

### Editing Manually
```
1. Download your .xlsx file
2. Open in Excel / Google Sheets
3. Edit prices, add notes, create charts
4. Save your changes
5. Re-upload to app to continue tracking
```

### Sharing with Others
```
1. Download your .xlsx file
2. Email to friend / family
3. They can open in spreadsheet app
4. They can see all your tracked products + prices
5. They can re-upload to their own app instance
```

---

**Next Step:** Check out [`FEATURES.md`](FEATURES.md) for advanced features and technical details!

Happy tracking! 🧴✨
