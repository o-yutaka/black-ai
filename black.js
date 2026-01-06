const chat = document.getElementById("chat");
const input = document.getElementById("input");

function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = "msg " + type;
  div.innerText = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function send() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  // BLACKの仮応答（ダミー）
  setTimeout(() => {
    const reply =
      "BLACK解析中\n\n入力構造を確認しました。\nまだAPI未接続です。";
    addMessage(reply, "black");
  }, 600);
}

// 初期メッセージ
addMessage("BLACK 起動完了。\n入力を待機中。", "black");
