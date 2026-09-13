import { useEffect, useRef, useState } from "react";
import { Html5QrcodeScanner } from "html5-qrcode";

export default function BarcodeScanner({ onScan, onError, disabled }) {
  const [isActive, setIsActive] = useState(false);
  const [lastScannedValue, setLastScannedValue] = useState("");
  const [cameraPermission, setCameraPermission] = useState(null);
  const scannerRef = useRef(null);
  const html5QrcodeScannerRef = useRef(null);

  // Initialize the barcode scanner
  useEffect(() => {
    if (!isActive) {
      // Clean up scanner when not active
      if (html5QrcodeScannerRef.current) {
        html5QrcodeScannerRef.current
          .stop()
          .catch(() => {
            // Scanner might have been stopped already
          });
        html5QrcodeScannerRef.current = null;
      }
      return;
    }

    if (!scannerRef.current) {
      return;
    }

    // Initialize scanner
    const html5QrcodeScanner = new Html5QrcodeScanner(
      scannerRef.current.id,
      {
        fps: 10,
        qrbox: { width: 280, height: 280 },
        aspectRatio: 1.0,
        supportedScanTypes: ["QR_CODE", "LINEAR_CODES"],
        rememberLastUsedCamera: true,
        showTorchButtonIfSupported: true,
      },
      /* verbose= */ false
    );

    html5QrcodeScannerRef.current = html5QrcodeScanner;

    const onScanSuccess = (decodedText, decodedResult) => {
      // Avoid processing the same barcode multiple times in quick succession
      if (decodedText === lastScannedValue) {
        return;
      }

      setLastScannedValue(decodedText);
      onScan(decodedText.trim());

      // Reset the last scanned value after a delay to allow re-scanning the same barcode
      setTimeout(() => {
        setLastScannedValue("");
      }, 2000);
    };

    const onScanFailure = (error) => {
      // Silently ignore scanning errors (this is normal as the scanner continuously attempts to read)
    };

    html5QrcodeScanner
      .render(onScanSuccess, onScanFailure)
      .catch((err) => {
        onError("Failed to initialize camera. Please check permissions and try again.");
        setCameraPermission(false);
        setIsActive(false);
      });

    setCameraPermission(true);

    return () => {
      if (html5QrcodeScannerRef.current) {
        html5QrcodeScannerRef.current
          .stop()
          .catch(() => {
            // Scanner might have been stopped already
          });
        html5QrcodeScannerRef.current = null;
      }
    };
  }, [isActive, lastScannedValue, onScan, onError]);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <span>📱 Barcode Scanner</span>
          </h3>
          <p className="text-xs text-gray-500 mt-1">
            Use your device camera to scan product EAN/UPC barcodes
          </p>
        </div>
        <button
          onClick={() => setIsActive(!isActive)}
          disabled={disabled || cameraPermission === false}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
            isActive
              ? "bg-red-100 text-red-700 hover:bg-red-200 disabled:opacity-50"
              : "bg-blue-100 text-blue-700 hover:bg-blue-200 disabled:opacity-50"
          }`}
        >
          {isActive ? "Stop Scanning" : "Start Scanner"}
        </button>
      </div>

      {cameraPermission === false && (
        <div className="mb-4 p-3 bg-amber-50 border border-amber-200 text-amber-700 text-sm rounded-lg">
          <strong>Camera access denied.</strong> Check your browser permissions and ensure
          the site has camera access. Some browsers may require HTTPS.
        </div>
      )}

      {isActive && (
        <div className="relative bg-black rounded-lg overflow-hidden border-2 border-gray-300">
          <div
            id="html5qr-code"
            ref={scannerRef}
            style={{ width: "100%", height: "400px" }}
          />
          <div className="absolute bottom-4 left-4 right-4 bg-blue-600/90 text-white text-xs p-2 rounded text-center">
            Point camera at barcode
          </div>
        </div>
      )}

      {!isActive && cameraPermission !== false && (
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-8 text-center">
          <div className="text-4xl mb-2">📷</div>
          <p className="text-gray-600 text-sm">Camera scanner is ready. Click "Start Scanner" to begin.</p>
        </div>
      )}
    </div>
  );
}
