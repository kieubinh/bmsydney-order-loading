# Setting Up OCR (Image Upload Feature)

## Step 1 — Install Python packages
Open a terminal/command prompt and run:
```
pip install pytesseract opencv-python pillow pdf2image
```

## Step 2 — Install Tesseract OCR engine (Windows)
1. Download the installer from:
   https://github.com/UB-Mannheim/tesseract/wiki
   
2. Run the installer — use the **default path**:
   `C:\Program Files\Tesseract-OCR\tesseract.exe`

3. During install, make sure **"Add to PATH"** is checked.

## Step 3 — Restart the app
```
python app.py
```

## Verify it works
Open a terminal and run:
```
tesseract --version
```
You should see a version number like `tesseract 5.x.x`

## Tips for best OCR results
- Use a clear, well-lit photo or scanned PDF
- Each row should be: `ITEM_CODE   QUANTITY`
- Printed/typed text works much better than handwriting
- Minimum image width: 400px
