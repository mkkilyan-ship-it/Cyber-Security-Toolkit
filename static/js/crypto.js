async function submitCryptoForm(endpoint, fileInput, passwordInput, statusEl) {
  const file = fileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("password", passwordInput.value);

  const response = await fetch(endpoint, { method: "POST", body: formData });

  if (!response.ok) {
    const data = await response.json();
    statusEl.textContent = data.error || "Erreur.";
    statusEl.className = "status error";
    return;
  }

  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match ? match[1] : "fichier_sortie";

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);

  statusEl.textContent = `Fichier "${filename}" généré et téléchargé.`;
  statusEl.className = "status success";
}

document.getElementById("encrypt-form").addEventListener("submit", (event) => {
  event.preventDefault();
  submitCryptoForm(
    "/api/encrypt",
    document.getElementById("encrypt-file"),
    document.getElementById("encrypt-password"),
    document.getElementById("crypto-status"),
  );
});

document.getElementById("decrypt-form").addEventListener("submit", (event) => {
  event.preventDefault();
  submitCryptoForm(
    "/api/decrypt",
    document.getElementById("decrypt-file"),
    document.getElementById("decrypt-password"),
    document.getElementById("crypto-status"),
  );
});
