# EPG Vision Studio v1

## Install

```bash
sudo apt update
sudo apt install -y ffmpeg tesseract-ocr python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Test Peacock OCR

```bash
python scripts/test_ocr.py providers/peacock.json 0
```

## Build XML/M3U

```bash
python scripts/build_epg.py
```

## Run Dashboard

```bash
python dashboard/app.py
```

Open `http://SERVER-IP:5050`.
