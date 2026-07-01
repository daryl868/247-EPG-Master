async function refreshOCR() {
    try {
        const response = await fetch("/api/ocr/status");
        const rows = await response.json();

        rows.forEach(r => {
            const id = `${r.provider_file}-${r.channel_index}`;

            const detected = document.getElementById(`detected-${id}`);
            const confidence = document.getElementById(`confidence-${id}`);
            const vote = document.getElementById(`vote-${id}`);
            const decision = document.getElementById(`decision-${id}`);
            const scan = document.getElementById(`scan-${id}`);
            const row = document.getElementById(`row-${id}`);

            if (!row) return;

            if (detected) detected.innerText = r.matched_title || "";
            if (confidence) confidence.innerText = r.confidence ?? "";
            if (vote) vote.innerText = r.vote_count ?? "";
            if (decision) {
                decision.innerText = r.decision || "";
                decision.className = "";
                if (r.decision === "ACCEPT") decision.classList.add("ok");
                else if (r.decision === "VERIFY") decision.classList.add("warn");
                else decision.classList.add("bad");
            }
            if (scan) scan.innerText = r.created_at || "";

            row.classList.add("updated");
            setTimeout(() => row.classList.remove("updated"), 1500);
        });
    } catch (err) {
        console.log("OCR refresh failed:", err);
    }
}

setInterval(refreshOCR, 5000);