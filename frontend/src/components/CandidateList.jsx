export default function CandidateList({ candidates, onSelect, loading }) {
  if (!candidates || candidates.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <p className="text-sm text-gray-500 mb-3">Multiple matches found — pick one:</p>
      <ul className="divide-y divide-gray-100">
        {candidates.map((c) => (
          <li key={c.url} className="py-2 flex items-center gap-3">
            {c.image_url ? (
              <img src={c.image_url} alt={c.name} className="w-10 h-10 object-cover rounded" />
            ) : (
              <div className="w-10 h-10 rounded bg-gray-100" />
            )}
            <span className="flex-1 text-sm text-gray-800 truncate">{c.name}</span>
            <button
              onClick={() => onSelect(c.url)}
              disabled={loading}
              className="text-xs font-medium text-pink-600 hover:text-pink-800 disabled:opacity-50"
            >
              Select
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
