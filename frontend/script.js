const japaneseInput = document.getElementById("japanese-input");
const englishInput = document.getElementById("english-input");
const submitButton = document.getElementById("submit-button");
const result = document.getElementById("result");
const screenButtons = document.querySelectorAll("[data-screen-target]");
const screens = document.querySelectorAll("[data-screen]");

const phraseViews = {
  "today-phrase": {
    endpoint: "http://127.0.0.1:8000/api/phrases/today",
    loadingMessage: "今日のフレーズを読み込み中...",
    labelElement: document.getElementById("today-phrase-label"),
    textElement: document.getElementById("today-phrase-text"),
    metaElement: document.getElementById("today-phrase-meta"),
    showJapaneseButton: document.getElementById("show-japanese-button"),
    showEnglishButton: document.getElementById("show-english-button"),
    state: {
      japaneseText: "",
      englishText: "",
      createdAt: "",
      visibleLanguage: "japanese",
      hasPhrase: false,
    },
  },
  "yesterday-phrase": {
    endpoint: "http://127.0.0.1:8000/api/phrases/yesterday",
    loadingMessage: "昨日のフレーズを読み込み中...",
    labelElement: document.getElementById("yesterday-phrase-label"),
    textElement: document.getElementById("yesterday-phrase-text"),
    metaElement: document.getElementById("yesterday-phrase-meta"),
    showJapaneseButton: document.getElementById("show-yesterday-japanese-button"),
    showEnglishButton: document.getElementById("show-yesterday-english-button"),
    state: {
      japaneseText: "",
      englishText: "",
      createdAt: "",
      visibleLanguage: "japanese",
      hasPhrase: false,
    },
  },
};

function hasRequiredInputs() {
  return japaneseInput.value.trim() !== "" && englishInput.value.trim() !== "";
}

function updateSubmitButtonState() {
  submitButton.disabled = !hasRequiredInputs();
}

function formatCreatedAt(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toLocaleString("ja-JP");
}

function renderPhrase(view) {
  if (!view.state.hasPhrase) {
    view.labelElement.textContent = "日本語";
    view.showJapaneseButton.classList.add("is-active");
    view.showJapaneseButton.setAttribute("aria-selected", "true");
    view.showEnglishButton.classList.remove("is-active");
    view.showEnglishButton.setAttribute("aria-selected", "false");
    return;
  }

  const showJapanese = view.state.visibleLanguage === "japanese";

  view.labelElement.textContent = showJapanese
    ? "日本語"
    : "英語";
  view.textElement.textContent = showJapanese
    ? view.state.japaneseText
    : view.state.englishText;

  view.showJapaneseButton.classList.toggle("is-active", showJapanese);
  view.showJapaneseButton.setAttribute("aria-selected", String(showJapanese));
  view.showEnglishButton.classList.toggle("is-active", !showJapanese);
  view.showEnglishButton.setAttribute("aria-selected", String(!showJapanese));
}

function setPhraseMessage(view, message) {
  view.labelElement.textContent = "日本語";
  view.textElement.textContent = message;
}

async function loadPhrase(screenName) {
  const view = phraseViews[screenName];

  if (!view) {
    return;
  }

  setPhraseMessage(view, view.loadingMessage);
  view.metaElement.textContent = "";

  try {
    const response = await fetch(view.endpoint);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    view.state.japaneseText = data.japanese_text;
    view.state.englishText = data.english_text;
    view.state.createdAt = data.created_at;
    view.state.visibleLanguage = "japanese";
    view.state.hasPhrase = true;

    renderPhrase(view);

    const createdAtText = formatCreatedAt(data.created_at);
    view.metaElement.textContent = createdAtText
      ? `作成日時: ${createdAtText}`
      : "";
  } catch (error) {
    view.state.japaneseText = "";
    view.state.englishText = "";
    view.state.createdAt = "";
    view.state.visibleLanguage = "japanese";
    view.state.hasPhrase = false;
    setPhraseMessage(
      view,
      `取得できませんでした: ${error.message}`,
    );
    view.metaElement.textContent = "";
    renderPhrase(view);
  }
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

  result.textContent = "Submitting...";
  submitButton.disabled = true;

  try {
    const response = await fetch("http://127.0.0.1:8000/api/phrases", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        japanese,
        english,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    result.textContent = `Submitted: phrase #${data.phrase_id}`;
    japaneseInput.value = "";
    englishInput.value = "";
  } catch (error) {
    result.textContent = `Submit failed: ${error.message}`;
  } finally {
    updateSubmitButtonState();
  }
}

screenButtons.forEach((button) => {
  button.addEventListener("click", () => {
    switchScreen(button.dataset.screenTarget);
  });
});

Object.values(phraseViews).forEach((view) => {
  view.showJapaneseButton.addEventListener("click", () => {
    view.state.visibleLanguage = "japanese";
    renderPhrase(view);
  });

  view.showEnglishButton.addEventListener("click", () => {
    view.state.visibleLanguage = "english";
    renderPhrase(view);
  });
});

japaneseInput.addEventListener("input", updateSubmitButtonState);
englishInput.addEventListener("input", updateSubmitButtonState);
submitButton.addEventListener("click", submitPhrases);

updateSubmitButtonState();
