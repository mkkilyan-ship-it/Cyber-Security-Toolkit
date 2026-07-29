const lengthInput = document.getElementById("pw-length");
const lengthValue = document.getElementById("length-value");

lengthInput.addEventListener("input", () => {
  lengthValue.textContent = lengthInput.value;
});

document.getElementById("password-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    length: Number(lengthInput.value),
    upper: document.getElementById("pw-upper").checked,
    lower: document.getElementById("pw-lower").checked,
    digits: document.getElementById("pw-digits").checked,
    symbols: document.getElementById("pw-symbols").checked,
    exclude_ambiguous: document.getElementById("pw-ambiguous").checked,
  };

  const response = await fetch("/api/password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();

  const resultCard = document.getElementById("password-result");
  if (!response.ok) {
    resultCard.hidden = false;
    document.getElementById("password-output").textContent = data.error || "Erreur";
    return;
  }

  resultCard.hidden = false;
  document.getElementById("password-output").textContent = data.password;

  const ratingToPercent = { faible: 25, moyen: 50, fort: 75, excellent: 100 };
  const ratingToColor = { faible: "#e5484d", moyen: "#e5b73b", fort: "#39d98a", excellent: "#39d98a" };
  const fill = document.getElementById("strength-fill");
  fill.style.width = `${ratingToPercent[data.rating] || 0}%`;
  fill.style.background = ratingToColor[data.rating] || "#e5484d";

  document.getElementById("strength-label").textContent =
    `${data.rating} (${data.entropy_bits} bits d'entropie)`;
});

document.getElementById("copy-password").addEventListener("click", async () => {
  const text = document.getElementById("password-output").textContent;
  if (!text) return;
  await navigator.clipboard.writeText(text);

  const btn = document.getElementById("copy-password");
  const original = btn.textContent;
  btn.textContent = "Copié !";
  setTimeout(() => { btn.textContent = original; }, 1500);
});
