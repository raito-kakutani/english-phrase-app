const japaneseInput = document.getElementById("japanese-input");
const englishInput = document.getElementById("english-input");
const submitButton = document.getElementById("submit-button");
const result = document.getElementById("result");
const screenButtons = document.querySelectorAll("[data-screen-target]");
const screens = document.querySelectorAll("[data-screen]");

const phraseViews = {
  "today-phrase": {
    endpoint: "http://127.0.0.1:8000/api/phrases/today",
    countElement: document.getElementById("today-phrase-count"),
    japaneseElement: document.getElementById("today-phrase-text"),
    englishElement: document.getElementById("today-phrase-english"),
    showEnglishButton: document.getElementById("show-english-button"),
    nextButton: document.getElementById("next-today-phrase-button"),
    state: {
      phrases: [],
      currentIndex: 0,
      isEnglishVisible: false,
      hasPhrase: false,
    },
  },
  "yesterday-phrase": {
    endpoint: "http://127.0.0.1:8000/api/phrases/yesterday",
    countElement: document.getElementById("yesterday-phrase-count"),
    japaneseElement: document.getElementById("yesterday-phrase-text"),
    englishElement: document.getElementById("yesterday-phrase-english"),
    showEnglishButton: document.getElementById("show-yesterday-english-button"),
    nextButton: document.getElementById("next-yesterday-phrase-button"),
    state: {
      phrases: [],
      currentIndex: 0,
      isEnglishVisible: false,
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
  if (!view) return;

  resetView(view);

  try {
    const response = await fetch(view.endpoint);
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
    const response = await fetch("http://127.0.0.1:8000/api/phrases", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ japanese, english }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    result.textContent = "";
    japaneseInput.value = "";
    englishInput.value = "";
  } catch (error) {
    result.textContent = `Submit failed: ${error.message}`;
  } finally {
    updateSubmitButtonState();
  }
}

screenButtons.forEach((button) => {
  button.addEventListener("click", () => switchScreen(button.dataset.screenTarget));
});

Object.values(phraseViews).forEach((view) => {
  view.showEnglishButton.addEventListener("click", () => toggleEnglish(view));
  view.nextButton.addEventListener("click", () => showNextPhrase(view));
});

japaneseInput.addEventListener("input", updateSubmitButtonState);
englishInput.addEventListener("input", updateSubmitButtonState);
submitButton.addEventListener("click", submitPhrases);

updateSubmitButtonState();
