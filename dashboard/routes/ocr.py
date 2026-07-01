from flask import Blueprint, render_template
from services.db_service import recent_ocr_results

ocr_bp = Blueprint("ocr", __name__)

@ocr_bp.route("/")
def review():
    rows = recent_ocr_results(100)
    return render_template("ocr_review.html", rows=rows)
