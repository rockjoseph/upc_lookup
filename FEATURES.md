# 🧴 BBW UPC Scanner - Features & Capabilities

## Complete Feature List

### 1. UPC Code Scanning & Product Lookup

#### How It Works
- **Input Method**: Type or paste UPC codes (8-14 digits)
- **Recognition**: Auto-detects UPC format and searches Bath & Body Works catalog
- **Fallback**: If exact UPC match isn't found, shows similar products for selection
- **Data Extraction**: Automatically retrieves:
  - ✅ Product Name
  - ✅ SKU/UPC Number
  - ✅ Sale Price
  - ✅ Original Price
  - ✅ Promotional Tags ("Buy 3 Get 1 Free", "40% Off", etc.)
  - ✅ Stock Status (In Stock / Out of Stock)
  - ✅ Product Image URL
  - ✅ Product URL

#### UPC Format Support
- **Standard UPC-A**: 12 digits (e.g., `031965005612`)
- **UPC-E**: 8 digits (compressed format)
- **EAN-13**: 13 digits (international format)
- **Custom 14-digit codes**: Supported

**Example UPC Search:**
```
Input: 031965005612
Result: 
  - Bath & Body Works Warm Vanilla Sugar
  - Price: $14.50 (was $27.50)
  - Promo: "Buy 3 Get 1 Free"
  - In Stock ✓
  - [Product image displayed]
```

---

### 2. Multi-Method Product Search

You can search in **three different ways**:

#### Method A: UPC / Barcode (Most Reliable)
- Fastest and most accurate
- Use when you have the barcode in front of you
- Type or paste the UPC code
- Select "UPC / Barcode" from dropdown

#### Method B: Product URL (Direct)
- Paste the full URL from bathandbodyworks.com
- Fetches product directly without searching
- Example: `https://www.bathandbodyworks.com/p/warm-vanilla-sugar-fine-fragrance-mist/...`
- Select "Product URL" from dropdown

#### Method C: Name / Keyword (Flexible)
- Search by product name or description
- Example: "Mahogany Teakwood Delight"
- Shows 3-8 matching products to choose from
- Select "Name / Keyword" from dropdown

#### Auto-Detect Mode (Default)
- Leave dropdown on "Auto-detect"
- App automatically determines if input is URL, UPC, or keyword
- Recommended for quick searches

---

### 3. Real-Time Product Display

The **Product Card** shows:

```
┌─ PRODUCT CARD ─────────────────────────────┐
│                                             │
│  [28x28px Image]  ▸ Product Name            │
│                     SKU: 012345             │
│                                             │
│                     💰 $12.50 (was $25.00)  │
│                     🏷️  Buy 3 Get 1 Free    │
│                     🟢 In Stock             │
│                                             │
│  [Add/Update] [View on bathandbodyworks.com]│
│                                             │
└─────────────────────────────────────────────┘
```

**Visual Indicators:**
- 🟢 Green dot = In Stock
- 🔴 Red dot = Out of Stock
- Pink price = On sale (original price shown struck through)
- Gray price = Regular price

---

### 4. Excel Spreadsheet Management

#### Create New Spreadsheet
- Automatic on page load
- Or click "New Spreadsheet" button
- Starts with empty `Prices` sheet

#### Excel Schema
Your spreadsheet has these columns:

| Column | Data Type | Example |
|--------|-----------|---------|
| **SKU/UPC** | Text | `031965005612` |
| **Product Name** | Text | `Warm Vanilla Sugar Fine Fragrance Mist` |
| **Original Price** | Currency | `$27.50` |
| **Current Sale Price** | Currency | `$14.50` |
| **Promo Deal** | Text | `Buy 3 Get 1 Free` |
| **Last Checked Date/Time** | Date+Time | `2024-09-13 14:30:00` |
| **Product URL** | Hyperlink | `https://www.bathandbodyworks.com/p/...` |

#### Add or Update Products
When you click **"Add / Update in Excel"**, the app:

1. **Checks for existing product** by:
   - SKU match (primary)
   - Exact product name match (fallback)

2. **If product exists**: Updates these columns only:
   - Current Sale Price
   - Promo Deal
   - Last Checked Date/Time
   - Product URL

3. **If product is new**: Appends entire row to spreadsheet

This means your price history is **preserved** — the app only updates current data.

#### Upload Existing Spreadsheet
- Click "Upload .xlsx"
- Select your existing Bath & Body Works tracking file
- Must have column headers: SKU/UPC, Product Name, etc.
- App matches existing products by SKU or name
- Preserves original data, updates prices

#### Download Updated File
- Click "Download Updated Excel"
- Saves as `.xlsx` file (Excel format)
- Includes all your products and latest prices
- Edit in Excel, Google Sheets, or any spreadsheet app
- Re-upload to continue tracking in the app

---

### 5. Smart Caching & Performance

The app is optimized for speed:

- **Request Cache**: Recently searched products cached for 5 minutes
- **Rate Limiting**: 2.5-second minimum delay between requests (polite scraping)
- **Retry Logic**: Automatic retry with exponential backoff on network issues
- **Parallel Operations**: Search while downloading, add while searching

**Result:** Fast repeat searches, instant feedback, no slowdowns

---

### 6. Error Handling & Recovery

The app handles common issues gracefully:

| Scenario | Behavior |
|----------|----------|
| **UPC not found** | Shows similar products or clear error message |
| **Network error** | Retries automatically up to 3 times with delays |
| **Page loading error** | Falls back to JavaScript rendering (if available) |
| **Invalid Excel file** | Clear error message with format requirements |
| **Session timeout** | Auto-creates new session, keeps data safe |

---

### 7. Data Privacy & Storage

- **Local Storage**: Session data stored only on your computer
- **No Cloud Upload**: All data stays local (files saved to `backend/data/sessions/`)
- **Session IDs**: Unique ID for each tracking session
- **Auto-Cleanup**: Old sessions deleted after 24 hours of inactivity

---

## Advanced Features

### Batch Import/Export Workflow

**Workflow: Existing Sheet → App → Update → Download**

```
1. Have existing "Bath & Body Works Prices.xlsx"
   ↓
2. Click "Upload .xlsx"
   ↓
3. Search for new products or re-check prices
   ↓
4. Click "Add / Update in Excel" for each product
   ↓
5. Click "Download Updated Excel"
   ↓
6. Now have updated file with latest prices!
```

### Multi-Session Support

Each "session" is independent:
- Click "New Spreadsheet" to start tracking a different product set
- Upload to switch between multiple tracking lists
- Each session has unique ID in backend storage

---

## Technical Details

### Product Data Sources
- **Primary**: JSON-LD schema.org Product data (embedded in page)
- **Secondary**: CSS selectors on page HTML (fallback)
- **Tertiary**: Playwright JavaScript rendering (optional, if JS-heavy page)

### Search Flow
```
User Input
    ↓
[Auto-Detect Query Type]
    ├─→ URL? → Direct scrape
    ├─→ UPC? → Site search
    └─→ Keyword? → Site search
         ↓
    [Search Results]
         ↓
    [1 match? → Scrape directly]
    [Multiple? → Show candidates]
         ↓
    [Return Product Data]
```

### Rate Limiting Policy
- **Min interval**: 2.5 seconds between BBW requests
- **Per-page cache**: 5 minutes (same UPC searched twice in 5 min = no re-fetch)
- **Retry strategy**: 3 attempts with exponential backoff (2s, 4s, 8s)
- **Friendly headers**: Real User-Agent, Referer, etc. (not bot-like)

---

## Use Cases

### 1. Personal Price Monitoring
- Track products you love
- Monitor price drops
- Plan purchases around promotions

### 2. Budget Shopping
- Build list of products you want
- Check prices across visits
- Export for spreadsheet analysis

### 3. Gift Idea Tracking
- Save product links and prices
- Remember what friends like
- Compare prices at different times

### 4. Inventory Management
- Track product availability
- Monitor stock status changes
- Plan restocking

---

## Roadmap / Potential Enhancements

Future features could include:
- 📱 Mobile barcode scanner (camera-based)
- 📧 Price drop alerts (email notifications)
- 📊 Price trend charts/graphs
- 🔔 Wishlist with notifications
- ☁️ Cloud backup option
- 🌙 Dark mode
- 📤 Export to Google Sheets, CSV
- 🛒 Bulk product recommendations

---

## Limitations & Notes

- **Scraping**: BBW's website markup can change; app may need updates
- **Rate Limiting**: Deliberately polite to respect site's Terms of Service
- **Cache**: Old searches cached ~5 minutes; use "New Spreadsheet" for fresh data
- **JavaScript Pages**: Some promotions rendered as images may not be detected

---

## Performance Benchmarks

| Action | Typical Time |
|--------|-------------|
| UPC Lookup (cached) | < 0.5 seconds |
| UPC Lookup (fresh) | 3-5 seconds |
| Multiple matches shown | < 1 second |
| Add to Excel | < 0.5 seconds |
| Download .xlsx | < 0.5 seconds |
| Upload .xlsx | 1-2 seconds |

---

## FAQ

**Q: How do I know if a UPC is valid?**  
A: Valid UPCs are 8-14 digits. If you're unsure, use the product name search instead.

**Q: Can I edit the Excel file manually?**  
A: Yes! Edit it in Excel or Google Sheets, then re-upload and continue tracking.

**Q: How many products can I track?**  
A: No limit! File size depends on your spreadsheet, but typically thousands of products per file.

**Q: Is my data backed up?**  
A: Data is stored locally on your computer. For safety, download your `.xlsx` file regularly.

**Q: Can multiple people use the app simultaneously?**  
A: The app is designed for single-user/personal use. Running it locally is private to your computer.

**Q: What if Bath & Body Works changes their website?**  
A: The app will show an error. The developers can update the scraper to match the new layout.

---

**Version**: 1.0.0  
**Last Updated**: September 2024
