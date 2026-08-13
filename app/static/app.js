const API_BASE = window.location.port === "5500" ? "http://127.0.0.1:8000" : window.location.origin;

const state = { qrUrl: null };
const $ = (selector, parent = document) => parent.querySelector(selector);
const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...options,
    headers: options.body instanceof FormData ? options.headers : {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let message = `Pedido recusado (${response.status}).`;
    try {
      const payload = await response.json();
      if (typeof payload.detail === "string") message = payload.detail;
      if (Array.isArray(payload.detail)) message = payload.detail.map((item) => item.msg).join(" ");
    } catch (_) { /* A resposta pode não ser JSON. */ }
    throw new Error(message);
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return response.json();
  if (contentType.startsWith("image/")) return response.blob();
  return response.text();
}

function setApiStatus(online) {
  $("#status-dot").className = `status-dot ${online ? "online" : "offline"}`;
  $("#api-status").textContent = online ? "API ligada" : "API indisponível";
}

function toast(message, type = "success") {
  const node = document.createElement("div");
  node.className = `toast ${type === "error" ? "error" : ""}`;
  node.textContent = message;
  $("#toast-region").append(node);
  window.setTimeout(() => node.remove(), 4500);
}

function setBusy(form, busy) {
  const button = $("button[type='submit']", form);
  if (!button) return;
  button.disabled = busy;
  const label = $("span", button);
  if (busy) {
    button.dataset.label = label.textContent;
    label.textContent = "A processar…";
  } else if (button.dataset.label) {
    label.textContent = button.dataset.label;
  }
}

function setStep(number) {
  $$(".step").forEach((step) => step.classList.toggle("active", Number(step.dataset.step) <= number));
}

function showView(id) {
  $$(".view").forEach((view) => { view.hidden = view.id !== id; });
  setStep(id === "auth-view" ? 1 : id === "two-factor-view" ? 2 : 3);
}

function switchTab(tabName) {
  $$(".tab").forEach((tab) => {
    const active = tab.dataset.tab === tabName;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  $$(".tab-pane").forEach((pane) => {
    const active = pane.id === `${tabName}-pane`;
    pane.classList.toggle("active", active);
    pane.hidden = !active;
  });
}

function validateForm(form) {
  let valid = true;
  $$("input", form).forEach((input) => {
    const inputValid = input.checkValidity();
    input.classList.toggle("invalid", !inputValid);
    if (!inputValid) valid = false;
  });
  if (!valid) toast("Verifique os campos assinalados.", "error");
  return valid;
}

function resetOtp() {
  $$("#otp-inputs input").forEach((input) => { input.value = ""; input.classList.remove("invalid"); });
}

async function prepareTwoFactor(needsSetup) {
  showView("two-factor-view");
  resetOtp();
  const qrArea = $("#qr-area");

  if (!needsSetup) {
    $("#two-factor-title").textContent = "Confirme que é mesmo você";
    $("#two-factor-description").textContent = "Introduza o código atual da sua aplicação autenticadora.";
    qrArea.hidden = true;
    $("#otp-inputs input").focus();
    return;
  }

  $("#two-factor-title").textContent = "Proteja a sua conta";
  $("#two-factor-description").textContent = "Leia o QR Code com a sua aplicação autenticadora e insira o código gerado.";
  qrArea.hidden = false;
  qrArea.innerHTML = '<div class="qr-placeholder"><span></span></div><small>A preparar QR Code seguro…</small>';

  try {
    const blob = await api("/Autenticar/Ativar2FA", { method: "POST" });
    if (state.qrUrl) URL.revokeObjectURL(state.qrUrl);
    state.qrUrl = URL.createObjectURL(blob);
    qrArea.innerHTML = "";
    const image = document.createElement("img");
    image.src = state.qrUrl;
    image.alt = "QR Code para configurar autenticação em dois fatores";
    const caption = document.createElement("small");
    caption.textContent = "Leia com a sua aplicação autenticadora";
    qrArea.append(image, caption);
    $("#otp-inputs input").focus();
  } catch (error) {
    showView("auth-view");
    toast(error.message, "error");
  }
}

function renderAccount(user) {
  const initials = user.name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
  $("#account-avatar").textContent = initials || "U";
  $("#account-name").textContent = user.name;
  $("#account-email").textContent = user.email;
  $("#account-id").textContent = `#${user.id}`;
  $("#account-status").textContent = user.status ? "Ativa" : "Inativa";
  $("#account-role").textContent = user.admin ? "Administrador" : "Utilizador";
  $("#account-2fa").textContent = user.security_2fa_active ? "Ativa" : "Inativa";
  showView("account-view");
}

async function loadAccount({ silent = false } = {}) {
  try {
    const user = await api("/MinhaConta/");
    setApiStatus(true);
    renderAccount(user);
    if (!silent) toast("Dados atualizados.");
    return true;
  } catch (error) {
    if (error.message !== "Não autenticado." && !silent) toast(error.message, "error");
    return false;
  }
}

$$('.tab').forEach((tab) => tab.addEventListener("click", () => switchTab(tab.dataset.tab)));

$$('.password-toggle').forEach((button) => button.addEventListener("click", () => {
  const input = document.getElementById(button.dataset.target);
  input.type = input.type === "password" ? "text" : "password";
  button.classList.toggle("visible", input.type === "text");
  button.setAttribute("aria-label", input.type === "text" ? "Ocultar palavra-passe" : "Mostrar palavra-passe");
}));

$("#register-password").addEventListener("input", (event) => {
  const password = event.target.value;
  let score = password.length >= 8 ? 1 : 0;
  if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score += 1;
  if (/\d/.test(password) && /[^A-Za-z0-9]/.test(password)) score += 1;
  $$(".password-meter > span").forEach((bar, index) => bar.classList.toggle("filled", index < score));
  $("#password-hint").textContent = score === 3 ? "Palavra-passe forte" : score === 2 ? "Boa palavra-passe" : "Use 8 ou mais caracteres";
});

$("#register-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!validateForm(form)) return;
  setBusy(form, true);
  try {
    const user = await api("/Autenticar/CriarConta", {
      method: "POST",
      body: JSON.stringify({
        name: $("#register-name").value.trim(),
        email: $("#register-email").value.trim(),
        password: $("#register-password").value,
      }),
    });
    $("#login-email").value = user.email;
    $("#login-password").value = "";
    form.reset();
    switchTab("login");
    toast("Conta criada. Já pode iniciar sessão.");
  } catch (error) {
    toast(error.message, "error");
  } finally {
    setBusy(form, false);
  }
});

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!validateForm(form)) return;
  setBusy(form, true);
  try {
    const result = await api("/Autenticar/Entrar", {
      method: "POST",
      body: JSON.stringify({ email: $("#login-email").value.trim(), password: $("#login-password").value }),
    });
    await prepareTwoFactor(!result.active);
  } catch (error) {
    toast(error.message, "error");
  } finally {
    setBusy(form, false);
  }
});

const otpInputs = $$("#otp-inputs input");
otpInputs.forEach((input, index) => {
  input.addEventListener("input", () => {
    input.value = input.value.replace(/\D/g, "").slice(-1);
    input.classList.remove("invalid");
    if (input.value && index < otpInputs.length - 1) otpInputs[index + 1].focus();
    if (otpInputs.every((item) => item.value) && index === otpInputs.length - 1) $("#otp-form").requestSubmit();
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "Backspace" && !input.value && index > 0) otpInputs[index - 1].focus();
  });
  input.addEventListener("paste", (event) => {
    const digits = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (!digits) return;
    event.preventDefault();
    digits.split("").forEach((digit, digitIndex) => { if (otpInputs[digitIndex]) otpInputs[digitIndex].value = digit; });
    otpInputs[Math.min(digits.length, 6) - 1].focus();
    if (digits.length === 6) $("#otp-form").requestSubmit();
  });
});

$("#otp-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const otp = otpInputs.map((input) => input.value).join("");
  if (!/^\d{6}$/.test(otp)) {
    otpInputs.forEach((input) => input.classList.add("invalid"));
    toast("Introduza os seis dígitos do código.", "error");
    return;
  }
  setBusy(form, true);
  try {
    const user = await api(`/Autenticar/Confirmar2FA?otp=${encodeURIComponent(otp)}`, { method: "POST" });
    renderAccount(user);
    toast("Sessão iniciada com segurança.");
  } catch (error) {
    resetOtp();
    otpInputs.forEach((input) => input.classList.add("invalid"));
    otpInputs[0].focus();
    toast(error.message, "error");
  } finally {
    setBusy(form, false);
  }
});

$("#back-to-login").addEventListener("click", () => showView("auth-view"));
$("#refresh-account").addEventListener("click", () => loadAccount());
$("#logout-button").addEventListener("click", async () => {
  try {
    await api("/MinhaConta/Sair", { method: "POST" });
    showView("auth-view");
    switchTab("login");
    $("#login-password").value = "";
    toast("Sessão terminada.");
  } catch (error) {
    toast(error.message, "error");
  }
});

(async function init() {
  try {
    const response = await fetch(`${API_BASE}/openapi.json`, { credentials: "include" });
    setApiStatus(response.ok);
  } catch (_) {
    setApiStatus(false);
  }
  await loadAccount({ silent: true });
})();
