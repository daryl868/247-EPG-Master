from flask import Blueprint, render_template
from services.system_service import provider_summary, xml_files, git_status, recent_log
from services.db_service import recent_ocr_results

operations_bp = Blueprint("operations", __name__)

@operations_bp.route("/")
def operations():
    providers, total_channels, total_ocr = provider_summary()
    rows = recent_ocr_results(30)

    return render_template(
        "operations.html",
        providers=providers,
        total_channels=total_channels,
        total_ocr=total_ocr,
        xml_files=xml_files(),
        git_status=git_status(),
        logs=recent_log(80),
        rows=rows
    )
