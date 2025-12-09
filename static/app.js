const tableBody = document.getElementById("companyTableBody");
const sectorFilter = document.getElementById("sectorFilter");
const rankFilter = document.getElementById("rankFilter");
const searchInput = document.getElementById("searchInput");
const companyCount = document.getElementById("companyCount");

const detailsCard = document.getElementById("detailsCard");
const newsCard = document.getElementById("newsCard");
const detailName = document.getElementById("detailName");
const detailTicker = document.getElementById("detailTicker");
const detailSector = document.getElementById("detailSector");
const detailRank = document.getElementById("detailRank");
const detailIndia = document.getElementById("detailIndia");
const detailTN = document.getElementById("detailTN");
const detailAbout = document.getElementById("detailAbout");
const newsList = document.getElementById("newsList");
const newsSourceNote = document.getElementById("newsSourceNote");

async function loadCompanies() {
  const sector = sectorFilter.value;
  const rank = rankFilter.value;
  const q = searchInput.value.trim();

  const params = new URLSearchParams();
  if (sector) params.append("sector", sector);
  if (rank) params.append("rank", rank);
  if (q) params.append("q", q);

  const res = await fetch(`/api/companies?${params.toString()}`);
  const data = await res.json();
  renderCompanyTable(data);
}

function renderCompanyTable(data) {
  tableBody.innerHTML = "";
  companyCount.textContent = `${data.length} companies`;

  if (!data.length) {
    detailsCard.style.display = "none";
    newsCard.style.display = "none";
    return;
  }

  data.forEach((c, idx) => {
    const tr = document.createElement("tr");
    tr.style.cursor = "pointer";

    const rankColor = c.rank_color || "#ffffff";

    tr.innerHTML = `
      <td>${c.company_name}</td>
      <td>${c.ticker}</td>
      <td>${c.sector || ""}</td>
      <td style="background-color:${rankColor};">${c.rank ?? ""}</td>
      <td>${c.present_in_india || ""}</td>
      <td>${c.present_in_tn || ""}</td>
    `;

    tr.addEventListener("click", () => {
      showDetails(c);
      loadNews(c.ticker);
    });

    tableBody.appendChild(tr);

    if (idx === 0) {
      showDetails(c);
      loadNews(c.ticker);
    }
  });
}

function showDetails(c) {
  detailsCard.style.display = "block";

  detailName.textContent = c.company_name;
  detailTicker.textContent = c.ticker;
  detailSector.textContent = c.sector || "";
  detailRank.textContent = c.rank ?? "";
  detailIndia.textContent = c.present_in_india || "";
  detailTN.textContent = c.present_in_tn || "";
  detailAbout.textContent = c.about || "No description available.";
}

async function loadNews(ticker) {
  newsCard.style.display = "block";
  newsList.innerHTML = `<li class="list-group-item">Loading news…</li>`;
  newsSourceNote.textContent = "";

  try {
    const res = await fetch(`/api/news/${encodeURIComponent(ticker)}`);
    const news = await res.json();
    newsList.innerHTML = "";

    if (!news || news.length === 0) {
      newsList.innerHTML =
        `<li class="list-group-item small text-muted">No recent news available.</li>`;
      return;
    }

    news.forEach(n => {
      const li = document.createElement("li");
      li.className = "list-group-item";
      li.innerHTML = `
        <a href="${n.url}" target="_blank" class="fw-semibold">${n.title}</a>
        <div class="small text-muted">
          ${(n.source || "")} ${(n.published || "")}
        </div>
      `;
      newsList.appendChild(li);
    });

    newsSourceNote.textContent =
      "News feed currently uses a placeholder endpoint. Connect a real news API in the backend.";
  } catch (e) {
    newsList.innerHTML =
      `<li class="list-group-item small text-muted">Error loading news.</li>`;
  }
}

sectorFilter.addEventListener("change", loadCompanies);
rankFilter.addEventListener("change", loadCompanies);

let searchTimeout = null;
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(loadCompanies, 300);
});

document.addEventListener("DOMContentLoaded", loadCompanies);
