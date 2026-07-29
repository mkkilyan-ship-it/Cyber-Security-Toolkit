document.getElementById("hash-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = document.getElementById("hash-file").files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/hash", { method: "POST", body: formData });
  const data = await response.json();

  const resultCard = document.getElementById("hash-result");
  const list = document.getElementById("hash-list");
  resultCard.hidden = false;
  list.innerHTML = "";

  if (!response.ok) {
    list.innerHTML = `<li>${data.error || "Erreur."}</li>`;
    return;
  }

  Object.entries(data.hashes).forEach(([algo, digest]) => {
    const li = document.createElement("li");
    li.textContent = `${algo}: ${digest}`;
    list.appendChild(li);
  });
});

document.getElementById("verify-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = document.getElementById("verify-file").files[0];
  const expected = document.getElementById("verify-hash").value.trim();
  const statusEl = document.getElementById("verify-status");
  if (!file || !expected) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("expected_hash", expected);

  const response = await fetch("/api/verify", { method: "POST", body: formData });
  const data = await response.json();

  if (!response.ok) {
    statusEl.textContent = data.error || "Erreur.";
    statusEl.className = "status error";
    return;
  }

  if (data.match) {
    statusEl.textContent = `Correspondance (${data.algorithm}) : intégrité vérifiée.`;
    statusEl.className = "status success";
  } else {
    statusEl.textContent = `Aucune correspondance (${data.algorithm}). Empreinte calculée : ${data.computed_hash}`;
    statusEl.className = "status error";
  }
});
