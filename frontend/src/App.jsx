import { useEffect, useState } from "react";
import {
  createSession,
  getRows,
  lookupCandidate,
  lookupProduct,
  updateExcel,
  uploadExcel,
} from "./api";
import BarcodeScanner from "./components/BarcodeScanner";
import CandidateList from "./components/CandidateList";
import ExcelPanel from "./components/ExcelPanel";
import ProductCard from "./components/ProductCard";
import SearchBar from "./components/SearchBar";

export default function App() {
  const [product, setProduct] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);

  const [sessionId, setSessionId] = useState(null);
  const [rows, setRows] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [adding, setAdding] = useState(false);
  const [justAdded, setJustAdded] = useState(false);

  // Auto-create a blank spreadsheet session on first load so the app is
  // immediately usable without requiring an upload.
  useEffect(() => {
    createSession()
      .then((res) => {
        setSessionId(res.session_id);
        setRows(res.rows);
      })
      .catch((err) => setError(err.message));
  }, []);

  async function handleSearch(query, queryType) {
    setSearching(true);
    setError(null);
    setProduct(null);
    setCandidates([]);
    setJustAdded(false);
    try {
      const res = await lookupProduct(query, queryType);
      if (res.product) {
        setProduct(res.product);
      } else {
        setCandidates(res.candidates || []);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSearching(false);
    }
  }

  async function handleSelectCandidate(url) {
    setSearching(true);
    setError(null);
    try {
      const res = await lookupCandidate(url);
      setProduct(res.product);
      setCandidates([]);
      setJustAdded(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setSearching(false);
    }
  }

  async function handleAddToExcel() {
    if (!sessionId || !product) return;
    setAdding(true);
    setError(null);
    try {
      const res = await updateExcel(sessionId, product);
      setRows(res.rows);
      setJustAdded(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setAdding(false);
    }
  }

  async function handleNewSession() {
    setError(null);
    try {
      const res = await createSession();
      setSessionId(res.session_id);
      setRows(res.rows);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleUpload(file) {
    setUploading(true);
    setError(null);
    try {
      const res = await uploadExcel(file);
      setSessionId(res.session_id);
      setRows(res.rows);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  function handleBarcodeScanned(barcode) {
    // When a barcode is scanned, search for it as a UPC
    handleSearch(barcode, "upc");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-5">
          <h1 className="text-xl font-bold text-gray-900">🧴 BBW Price Tracker</h1>
          <p className="text-sm text-gray-500 mt-1">
            Look up Bath &amp; Body Works prices and sync them straight to your Excel sheet.
          </p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 flex flex-col gap-6">
        <BarcodeScanner
          onScan={handleBarcodeScanned}
          onError={setError}
          disabled={searching}
        />

        <SearchBar onSearch={handleSearch} loading={searching} />

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
            {error}
          </div>
        )}

        <ProductCard
          product={product}
          onAddToExcel={handleAddToExcel}
          adding={adding}
          added={justAdded}
        />

        <CandidateList candidates={candidates} onSelect={handleSelectCandidate} loading={searching} />

        <ExcelPanel
          session={sessionId}
          rows={rows}
          onNewSession={handleNewSession}
          onUpload={handleUpload}
          uploading={uploading}
        />
      </main>

      <footer className="max-w-4xl mx-auto px-4 pb-8 text-xs text-gray-400">
        For personal use tracking publicly listed prices. Please use responsibly and in
        accordance with bathandbodyworks.com's Terms of Service.
      </footer>
    </div>
  );
}
