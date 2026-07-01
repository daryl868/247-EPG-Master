from flask import Blueprint, jsonify  # type: ignore[import]
from services.db_service import recent_ocr_results

api_bp = Blueprint("api", __name__)

@api_bp.route("/ocr/status")
def ocr_status():
    rows = recent_ocr_results(200)
    return jsonify([dict(r) for r in rows])