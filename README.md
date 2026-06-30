# EPG Vision

A master 24/7 XMLTV and M3U platform with OCR-ready stream scanning.

## Upload structure

Keep all folders exactly as provided:

- `config/`
- `providers/`
- `scripts/`
- `generated/`
- `.github/workflows/`

## First run

After uploading to GitHub:

1. Go to **Actions**
2. Run **Build EPG Vision**
3. Enable GitHub Pages:
   - Settings → Pages
   - Deploy from branch
   - Branch: `main`
   - Folder: `/(root)`

## URLs

If the repo is named `EPG-Vision`, the combined XMLTV URL will be:

`https://daryl868.github.io/EPG-Vision/generated/all_247_epg.xml`

The combined M3U URL will be:

`https://daryl868.github.io/EPG-Vision/generated/all_247.m3u`

## OCR

OCR is included but disabled by default in GitHub Actions until crop profiles are tuned.

Manual OCR scan example:

`python scripts/scan_streams.py providers/netflix_series.json`

Debug OCR crops are saved in:

`cache/crops/`
