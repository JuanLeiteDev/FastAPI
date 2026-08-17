const API_BASE = window.location.port === "5500" ? "http://127.0.0.1:8000" : window.location.origin;
const OTP_CODE_LENGTH = 6;
const RECOVERY_CODE_LENGTH = 16;

const ROUTES = {
  "login-view": "/entrar",
  "register-view": "/criar-conta",
  "email-view": "/confirmar-email",
  "two-factor-view": "/confirmar-2fa",
  "recovery-codes-view": "/codigos-recuperacao",
  "account-view": "/minha-conta",
};

const TITLES = {
  "login-view": "Entrar | Lumen",
  "register-view": "Criar conta | Lumen",
  "email-view": "Confirmar email | Lumen",
  "two-factor-view": "Verificação de segurança | Lumen",
  "recovery-codes-view": "Códigos de recuperação | Lumen",
  "account-view": "Minha conta | Lumen",
};

const state = {
  email: "",
  twoFactorConfigured: false,
  usingRecoveryCode: false,
  recoveryCodes: [],
  pendingUser: null,
  qrUrl: null,
};

const $ = (selector, parent = document) => parent.querySelector(selector);
const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      credentials: "include",
      ...options,
      headers: options.body instanceof FormData
        ? options.headers
        : { "Content-Type": "application/json", ...options.headers },
    });
  } catch (_) {
    throw new ApiError("Não foi possível ligar ao serviço. Tente novamente.", 0);
  }

  if (!response.ok) {
    let message = `Não foi possível concluir o pedido (${response.status}).`;
    try {
      const payload = await response.json();
      if (typeof payload.detail === "string") message = payload.detail;
      if (Array.isArray(payload.detail)) message = payload.detail.map((item) => item.msg).join(" ");
    } catch (_) {
      // Algumas respostas de erro podem não ter conteúdo JSON.
    }
    throw new ApiError(message, response.status);
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return response.json();
  if (contentType.startsWith("image/")) return response.blob();
  return response.text();
}

function saveFlow() {
  sessionStorage.setItem("lumen-auth-flow", JSON.stringify({
    email: state.email,
    twoFactorConfigured: state.twoFactorConfigured,
  }));
}

function restoreFlow() {
  try {
    const flow = JSON.parse(sessionStorage.getItem("lumen-auth-flow"));
    if (!flow) return;
    state.email = typeof flow.email === "string" ? flow.email : "";
    state.twoFactorConfigured = Boolean(flow.twoFactorConfigured);
  } catch (_) {
    sessionStorage.removeItem("lumen-auth-flow");
  }
}

function clearFlow() {
  state.email = "";
  state.twoFactorConfigured = false;
  sessionStorage.removeItem("lumen-auth-flow");
}

function clearRecoveryCodes() {
  state.recoveryCodes = [];
  state.pendingUser = null;
  $("#recovery-code-list").replaceChildren();
}

function showView(id, { replace = false, updateHistory = true } = {}) {
  $$(".view").forEach((view) => { view.hidden = view.id !== id; });
  document.title = TITLES[id] || "Lumen | Área reservada";

  if (updateHistory) {
    const method = replace ? "replaceState" : "pushState";
    if (window.location.pathname !== ROUTES[id]) history[method]({ view: id }, "", ROUTES[id]);
  }

  const heading = $(`#${id} h2`);
  if (heading) requestAnimationFrame(() => heading.focus({ preventScroll: true }));
}

function viewFromPath(pathname) {
  return Object.keys(ROUTES).find((view) => ROUTES[view] === pathname);
}

function toast(message, type = "success") {
  const node = document.createElement("div");
  node.className = `toast ${type === "error" ? "error" : ""}`;
  node.textContent = message;
  $("#toast-region").append(node);
  window.setTimeout(() => node.remove(), 4200);
}

function setBusy(target, busy, busyLabel = "A processar…") {
  const button = target.matches("button") ? target : $("button[type='submit']", target);
  if (!button) return;
  button.disabled = busy;
  const label = $("span", button) || button;
  if (busy) {
    button.dataset.label = label.textContent;
    label.textContent = busyLabel;
  } else if (button.dataset.label) {
    label.textContent = button.dataset.label;
    delete button.dataset.label;
  }
}

function validateForm(form) {
  const fields = $$('input', form);
  fields.forEach((input) => input.classList.toggle("invalid", !input.checkValidity()));
  if (fields.every((input) => input.checkValidity())) return true;
  toast("Verifique os campos assinalados.", "error");
  return false;
}

function handleAuthError(error) {
  if (error.status === 401 && /autenticado|token/i.test(error.message)) {
    clearFlow();
    showView("login-view", { replace: true });
    toast("A sua sessão de verificação expirou. Inicie sessão novamente.", "error");
    return;
  }
  toast(error.message, "error");
}

async function sendConfirmationEmail({ notify = true } = {}) {
  await api("/Autenticar/EnviarEmail", { method: "POST" });
  if (notify) toast("Enviámos um novo código para o seu email.");
}

async function enterEmailStep() {
  $("#confirmation-email").textContent = state.email || "o seu email";
  $("#email-code").value = "";
  showView("email-view");
  await sendConfirmationEmail({ notify: false });
  $("#email-code").focus();
}

async function enterTwoFactorStep(needsSetup) {
  state.twoFactorConfigured = !needsSetup;
  saveFlow();
  showView("two-factor-view");
  $("#otp-code").value = "";
  const qrArea = $("#qr-area");
  const recoveryToggle = $("#toggle-recovery-code");
  setTwoFactorMode(false);
  recoveryToggle.hidden = needsSetup;

  if (!needsSetup) {
    $("#two-factor-title").textContent = "Código de segurança";
    $("#two-factor-description").textContent = "Introduza o código da sua aplicação autenticadora.";
    qrArea.hidden = true;
    $("#otp-code").focus();
    return;
  }

  $("#two-factor-title").textContent = "Ativar segurança 2FA";
  $("#two-factor-description").textContent = "Leia o QR Code e confirme com o código gerado.";
  qrArea.hidden = false;
  qrArea.innerHTML = '<div class="qr-loading" aria-label="A preparar QR Code"></div>';

  try {
    const blob = await api("/Autenticar/Ativar2FA", { method: "POST" });
    if (state.qrUrl) URL.revokeObjectURL(state.qrUrl);
    state.qrUrl = URL.createObjectURL(blob);
    const image = document.createElement("img");
    image.src = state.qrUrl;
    image.alt = "QR Code para configurar autenticação em dois fatores";
    qrArea.replaceChildren(image);
    $("#otp-code").focus();
  } catch (error) {
    handleAuthError(error);
  }
}

function setTwoFactorMode(useRecoveryCode) {
  state.usingRecoveryCode = useRecoveryCode;
  const input = $("#otp-code");
  const toggle = $("#toggle-recovery-code");

  input.value = "";
  input.classList.remove("invalid");
  input.inputMode = useRecoveryCode ? "text" : "numeric";
  input.placeholder = useRecoveryCode ? "A1B2C3D4E5F60708" : "000000";
  input.minLength = useRecoveryCode ? RECOVERY_CODE_LENGTH : OTP_CODE_LENGTH;
  // O campo é partilhado pelos dois modos. O teto deve sempre comportar um
  // código de recuperação; o modo autenticador é limitado no evento de input.
  input.maxLength = RECOVERY_CODE_LENGTH;
  input.pattern = useRecoveryCode
    ? `[A-Fa-f0-9]{${RECOVERY_CODE_LENGTH}}`
    : `[0-9]{${OTP_CODE_LENGTH}}`;
  $("#otp-label").textContent = useRecoveryCode ? "Código de recuperação" : "Código de 6 dígitos";
  $("#two-factor-description").textContent = useRecoveryCode
    ? "Introduza um dos códigos de recuperação que guardou."
    : "Introduza o código da sua aplicação autenticadora.";
  toggle.textContent = useRecoveryCode
    ? "Usar aplicação autenticadora"
    : "Usar código de recuperação";
  input.focus();
}

function showRecoveryCodes(codes, user) {
  state.recoveryCodes = [...codes];
  state.pendingUser = user;
  const list = $("#recovery-code-list");
  list.replaceChildren(...codes.map((code) => {
    const item = document.createElement("li");
    item.textContent = code;
    return item;
  }));
  showView("recovery-codes-view", { replace: true });
}

function renderAccount(user) {
  const name = user.name || "Utilizador";
  const initials = name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
  $("#account-avatar").textContent = initials || "U";
  $("#account-name").textContent = name;
  $("#account-email").textContent = user.email;
  $("#account-role").textContent = user.admin ? "Administrador" : "Utilizador";
  $("#account-email-status").textContent = user.email_active ? "Confirmado" : "Por confirmar";
  $("#account-2fa").textContent = user.security_2fa_active ? "Ativa" : "Inativa";
  clearFlow();
  showView("account-view", { replace: true });
}

async function loadAccount({ notify = false } = {}) {
  try {
    const user = await api("/MinhaConta/");
    renderAccount(user);
    if (notify) toast("Dados atualizados.");
    return true;
  } catch (error) {
    if (notify) toast(error.message, "error");
    return false;
  }
}

$$('[data-go]').forEach((button) => button.addEventListener("click", () => {
  const destination = button.dataset.go;
  if (destination === "login-view") clearFlow();
  showView(destination);
}));

$$('.password-toggle').forEach((button) => button.addEventListener("click", () => {
  const input = document.getElementById(button.dataset.target);
  const visible = input.type === "text";
  input.type = visible ? "password" : "text";
  button.textContent = visible ? "Mostrar" : "Ocultar";
  button.setAttribute("aria-label", visible ? "Mostrar palavra-passe" : "Ocultar palavra-passe");
}));

$$('input').forEach((input) => input.addEventListener("input", () => input.classList.remove("invalid")));

$("#register-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!validateForm(form)) return;

  const password = $("#register-password").value;
  const confirmPassword = $("#register-confirm-password").value;
  if (password !== confirmPassword) {
    $("#register-confirm-password").classList.add("invalid");
    toast("As palavras-passe não coincidem.", "error");
    return;
  }

  setBusy(form, true);
  const email = $("#register-email").value.trim();
  try {
    await api("/Autenticar/CriarConta", {
      method: "POST",
      body: JSON.stringify({
        name: $("#register-name").value.trim(),
        email,
        password,
        confirm_password: confirmPassword,
      }),
    });
    form.reset();
    $("#login-email").value = email;
    showView("login-view", { replace: true });
    $("#login-password").focus();
    toast("Conta criada. Inicie sessão para continuar.");
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
    state.email = $("#login-email").value.trim();
    const result = await api("/Autenticar/Entrar", {
      method: "POST",
      body: JSON.stringify({ email: state.email, password: $("#login-password").value }),
    });
    state.twoFactorConfigured = Boolean(result.auth2fa);
    saveFlow();

    if (!result.email) await enterEmailStep();
    else await enterTwoFactorStep(!result.auth2fa);
  } catch (error) {
    handleAuthError(error);
  } finally {
    setBusy(form, false);
  }
});

$("#email-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!validateForm(form)) return;
  setBusy(form, true);

  try {
    await api("/Autenticar/ConfirmarEmail", {
      method: "POST",
      body: JSON.stringify({ temporary_code: $("#email-code").value.trim() }),
    });
    toast("Email confirmado.");
    await enterTwoFactorStep(!state.twoFactorConfigured);
  } catch (error) {
    handleAuthError(error);
  } finally {
    setBusy(form, false);
  }
});

$("#resend-email").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  setBusy(button, true, "A enviar…");
  try {
    await sendConfirmationEmail();
  } catch (error) {
    handleAuthError(error);
  } finally {
    setBusy(button, false);
  }
});

$$('.code-input').forEach((input) => input.addEventListener("input", (event) => {
  if (event.target.id === "otp-code" && state.usingRecoveryCode) {
    event.target.value = event.target.value
      .replace(/[^A-Fa-f0-9]/g, "")
      .toUpperCase()
      .slice(0, RECOVERY_CODE_LENGTH);
    return;
  }
  event.target.value = event.target.value.replace(/\D/g, "").slice(0, OTP_CODE_LENGTH);
}));

$("#toggle-recovery-code").addEventListener("click", () => {
  setTwoFactorMode(!state.usingRecoveryCode);
});

$("#otp-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!validateForm(form)) return;
  setBusy(form, true);

  try {
    const otp = $("#otp-code").value;
    const result = await api("/Autenticar/Confirmar2FA", {
      method: "POST",
      body: JSON.stringify({ otp }),
    });
    if (Array.isArray(result.codigos) && result.codigos.length) {
      showRecoveryCodes(result.codigos, result.usuario);
      toast("2FA ativado. Guarde os códigos de recuperação.");
    } else {
      renderAccount(result.usuario);
      toast(state.usingRecoveryCode ? "Código de recuperação aceite." : "Sessão iniciada com segurança.");
    }
  } catch (error) {
    $("#otp-code").value = "";
    $("#otp-code").classList.add("invalid");
    $("#otp-code").focus();
    handleAuthError(error);
  } finally {
    setBusy(form, false);
  }
});

$("#copy-recovery-codes").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(state.recoveryCodes.join("\n"));
    toast("Códigos copiados.");
  } catch (_) {
    toast("Não foi possível copiar. Utilize a opção de descarregar.", "error");
  }
});

$("#download-recovery-codes").addEventListener("click", () => {
  const content = [
    "Lumen — Códigos de recuperação 2FA",
    "Cada código pode ser utilizado uma única vez.",
    "",
    ...state.recoveryCodes,
  ].join("\n");
  const url = URL.createObjectURL(new Blob([content], { type: "text/plain;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "lumen-codigos-recuperacao.txt";
  link.click();
  URL.revokeObjectURL(url);
});

$("#finish-recovery-codes").addEventListener("click", () => {
  const user = state.pendingUser;
  clearRecoveryCodes();
  if (user) renderAccount(user);
});

$("#refresh-account").addEventListener("click", () => loadAccount({ notify: true }));

$("#logout-button").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  setBusy(button, true, "A terminar…");
  try {
    await api("/MinhaConta/Sair", { method: "POST" });
    clearFlow();
    $("#login-form").reset();
    showView("login-view", { replace: true });
    toast("Sessão terminada.");
  } catch (error) {
    toast(error.message, "error");
  } finally {
    setBusy(button, false);
  }
});

window.addEventListener("popstate", async () => {
  const requestedView = viewFromPath(window.location.pathname) || "login-view";
  if (["account-view", "recovery-codes-view"].includes(requestedView) && !(await loadAccount())) {
    showView("login-view", { replace: true });
    return;
  }
  showView(requestedView, { updateHistory: false });
});

(async function init() {
  restoreFlow();
  $("#current-year").textContent = new Date().getFullYear();
  const requestedView = viewFromPath(window.location.pathname);

  if (await loadAccount()) return;

  if (requestedView === "register-view") {
    showView("register-view", { replace: true });
    return;
  }

  if (requestedView === "email-view" && state.email) {
    $("#confirmation-email").textContent = state.email;
    showView("email-view", { replace: true });
    return;
  }

  if (requestedView === "two-factor-view" && state.email) {
    await enterTwoFactorStep(!state.twoFactorConfigured);
    return;
  }

  showView("login-view", { replace: true });
})();
