from flask import Blueprint, render_template
from services.system_service import (
    provider_summary,
    xml_files,
    git_status,
    git_branch,
    git_last_commit,
    recent_log,
    metadata_cache_count,
    correction_count,
    cron_status,
)

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def home():
    providers, total_channels, total_ocr = provider_summary()
    xml = xml_files()

    stats = {
        "providers": len(providers),
        "channels": total_channels,
        "ocr_enabled": total_ocr,
        "xml_files": len(xml),
        "metadata_cache": metadata_cache_count(),
        "corrections": correction_count(),
        "cron": cron_status(),
        "branch": git_branch(),
        "last_commit": git_last_commit(),
    }

    return render_template(
        "dashboard.html",
        providers=providers,
        xml_files=xml,
        git_status=git_status(),
        logs=recent_log(),
        stats=stats
    )
