document.getElementById("scanner-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    host: document.getElementById("scan-host").value.trim(),
    start_port: Number(document.getElementById("scan-start").value),
    end_port: Number(document.getElementById("scan-end").value),
  };

  const resultCard = document.getElementById("scanner-result");
  const summary = document.getElementById("scanner-summary");
  const tbody = document.querySelector("#scanner-table tbody");

  resultCard.hidden = false;
  summary.textContent = "Analyse en cours...";
  tbody.innerHTML = "";

  const response = await fetch("/api/scan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();

  if (!response.ok) {
    summary.textContent = data.error || "Erreur lors de l'analyse.";
    return;
  }

  summary.textContent = `${data.scanned_ports} ports analysés sur ${data.host} (${data.resolved_host}) en ${data.duration_seconds}s - ${data.open_ports.length} port(s) ouvert(s).`;

  data.open_ports.forEach((entry) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${entry.port}</td><td>${entry.service}</td>`;
    tbody.appendChild(row);
  });
});
