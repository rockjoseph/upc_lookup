import { useState, useRef, useEffect } from "react";

const QUERY_TYPES = [
  { value: "auto", label: "Auto-detect" },
  { value: "url", label: "Product URL" },
  { value: "upc", label: "UPC / Barcode" },
  { value: "keyword", label: "Name / Keyword" },
];

export default function SearchBar({ onSearch, loading }) {
  const [query, setQuery] = useState("");
  const [queryType, setQueryType] = useState("auto");
  const inputRef = useRef(null);

  // Auto-focus the search input on component mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim()) return;
    onSearch(query.trim(), queryType);
    // Clear input after search for next quick entry
    setQuery("");
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2 w-full">
      <input
        ref={inputRef}
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Paste a product URL, UPC/barcode, or type a product name..."
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-400"
        autoComplete="off"
      />
      <select
        value={queryType}
        onChange={(e) => setQueryType(e.target.value)}
        className="rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-pink-400"
      >
        {QUERY_TYPES.map((t) => (
          <option key={t.value} value={t.value}>
            {t.label}
          </option>
        ))}
      </select>
      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-pink-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {loading ? "Searching..." : "Search"}
      </button>
    </form>
  );
}
