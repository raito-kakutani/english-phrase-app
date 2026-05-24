const japaneseInput = document.getElementById("japanese-input");
const englishInput = document.getElementById("english-input");
const submitButton = document.getElementById("submit-button");
const result = document.getElementById("result");

function hasRequiredInputs() {
  return (
    japaneseInput.value.trim() !== "" &&
    englishInput.value.trim() !== ""
  );
}

function updateSubmitButtonState() {
  submitButton.disabled = !hasRequiredInputs();
}

async function submitPhrases() {
  const japanese = japaneseInput.value.trim();
  const english = englishInput.value.trim();

  if (!hasRequiredInputs()) {
    updateSubmitButtonState();
    return;
  }

  if (result) {
    result.textContent = "Submitting...";
  }
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

    if (result) {
      result.textContent = `Submitted: Japanese ${data.japanese_length} chars / English ${data.english_length} chars`;
    }
  } catch (error) {
    if (result) {
      result.textContent = `Submit failed: ${error.message}`;
    }
  } finally {
    updateSubmitButtonState();
  }
}

japaneseInput.addEventListener("input", updateSubmitButtonState);
englishInput.addEventListener("input", updateSubmitButtonState);
submitButton.addEventListener("click", submitPhrases);
updateSubmitButtonState();
