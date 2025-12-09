from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

# ---------- CONFIG ----------
EXCEL_PATH = "Top-100-companies-rule-finbert-ranked.xlsx"  # exact filename from repo[file:1]
SHEET_NAME = "Sheet1"
RANK_COL = "Expansion_Rank"
SECTOR_COL = "BICS L1 Sect Nm"

# ---------- LOAD DATA ----------
if not os.path.exists(EXCEL_PATH):
    raise FileNotFoundError(f"Excel file not found at {EXCEL_PATH}")

df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

DISPLAY_COLUMNS = [
    "Name",
    "Ticker",
    SECTOR_COL,
    RANK_COL,
    "Remarks",
    "Present in India (Yes/No)",
    "Present in TN (Yes/No)",
]

df_display = df[DISPLAY_COLUMNS].copy()

df_display = df_display.rename(columns={
    "Name": "company_name",
    "Ticker": "ticker",
    SECTOR_COL: "sector",
    RANK_COL: "rank",
    "Remarks": "about",
    "Present in India (Yes/No)": "present_in_india",
    "Present in TN (Yes/No)": "present_in_tn",
})

df_display = df_display.dropna(subset=["company_name", "ticker"])

def rank_to_color(rank):
    try:
        r = int(rank)
    except Exception:
        return "#ffffff"
    if r == 1:
        return "#c6efce"   # green
    if r == 2:
        return "#ffeb9c"   # yellow
    if r == 3:
        return "#ffc7ce"   # red
    if r == 4:
        return "#bdd7ee"   # blue
    return "#eeeeee"

df_display["rank_color"] = df_display["rank"].apply(rank_to_color)

all_sectors = sorted(df_display["sector"].dropna().unique().tolist())
all_ranks = sorted(df_display["rank"].dropna().unique().tolist())

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template(
        "index.html",
        sectors=all_sectors,
        ranks=all_ranks
    )

@app.route("/api/companies")
def api_companies():
    sector = request.args.get("sector", "").strip()
    rank = request.args.get("rank", "").strip()
    q = request.args.get("q", "").strip().lower()

    def is_all(value: str) -> bool:
        return value == "" or value.lower().startswith("all")

    filtered = df_display.copy()

    # Sector filter
    if not is_all(sector):
        filtered = filtered[filtered["sector"] == sector]

    # Rank filter
    if not is_all(rank):
        try:
            r_int = int(float(rank))
            filtered = filtered[filtered["rank"].astype("Int64") == r_int]
        except Exception:
            pass

    # Search filter
    if q:
        filtered = filtered[
            filtered["company_name"].str.lower().str.contains(q, na=False)
            | filtered["ticker"].str.lower().str.contains(q, na=False)
        ]

    return jsonify(filtered.to_dict(orient="records"))

@app.route("/api/news/<ticker>")
def api_news(ticker):
    # Placeholder – replace with real news API if needed
    dummy_news = [
        {
            "title": f"Latest strategic update for {ticker}",
            "url": "#",
            "source": "Placeholder",
            "published": "N/A",
        }
    ]
    return jsonify(dummy_news)

if __name__ == "__main__":
    app.run(debug=True)
