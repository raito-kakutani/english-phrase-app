const loginForm = document.getElementById("login-form");
const loginEmailInput = document.getElementById("login-email");
const loginPasswordInput = document.getElementById("login-password");
const loginError = document.getElementById("login-error");

async function redirectIfAlreadyLoggedIn() {
  try {
    const response = await fetch("/api/auth/me", { credentials: "same-origin" });
    if (response.ok) {
      window.location.href = "./index.html";
    }
  } catch (error) {
    // Backend unreachable; stay on the login page.
  }
}

async function handleLogin(event) {
  event.preventDefault();
  loginError.textContent = "";

  const email = loginEmailInput.value.trim();
  const password = loginPasswordInput.value;

  if (!email || !password) {
    loginError.textContent = "メールアドレスとパスワードを入力してください。";
    return;
  }

  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    window.location.href = "./index.html";
  } catch (error) {
    loginError.textContent = error.message || "ログインに失敗しました。";
  }
}

loginForm.addEventListener("submit", handleLogin);

redirectIfAlreadyLoggedIn();
