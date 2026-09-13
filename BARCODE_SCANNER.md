# 📱 Barcode Scanner Feature

## Overview

The **Barcode Scanner** is a real-time camera-based barcode detection feature integrated into the BBW Price Tracker. It allows you to quickly scan product EAN/UPC barcodes using your device's camera, eliminating the need to manually type in barcode numbers.

## Features

- **Real-time barcode detection**: Uses your device camera to detect and read barcodes instantly
- **Support for multiple barcode formats**: 
  - UPC-A, UPC-E
  - EAN-8, EAN-13
  - Code 128, Code 39
  - ITF/Interleaved 2 of 5
  - QR codes
  - And many other linear barcode formats
- **Auto-search**: Automatically searches for the product when a barcode is scanned
- **Visual feedback**: Real-time camera preview with scanning guidance
- **Flash/Torch support**: Toggle camera flash on devices that support it
- **Permission handling**: Clear error messages if camera access is denied
- **Duplicate prevention**: Won't re-scan the same barcode multiple times within 2 seconds

## How to Use

### Starting the Scanner

1. Open the BBW Price Tracker web app
2. Scroll to the top where you see the **"📱 Barcode Scanner"** section
3. Click the **"Start Scanner"** button
4. Your device will request camera permission - **allow access**
5. A camera preview will appear with a scanning frame overlay

### Scanning a Product

1. Point your device camera at a product's barcode
2. Position the barcode within the scanning frame (the highlighted square)
3. Keep steady for 1-2 seconds
4. The app will automatically detect the barcode and:
   - Search for the product
   - Display product information (name, price, promo details)
   - Show stock status

### After Scanning

Once a product is found:
- Review the product details in the **Product Card**
- Click **"Add / Update in Excel"** to add it to your tracking spreadsheet
- Scan another product or use the manual search bar for additional lookups

### Stopping the Scanner

- Click **"Stop Scanning"** button to turn off the camera
- The scanner automatically stops when the app is closed

## Browser Compatibility

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome/Chromium | ✅ Yes | ✅ Yes |
| Firefox | ✅ Yes | ✅ Yes |
| Safari | ✅ Yes | ✅ Yes (iOS 15+) |
| Edge | ✅ Yes | ✅ Yes |

**Requirements**:
- Camera access permission
- HTTPS connection (required on most browsers for security)
- Modern browser with WebRTC support

## Troubleshooting

### "Camera access denied" message
- Check browser permissions for camera access
- In settings, ensure you've granted camera permission to the site
- Some browsers require HTTPS connections to access the camera
- On iOS: Go to Settings > Privacy > Camera and enable for Safari/your browser
- On Android: Go to Settings > Apps > [Browser Name] > Permissions > Camera and enable

### Camera won't start
- Close other apps using the camera
- Restart the browser
- Ensure your device has a camera
- Check that you're using HTTPS (except localhost)
- Try a different browser

### Barcode not being detected
- Ensure the barcode has good lighting (not too dark or too bright)
- Keep the barcode steady within the scanning frame
- Position the barcode squarely to the camera
- Try moving closer or farther from the barcode
- Ensure the barcode isn't damaged or faded
- Some old or low-quality barcodes may not scan - try manual entry instead

### Scanning same barcode again
- Wait 2 seconds between scans of the same barcode
- The app prevents rapid duplicate scans

### Flash/Torch not working
- Your device may not support the feature
- Some iOS devices require permission to use the flash
- Try a different camera angle or lighting condition

## Privacy & Security

- **No data collection**: The barcode scanner runs entirely on your device
- **No server upload**: Scanned data is never sent anywhere except to Bath & Body Works API through the product lookup
- **Local processing**: All image processing happens locally in your browser
- **Camera access**: Only active when you click "Start Scanner"

## Technical Details

- **Library**: [html5-qrcode](https://github.com/mebjas/html5-qrcode) - A pure JavaScript barcode/QR code scanning library
- **Camera access**: Uses WebRTC MediaStream API
- **Processing**: Real-time frame analysis at 10 FPS for optimal performance

## Tips for Best Results

1. **Lighting**: Scan in good natural light when possible
2. **Positioning**: Center the barcode in the scanning frame
3. **Angle**: Keep the camera perpendicular to the barcode
4. **Distance**: Adjust distance so the barcode fills about 60-70% of the frame
5. **Stability**: Keep the device steady while scanning
6. **Clean lens**: Make sure your device camera lens is clean
7. **Slow down**: Give the scanner a moment to process - don't move too quickly

## Combining Scanner with Manual Search

The barcode scanner works alongside the existing manual search features:
- **Auto-detect**: The scanner automatically detects barcode type
- **Fallback**: If the scanner doesn't work, you can still manually type the barcode in the search box
- **Multiple methods**: Use scanner for most products, manual entry for damaged barcodes

## Keyboard Shortcut (When scanning)

When the scanner is active, you can still:
- Paste a barcode in the search box below and use the "Search" button
- Upload an Excel file to sync prices
- Use all other features normally

## Accessibility

- Scanner has proper ARIA labels for screen readers
- Camera controls are keyboard accessible
- Error messages are clear and descriptive
- Works with browser zoom levels

## Future Enhancements

Potential improvements in future versions:
- Bulk scanning mode (scan multiple products and queue them)
- Scan history with easy re-search
- Barcode format detection and display
- Custom camera settings (zoom, resolution)
- Barcode validation checking
- Integration with inventory management

---

**Questions or issues?** Check the troubleshooting section above or review the app's documentation.
