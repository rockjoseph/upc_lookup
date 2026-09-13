function money(value) {
  if (value === null || value === undefined) return "—";
  return `$${Number(value).toFixed(2)}`;
}

export default function ProductCard({ product, onAddToExcel, adding, added }) {
  if (!product) return null;

  const onSale =
    product.original_price != null &&
    product.sale_price != null &&
    product.sale_price < product.original_price;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex gap-5">
      {product.image_url ? (
        <img
          src={product.image_url}
          alt={product.name}
          className="w-28 h-28 object-cover rounded-lg border border-gray-100 flex-shrink-0"
        />
      ) : (
        <div className="w-28 h-28 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400 text-xs flex-shrink-0">
          No image
        </div>
      )}

      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-gray-900 truncate">{product.name}</h3>
        {product.sku && <p className="text-xs text-gray-400 mt-0.5">SKU: {product.sku}</p>}

        <div className="flex items-baseline gap-2 mt-2">
          <span className={`text-xl font-bold ${onSale ? "text-pink-600" : "text-gray-900"}`}>
            {money(product.sale_price)}
          </span>
          {onSale && (
            <span className="text-sm text-gray-400 line-through">{money(product.original_price)}</span>
          )}
        </div>

        {product.promo_deal && (
          <span className="inline-block mt-2 text-xs font-medium bg-pink-50 text-pink-700 px-2 py-1 rounded-full">
            {product.promo_deal}
          </span>
        )}

        <div className="flex items-center gap-2 mt-2">
          <span
            className={`inline-block w-2 h-2 rounded-full ${
              product.stock_status === "OutOfStock" ? "bg-red-400" : "bg-green-500"
            }`}
          />
          <span className="text-xs text-gray-500">
            {product.stock_status === "OutOfStock" ? "Out of stock" : "In stock"}
          </span>
        </div>

        <div className="flex items-center gap-3 mt-4">
          <button
            onClick={onAddToExcel}
            disabled={adding}
            className="rounded-lg bg-gray-900 text-white text-sm font-medium px-4 py-2 hover:bg-gray-700 disabled:opacity-50 transition"
          >
            {adding ? "Saving..." : added ? "✓ Saved to Excel" : "Add / Update in Excel"}
          </button>
          <a
            href={product.url}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-gray-400 hover:text-gray-600 underline"
          >
            View on bathandbodyworks.com
          </a>
        </div>
      </div>
    </div>
  );
}
