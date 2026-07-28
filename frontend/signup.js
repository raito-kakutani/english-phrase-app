const signupForm = document.getElementById("signup-form");
const signupEmailInput = document.getElementById("signup-email");
const signupPasswordInput = document.getElementById("signup-password");
const signupError = document.getElementById("signup-error");

async function redirectIfAlreadyLoggedIn() {
  try {
    const response = await fetch("/api/auth/me", { credentials: "same-origin" });
    if (response.ok) {
      window.location.href = "./index.html";
    }
  } catch (error) {
    // Backend unreachable; stay on the signup page.
  }
}

async function handleSignup(event) {
  event.preventDefault();
  signupError.textContent = "";

  const email = signupEmailInput.value.trim();
  const password = signupPasswordInput.value;

  if (!email) {
    signupError.textContent = "メールアドレスを入力してください。";
    return;
  }

  if (password.length < 8) {
    signupError.textContent = "パスワードは8文字以上で入力してください。";
    return;
  }

  try {
    const signupResponse = await fetch("/api/auth/signup", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const signupData = await signupResponse.json();

    if (!signupResponse.ok) {
      throw new Error(signupData.detail || `HTTP ${signupResponse.status}`);
    }

    const loginResponse = await fetch("/api/auth/login", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!loginResponse.ok) {
      throw new Error("登録は完了しましたが、ログインに失敗しました。");
    }

    window.location.href = "./index.html";
  } catch (error) {
    signupError.textContent = error.message || "新規登録に失敗しました。";
  }
}

signupForm.addEventListener("submit", handleSignup);

redirectIfAlreadyLoggedIn();
