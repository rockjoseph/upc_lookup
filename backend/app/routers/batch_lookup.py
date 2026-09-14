"""Batch UPC/EAN lookup endpoint for processing Excel files.

Accepts an Excel file with UPC codes and returns product information
populated via Open Barcode database lookup.
"""
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from io import BytesIO
import openpyxl

from app.scraper.openbarcode_lookup import lookup_by_upc, is_valid_upc_ean, OpenBarcodeError

logger = logging.getLogger("batch_lookup")
router = APIRouter(prefix="/api/batch", tags=["batch"])


@router.post("/lookup-upcs")
async def batch_lookup_upcs(file: UploadFile = File(...)):
    """Process an Excel file and populate product names from UPC codes.

    Expected Excel format:
    - Column A: UPC/EAN codes
    - Column B: (Optional) Will be populated with product names

    Returns:
        Excel file with populated product names and metadata
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="File must be an Excel file (.xlsx or .xls)"
        )

    try:
        # Read uploaded file
        contents = await file.read()
        workbook = openpyxl.load_workbook(BytesIO(contents))
        worksheet = workbook.active

        results = []
        errors = []

        # Process each row
        for row_idx, row in enumerate(worksheet.iter_rows(values_only=False), start=1):
            if row_idx == 1:
                # Skip header if present
                continue

            upc_cell = row[0]
            if not upc_cell or not upc_cell.value:
                continue

            upc_code = str(upc_cell.value).strip()

            if not is_valid_upc_ean(upc_code):
                errors.append({
                    "row": row_idx,
                    "upc": upc_code,
                    "error": "Invalid UPC/EAN format (must be 8-14 digits)"
                })
                continue

            try:
                # Look up product in Open Barcode
                product = lookup_by_upc(upc_code)

                if product:
                    # Add product name to column B
                    name_cell = row[1] if len(row) > 1 else None
                    if name_cell is None:
                        # Create cell if it doesn't exist
                        name_cell = worksheet.cell(row=row_idx, column=2)

                    name_cell.value = product.name

                    # Add other details if columns exist
                    if len(row) > 2 and row[2]:
                        row[2].value = product.sku

                    if len(row) > 3 and row[3]:
                        row[3].value = product.current_price

                    results.append({
                        "row": row_idx,
                        "upc": upc_code,
                        "product_name": product.name,
                        "sku": product.sku,
                        "status": "found"
                    })
                else:
                    errors.append({
                        "row": row_idx,
                        "upc": upc_code,
                        "error": "Product not found in Open Barcode database"
                    })

            except OpenBarcodeError as e:
                errors.append({
                    "row": row_idx,
                    "upc": upc_code,
                    "error": f"Lookup error: {str(e)}"
                })

        # Save modified workbook to bytes
        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        return {
            "status": "success",
            "processed": len(results),
            "errors": len(errors),
            "results": results,
            "error_details": errors,
            "file": output.getvalue().hex()  # Return as hex string for JSON serialization
        }

    except Exception as e:
        logger.error(f"Batch lookup error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Excel file: {str(e)}"
        )


@router.get("/lookup/{upc}")
def quick_lookup(upc: str):
    """Quick lookup for a single UPC code.

    Args:
        upc: UPC/EAN code (8-14 digits)

    Returns:
        Product information from Open Barcode
    """
    if not is_valid_upc_ean(upc):
        raise HTTPException(
            status_code=400,
            detail="Invalid UPC/EAN format (must be 8-14 digits)"
        )

    try:
        product = lookup_by_upc(upc)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"UPC {upc} not found in Open Barcode database"
            )

        return {
            "status": "found",
            "upc": upc,
            "name": product.name,
            "sku": product.sku,
            "price": product.current_price,
            "note": "Pricing should be verified on retailer website"
        }

    except OpenBarcodeError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Open Barcode lookup failed: {str(e)}"
        )
