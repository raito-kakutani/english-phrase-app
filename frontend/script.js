const japaneseInput = document.getElementById("japanese-input");
const englishInput = document.getElementById("english-input");
const submitButton = document.getElementById("submit-button");
const result = document.getElementById("result");
const screenButtons = document.querySelectorAll("[data-screen-target]");
const screens = document.querySelectorAll("[data-screen]");

const authView = document.getElementById("auth-view");
const appView = document.getElementById("app-view");
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const loginEmailInput = document.getElementById("login-email");
const loginPasswordInput = document.getElementById("login-password");
const loginError = document.getElementById("login-error");
const signupEmailInput = document.getElementById("signup-email");
const signupPasswordInput = document.getElementById("signup-password");
const signupError = document.getElementById("signup-error");
const showSignupButton = document.getElementById("show-signup-button");
const showLoginButton = document.getElementById("show-login-button");
const logoutButton = document.getElementById("logout-button");

function toDateStr(date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

const _now = new Date();
const _yesterday = new Date(_now);
_yesterday.setDate(_now.getDate() - 1);

const phraseViews = {
  "today-phrase": {
    endpoint: `/api/phrases/date/${toDateStr(_now)}`,
    countElement: document.getElementById("today-phrase-count"),
    japaneseElement: document.getElementById("today-phrase-text"),
    englishElement: document.getElementById("today-phrase-english"),
    showEnglishButton: document.getElementById("show-english-button"),
    prevButton: document.getElementById("prev-today-phrase-button"),
    nextButton: document.getElementById("next-today-phrase-button"),
    state: {
      phrases: [],
      currentIndex: 0,
      isEnglishVisible: false,
      hasPhrase: false,
    },
  },
  "yesterday-phrase": {
    endpoint: `/api/phrases/date/${toDateStr(_yesterday)}`,
    countElement: document.getElementById("yesterday-phrase-count"),
    japaneseElement: document.getElementById("yesterday-phrase-text"),
    englishElement: document.getElementById("yesterday-phrase-english"),
    showEnglishButton: document.getElementById("show-yesterday-english-button"),
    prevButton: document.getElementById("prev-yesterday-phrase-button"),
    nextButton: document.getElementById("next-yesterday-phrase-button"),
    state: {
      phrases: [],
      currentIndex: 0,
      isEnglishVisible: false,
      hasPhrase: false,
    },
  },
  "date-phrase": {
    endpoint: null,
    countElement: document.getElementById("date-phrase-count"),
    japaneseElement: document.getElementById("date-phrase-text"),
    englishElement: document.getElementById("date-phrase-english"),
    showEnglishButton: document.getElementById("show-date-english-button"),
    prevButton: document.getElementById("prev-date-phrase-button"),
    nextButton: document.getElementById("next-date-phrase-button"),
    state: {
      phrases: [],
      currentIndex: 0,
      isEnglishVisible: false,
      hasPhrase: false,
    },
  },
};

function showAppView() {
  authView.hidden = true;
  appView.hidden = false;
}

function showAuthView() {
  appView.hidden = true;
  authView.hidden = false;
  loginForm.hidden = false;
  signupForm.hidden = true;
}

function handleUnauthorized() {
  window.location.reload();
}

async function checkAuth() {
  try {
    const response = await fetch("/api/auth/me", { credentials: "same-origin" });
    if (response.ok) {
      showAppView();
    } else {
      showAuthView();
    }
  } catch (error) {
    showAuthView();
  }
}

async function handleLogin(event) {
  event.preventDefault();
  loginError.textContent = "";

  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: loginEmailInput.value.trim(),
        password: loginPasswordInput.value,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    window.location.reload();
  } catch (error) {
    loginError.textContent = error.message || "ログインに失敗しました。";
  }
}

async function handleSignup(event) {
  event.preventDefault();
  signupError.textContent = "";

  const email = signupEmailInput.value.trim();
  const password = signupPasswordInput.value;

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

    window.location.reload();
  } catch (error) {
    signupError.textContent = error.message || "新規登録に失敗しました。";
  }
}

async function handleLogout() {
  try {
    await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
  } finally {
    window.location.reload();
  }
}

function hasRequiredInputs() {
  return japaneseInput.value.trim() !== "" && englishInput.value.trim() !== "";
}

function updateSubmitButtonState() {
  submitButton.disabled = !hasRequiredInputs();
}

function getCurrentPhrase(view) {
  return view.state.phrases[view.state.currentIndex] ?? null;
}

function renderPhrase(view) {
  if (!view.state.hasPhrase) {
    view.countElement.textContent = "";
    view.japaneseElement.textContent = "";
    view.englishElement.textContent = "";
    view.englishElement.hidden = true;
    view.showEnglishButton.textContent = "英語表示";
    view.showEnglishButton.disabled = true;
    view.prevButton.disabled = true;
    view.nextButton.disabled = true;
    return;
  }

  const phrase = getCurrentPhrase(view);
  const total = view.state.phrases.length;
  const current = view.state.currentIndex + 1;

  view.countElement.textContent = `${current} / ${total}`;
  view.japaneseElement.textContent = phrase.japanese_text;
  view.englishElement.textContent = phrase.english_text;
  view.englishElement.hidden = !view.state.isEnglishVisible;
  view.showEnglishButton.textContent = view.state.isEnglishVisible ? "英語非表示" : "英語表示";
  view.showEnglishButton.disabled = false;
  view.prevButton.disabled = current <= 1;
  view.nextButton.disabled = current >= total;
}

function resetView(view) {
  view.state.phrases = [];
  view.state.currentIndex = 0;
  view.state.isEnglishVisible = false;
  view.state.hasPhrase = false;
  renderPhrase(view);
}

async function loadPhrase(screenName) {
  const view = phraseViews[screenName];
  if (!view || !view.endpoint) return;

  resetView(view);

  try {
    const response = await fetch(view.endpoint, { credentials: "same-origin" });

    if (response.status === 401) {
      handleUnauthorized();
      return;
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    view.state.phrases = Array.isArray(data) ? data : [];
    view.state.currentIndex = 0;
    view.state.isEnglishVisible = false;
    view.state.hasPhrase = view.state.phrases.length > 0;
    renderPhrase(view);
  } catch (error) {
    resetView(view);
  }
}

function toggleEnglish(view) {
  if (!view.state.hasPhrase) return;
  view.state.isEnglishVisible = !view.state.isEnglishVisible;
  renderPhrase(view);
}

function showNextPhrase(view) {
  if (!view.state.hasPhrase) return;

  const nextIndex = view.state.currentIndex + 1;
  if (nextIndex >= view.state.phrases.length) return;

  view.state.currentIndex = nextIndex;
  view.state.isEnglishVisible = false;
  renderPhrase(view);
}

function showPrevPhrase(view) {
  if (!view.state.hasPhrase) return;

  const prevIndex = view.state.currentIndex - 1;
  if (prevIndex < 0) return;

  view.state.currentIndex = prevIndex;
  view.state.isEnglishVisible = false;
  renderPhrase(view);
}

function switchScreen(screenName) {
  screens.forEach((screen) => {
    const isActive = screen.dataset.screen === screenName;
    screen.classList.toggle("is-active", isActive);
    screen.hidden = !isActive;
  });

  screenButtons.forEach((button) => {
    button.classList.toggle(
      "is-active",
      button.dataset.screenTarget === screenName,
    );
  });

  loadPhrase(screenName);
}

async function submitPhrases() {
  const japanese = japaneseInput.value.trim();
  const english = englishInput.value.trim();

  if (!hasRequiredInputs()) {
    updateSubmitButtonState();
    return;
  }

  result.textContent = "";
  submitButton.disabled = true;

  try {
    const response = await fetch("/api/phrases", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ japanese, english }),
    });

    if (response.status === 401) {
      handleUnauthorized();
      return;
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    result.textContent = "";
    japaneseInput.value = "";
    englishInput.value = "";
  } catch (error) {
    console.error(error);
    result.textContent = "フレーズ登録に失敗しました。";
  } finally {
    updateSubmitButtonState();
  }
}

screenButtons.forEach((button) => {
  button.addEventListener("click", () => switchScreen(button.dataset.screenTarget));
});

Object.values(phraseViews).forEach((view) => {
  view.showEnglishButton.addEventListener("click", () => toggleEnglish(view));
  view.prevButton.addEventListener("click", () => showPrevPhrase(view));
  view.nextButton.addEventListener("click", () => showNextPhrase(view));
});

japaneseInput.addEventListener("input", updateSubmitButtonState);
englishInput.addEventListener("input", updateSubmitButtonState);
submitButton.addEventListener("click", submitPhrases);

updateSubmitButtonState();

loginForm.addEventListener("submit", handleLogin);
signupForm.addEventListener("submit", handleSignup);
logoutButton.addEventListener("click", handleLogout);

showSignupButton.addEventListener("click", () => {
  loginError.textContent = "";
  loginForm.hidden = true;
  signupForm.hidden = false;
});

showLoginButton.addEventListener("click", () => {
  signupError.textContent = "";
  signupForm.hidden = true;
  loginForm.hidden = false;
});

checkAuth();

const calendarState = (() => {
  const now = new Date();
  return {
    year: now.getFullYear(),
    month: now.getMonth(),
    selectedYear: null,
    selectedMonth: null,
    selectedDay: null,
  };
})();

function renderCalendar() {
  const { year, month } = calendarState;
  const now = new Date();
  const isCurrentMonth = year === now.getFullYear() && month === now.getMonth();
  const today = isCurrentMonth ? now.getDate() : -1;

  document.getElementById("calendar-month-label").textContent = `${year}年${month + 1}月`;

  const firstDow = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const container = document.getElementById("calendar-days");
  container.innerHTML = "";

  for (let i = 0; i < firstDow; i++) {
    const empty = document.createElement("span");
    empty.className = "calendar-day is-empty";
    container.appendChild(empty);
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const cell = document.createElement("button");
    cell.type = "button";
    const isToday = d === today;
    const isSelected =
      calendarState.selectedYear === year &&
      calendarState.selectedMonth === month &&
      calendarState.selectedDay === d;
    cell.className =
      "calendar-day" +
      (isToday ? " is-today" : "") +
      (isSelected ? " is-selected" : "");
    cell.textContent = d;

    cell.addEventListener("click", () => {
      const mm = String(month + 1).padStart(2, "0");
      const dd = String(d).padStart(2, "0");
      const dateStr = `${year}-${mm}-${dd}`;

      calendarState.selectedYear = year;
      calendarState.selectedMonth = month;
      calendarState.selectedDay = d;

      phraseViews["date-phrase"].endpoint = `/api/phrases/date/${dateStr}`;
      document.getElementById("date-phrase-eyebrow").textContent =
        `${year}年${month + 1}月${d}日`;

      switchScreen("date-phrase");
      renderCalendar();
    });

    container.appendChild(cell);
  }
}

document.getElementById("calendar-prev").addEventListener("click", () => {
  calendarState.month -= 1;
  if (calendarState.month < 0) {
    calendarState.month = 11;
    calendarState.year -= 1;
  }
  renderCalendar();
});

document.getElementById("calendar-next").addEventListener("click", () => {
  calendarState.month += 1;
  if (calendarState.month > 11) {
    calendarState.month = 0;
    calendarState.year += 1;
  }
  renderCalendar();
});

renderCalendar();
