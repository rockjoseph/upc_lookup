"""Open Barcode product lookup service.

Uses the Open Barcode database (https://openbarcode.org) to identify products
by UPC/EAN code. This avoids web scraping and bot detection issues entirely.

Strategy
--------
1. Look up UPC/EAN in Open Barcode database
2. Extract product name, brand, and category
3. Create a Product object with available data
4. Return results for display in Excel or product cards

No pricing data from Open Barcode (it's a code-only database), so we return
estimated pricing of $0.00 with a note that pricing should be verified.
"""
import logging
import requests
from typing import Optional, Dict, Any

from app.models import Product, ScraperError
from app.config import REQUEST_TIMEOUT_SECONDS

logger = logging.getLogger("openbarcode_lookup")

# Open Barcode API endpoint
OPENBARCODE_API = "https://openbarcode.org/api/v1/products"
OPENBARCODE_SEARCH_API = "https://openbarcode.org/api/v1/search"


class OpenBarcodeError(ScraperError):
    """Error during Open Barcode lookup."""
    pass


def is_valid_upc_ean(code: str) -> bool:
    """Check if string looks like a valid UPC/EAN code (8-14 digits)."""
    code = code.strip()
    return code.isdigit() and 8 <= len(code) <= 14


def lookup_by_upc(upc_code: str) -> Optional[Product]:
    """Look up a product by UPC/EAN code using Open Barcode API.

    Args:
        upc_code: UPC or EAN code (8-14 digits)

    Returns:
        Product object if found, None otherwise

    Raises:
        OpenBarcodeError: If API call fails
    """
    if not is_valid_upc_ean(upc_code):
        return None

    try:
        # Try Open Barcode API endpoint
        url = f"{OPENBARCODE_API}/{upc_code}"
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers={"User-Agent": "BBW-Price-Tracker/1.0"}
        )

        if response.status_code == 404:
            logger.debug(f"UPC {upc_code} not found in Open Barcode database")
            return None

        if response.status_code != 200:
            raise OpenBarcodeError(
                f"Open Barcode API returned {response.status_code}: {response.text}"
            )

        data = response.json()
        return _parse_openbarcode_product(upc_code, data)

    except requests.RequestException as e:
        raise OpenBarcodeError(f"Failed to connect to Open Barcode API: {e}") from e
    except (ValueError, KeyError) as e:
        raise OpenBarcodeError(f"Failed to parse Open Barcode response: {e}") from e


def search_by_keyword(query: str) -> Optional[Product]:
    """Search Open Barcode for products by keyword.

    Args:
        query: Product name or keyword

    Returns:
        First matching Product, or None if not found

    Raises:
        OpenBarcodeError: If API call fails
    """
    if not query or len(query) < 2:
        return None

    try:
        response = requests.get(
            OPENBARCODE_SEARCH_API,
            params={"q": query},
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers={"User-Agent": "BBW-Price-Tracker/1.0"}
        )

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise OpenBarcodeError(
                f"Open Barcode search API returned {response.status_code}: {response.text}"
            )

        data = response.json()
        if not data or "results" not in data or not data["results"]:
            return None

        # Take the first result
        first_result = data["results"][0]
        upc = first_result.get("code", "")
        return _parse_openbarcode_product(upc, first_result)

    except requests.RequestException as e:
        raise OpenBarcodeError(f"Failed to search Open Barcode: {e}") from e
    except (ValueError, KeyError) as e:
        raise OpenBarcodeError(f"Failed to parse Open Barcode response: {e}") from e


def _parse_openbarcode_product(upc: str, data: Dict[str, Any]) -> Optional[Product]:
    """Parse Open Barcode API response into a Product object.

    Args:
        upc: The UPC/EAN code
        data: API response data

    Returns:
        Product object or None if required fields missing
    """
    try:
        # Extract available fields from Open Barcode response
        name = data.get("name") or data.get("title") or "Unknown Product"
        brand = data.get("brand", "")
        category = data.get("category", "")

        # Build product name with brand if available
        if brand:
            full_name = f"{brand} {name}".strip()
        else:
            full_name = name

        # Open Barcode doesn't provide pricing, so set placeholder values
        # User should verify pricing from actual retailer
        sku = data.get("sku") or upc

        return Product(
            name=full_name,
            sku=sku,
            original_price="$0.00",  # Not available from Open Barcode
            current_price="N/A",  # Not available from Open Barcode
            promo_text="Verify pricing on retailer site",
            in_stock="Unknown",  # Not available from Open Barcode
            product_url="",  # Not available from Open Barcode
        )

    except (KeyError, ValueError) as e:
        logger.warning(f"Failed to parse Open Barcode data for UPC {upc}: {e}")
        return None
