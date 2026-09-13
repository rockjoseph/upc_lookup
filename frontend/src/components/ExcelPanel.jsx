import { useRef } from "react";
import { downloadUrl } from "../api";

function money(value) {
  if (value === null || value === undefined) return "";
  return `$${Number(value).toFixed(2)}`;
}

export default function ExcelPanel({ session, rows, onNewSession, onUpload, uploading }) {
  const fileInputRef = useRef(null);

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (file) onUpload(file);
    e.target.value = "";
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h2 className="font-semibold text-gray-900">Excel Spreadsheet</h2>
        <div className="flex gap-2">
          <button
            onClick={onNewSession}
            className="text-xs font-medium rounded-lg border border-gray-300 px-3 py-1.5 hover:bg-gray-50 transition"
          >
            New Spreadsheet
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="text-xs font-medium rounded-lg border border-gray-300 px-3 py-1.5 hover:bg-gray-50 transition disabled:opacity-50"
          >
            {uploading ? "Uploading..." : "Upload .xlsx"}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx"
            className="hidden"
            onChange={handleFileChange}
          />
          {session && (
            <a
              href={downloadUrl(session)}
              className="text-xs font-medium rounded-lg bg-pink-600 text-white px-3 py-1.5 hover:bg-pink-700 transition"
            >
              Download Updated Excel
            </a>
          )}
        </div>
      </div>

      {!session && (
        <p className="text-sm text-gray-400 mt-4">
          Start a new spreadsheet or upload an existing one to begin tracking prices.
        </p>
      )}

      {session && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-400 border-b border-gray-100">
                <th className="py-2 pr-3">SKU/UPC</th>
                <th className="py-2 pr-3">Product Name</th>
                <th className="py-2 pr-3">Original</th>
                <th className="py-2 pr-3">Sale Price</th>
                <th className="py-2 pr-3">Promo</th>
                <th className="py-2 pr-3">Last Checked</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-4 text-center text-gray-400">
                    No rows yet — search for a product and add it above.
                  </td>
                </tr>
              )}
              {rows.map((row, idx) => (
                <tr key={`${row.sku}-${idx}`} className="border-b border-gray-50">
                  <td className="py-2 pr-3 text-gray-500">{row.sku || "—"}</td>
                  <td className="py-2 pr-3 text-gray-800 max-w-xs truncate">{row.name}</td>
                  <td className="py-2 pr-3 text-gray-500">{money(row.original_price)}</td>
                  <td className="py-2 pr-3 font-medium text-pink-600">{money(row.sale_price)}</td>
                  <td className="py-2 pr-3 text-gray-500">{row.promo_deal || "—"}</td>
                  <td className="py-2 pr-3 text-gray-400 whitespace-nowrap">{row.last_checked || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
