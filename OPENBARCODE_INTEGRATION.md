# Open Barcode Integration

## Overview

This application now uses **Open Barcode** as the primary product lookup method for UPC/EAN codes. This eliminates bot detection issues from web scraping Bath & Body Works directly.

## How It Works

### 1. **UPC Code Lookup**
- User provides a UPC/EAN code (8-14 digits)
- App queries Open Barcode database first
- If found, returns product name and details
- No web scraping, no bot detection

### 2. **Fallback to Bath & Body Works**
If Open Barcode doesn't have the product:
- Automatically falls back to Bath & Body Works search
- Users can still get pricing and promo info
- More reliable for Bath & Body Works-specific products

### 3. **Batch Excel Processing**
- Upload an Excel file with UPC codes in Column A
- App populates product names using Open Barcode
- Returns updated Excel file ready for manual pricing additions

## API Endpoints

### Single UPC Lookup
```bash
GET /api/batch/lookup/{upc}
```
**Example:**
```bash
curl http://localhost:8000/api/batch/lookup/1200198024751
```

**Response:**
```json
{
  "status": "found",
  "upc": "1200198024751",
  "name": "Bath & Body Works Product Name",
  "sku": "SKU123",
  "price": "N/A",
  "note": "Pricing should be verified on retailer website"
}
```

### Batch Excel File Processing
```bash
POST /api/batch/lookup-upcs
Content-Type: multipart/form-data

[Excel file with UPC codes]
```

**Response:**
```json
{
  "status": "success",
  "processed": 10,
  "errors": 2,
  "results": [
    {
      "row": 2,
      "upc": "1200198024751",
      "product_name": "Bath & Body Works Product",
      "sku": "SKU123",
      "status": "found"
    }
  ],
  "error_details": [
    {
      "row": 3,
      "upc": "invalid",
      "error": "Invalid UPC/EAN format"
    }
  ]
}
```

## Usage Workflow

### Option 1: Excel File Upload (Recommended)
1. Prepare Excel file with UPC codes in Column A
2. POST file to `/api/batch/lookup-upcs`
3. Receive updated Excel with product names populated
4. Manually add pricing from Bath & Body Works website or other sources
5. Download completed spreadsheet

### Option 2: Interactive Search
1. User enters UPC in search box
2. App queries Open Barcode first
3. If product found → display product card
4. If not found → falls back to Bath & Body Works search
5. User adds product to Excel spreadsheet

### Option 3: Single UPC Lookup via API
```bash
curl http://localhost:8000/api/batch/lookup/1200198024751
```

## Configuration

No additional configuration needed! The integration is automatic:
- Uses Open Barcode by default for UPC lookups
- Falls back to Bath & Body Works if needed
- No API keys required (Open Barcode is free)
- No rate limiting concerns

## Advantages Over Web Scraping

| Feature | Web Scraping | Open Barcode |
|---------|--------------|--------------|
| **Bot Detection** | ❌ Gets blocked | ✅ No scraping |
| **Rate Limiting** | ⚠️ Possible | ✅ No limits |
| **Reliability** | ⚠️ Markup changes break it | ✅ Stable API |
| **Speed** | ⚠️ Slow (3-5s per page) | ✅ Fast (<1s) |
| **Offline** | ❌ No | ✅ Yes (cached) |
| **Pricing Data** | ✅ Real-time | ⚠️ Manual lookup |

## Limitations

1. **Open Barcode is Code-to-Product Only**
   - Returns product name, brand, category
   - Does NOT include pricing
   - Does NOT include availability status

2. **Works Best For:**
   - General product identification
   - Building product databases
   - Cross-referencing products
   - Bulk UPC processing

3. **Pricing Still Needs To Be:**
   - Looked up manually from retailer websites
   - Scraped from Bath & Body Works (fallback)
   - Added via manual data entry

## Implementation Details

### Files Added/Modified

**New Files:**
- `app/scraper/openbarcode_lookup.py` - Open Barcode API client
- `app/routers/batch_lookup.py` - Batch processing endpoints

**Modified Files:**
- `app/scraper/search.py` - Updated to use Open Barcode first for UPC codes
- `app/main.py` - Added batch_lookup router

### Code Flow

```
User UPC Query
    ↓
resolve_query() in search.py
    ↓
Is it a UPC? → Yes → openbarcode_lookup.lookup_by_upc()
    ↓                        ↓
                    Found in Open Barcode? → Yes → Return Product
                        ↓
                        No → Try BBW search (fallback)
    ↓
Is it a keyword? → Yes → bbw_scraper.search_products()
```

## Testing

### Test Single UPC Lookup
```bash
python -m pytest tests/ -v -k "barcode"
```

### Test Batch Processing
```python
# Example test
import requests

response = requests.get("http://localhost:8000/api/batch/lookup/1200198024751")
assert response.status_code == 200
print(response.json())
```

## Future Enhancements

1. **Pricing API Integration**
   - Integrate with retail pricing APIs
   - Add automatic pricing lookups
   - Price history tracking

2. **Batch Processing Improvements**
   - Direct file upload to Excel endpoint
   - Automatic Excel file generation
   - Download updated files directly

3. **Product Enrichment**
   - Add Open Barcode images
   - Include product categories
   - Add brand information

4. **Error Handling**
   - Better duplicate detection
   - Fuzzy matching for similar products
   - Manual override for uncertain matches

## Support

- **Open Barcode:** https://openbarcode.org
- **Issue:** UPC not found? Try:
  1. Verify UPC is correct (8-14 digits)
  2. Check Bath & Body Works product exists
  3. Use manual lookup on openbarcode.org

## License

Open Barcode is free and open-source. No API key required.
Integration follows Open Barcode's terms of service.
