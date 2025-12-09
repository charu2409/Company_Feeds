from flask import Flask, render_template, jsonify, request
import pandas as pd

app = Flask(__name__)

# ---------- CONFIG ----------
EXCEL_PATH = "Top-100-companies-rule-finbert-ranked.xlsx"
SHEET_NAME = "Sheet1"  # change if different
RANK_COL = "Expansion_Rank"  # rank column name
SECTOR_COL = "BICS L1 Sect Nm"  # sector column
NEWS_LIMIT_PER_COMPANY = 5

# ---------- LOAD DATA ----------
df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

# Keep only needed columns for main grid
DISPLAY_COLUMNS = [
    "Name",                # company name
    "Ticker",              # ticker
    SECTOR_COL,            # sector
    RANK_COL,              # rank
    "Remarks",             # about the company (narrative)
    "Present in India (Yes/No)",
    "Present in TN (Yes/No)"
]

df_display = df[DISPLAY_COLUMNS].copy()

# Standardise column names for frontend
df_display = df_display.rename(columns={
    "Name": "company_name",
    "Ticker": "ticker",
    SECTOR_COL: "sector",
    RANK_COL: "rank",
    "Remarks": "about",
    "Present in India (Yes/No)": "present_in_india",
    "Present in TN (Yes/No)": "present_in_tn"
})

# Drop rows without company name or ticker
df_display = df_display.dropna(subset=["company_name", "ticker"])

# For dropdown filters
all_sectors = sorted(df_display["sector"].dropna().unique().tolist())
all_ranks = sorted(df_display["rank"].dropna().unique().tolist())


# ---------- SIMPLE RANK→COLOR MAPPING ----------
# Adjust colours to exactly match your Excel legend if needed
def rank_to_color(rank):
    try:
        r = int(rank)
    except Exception:
        return "#ffffff"
    if r == 1:
        return "#c6efce"  # light green
    if r == 2:
        return "#ffeb9c"  # light yellow
    if r == 3:
        return "#ffc7ce"  # light red
    if r == 4:
        return "#bdd7ee"  # light blue
    return "#eeeeee"


df_display["rank_color"] = df_display["rank"].apply(rank_to_color)


# ---------- HOME PAGE ----------
@app.route("/")
def index():
    return render_template(
        "index.html",
        sectors=all_sectors,
        ranks=all_ranks
    )


# ---------- API: COMPANY LIST WITH FILTERS ----------
@app.route("/api/companies")
def api_companies():
    sector = request.args.get("sector")
    rank = request.args.get("rank")

    filtered = df_display.copy()

    if sector and sector != "ALL":
        filtered = filtered[filtered["sector"] == sector]

    if rank and rank != "ALL":
        try:
            r_int = int(rank)
            filtered = filtered[filtered["rank"] == r_int]
        except Exception:
            pass

    data = filtered.to_dict(orient="records")
    return jsonify(data)


# ---------- API: RECENT NEWS (dummy placeholder) ----------
# You will replace this with a real news API (e.g. NewsAPI, GNews, Bing, etc.)
@app.route("/api/news/<ticker>")
def api_news(ticker):
    # Minimal static placeholder; integrate external API here
    # Example: call your news API with company name / ticker and return JSON
    dummy_news = [
        {
            "title": f"Latest strategic update for {ticker}",
            "url": "#",
            "source": "Internal / Placeholder",
            "published": "N/A"
        }
    ]
    return jsonify(dummy_news[:NEWS_LIMIT_PER_COMPANY])


if __name__ == "__main__":
    app.run(debug=True)
