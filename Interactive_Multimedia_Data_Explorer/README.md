# Interactive Multimedia Data Explorer

A simple runnable Python mini project based on the PIMV lab manual.

## Libraries used
- Streamlit — interactive web dashboard (Experiment 4)
- Pandas — CSV data handling
- Plotly — interactive charts (Experiment 2)
- Pillow — image processing and filters (Experiment 7)

## Features
- Upload a CSV or explore the included sample data
- Filter categorical and numeric values
- View dataset preview, summary statistics, missing values and data types
- Create interactive bar, line, scatter, histogram, box and pie charts
- Upload images, apply filters, resize and download edited images

## Run on Windows
1. Install Python 3.10 or newer.
2. Extract this ZIP folder.
3. Open Command Prompt / terminal in the extracted project folder.
4. Install libraries:
   ```bash
   python -m pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python -m streamlit run app.py
   ```
6. Open the local URL printed in the terminal (usually http://localhost:8501).

## Notes
- No API key or internet connection is required for the Python app itself.
- Plotly map tiles are not used; the app's charts work locally.
- If `streamlit` is not recognized, use `python -m streamlit run app.py`.
