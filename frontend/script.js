const result = document.getElementById("result");
const button = document.getElementById("check-api-button");

async function checkApi() {
  result.textContent = "確認中...";

  try {
    const response = await fetch("http://127.0.0.1:8000/api/health");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    result.textContent = `API接続成功: ${data.status}`;
  } catch (error) {
    result.textContent = `API接続失敗: ${error.message}`;
  }
}

button.addEventListener("click", checkApi);
