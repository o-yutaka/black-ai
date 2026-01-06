const chat = document.getElementById("chat");
const input = document.getElementById("input");

const API_KEY = "ここにOpenAIのAPIキー"; // ⚠️テスト用のみ

function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = "msg " + type;
  div.innerText = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function send() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  addMessage("BLACK 思考中…", "black");

  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + API_KEY
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "あなたはBLACK。冷静で構造的に分析する研究用AI。" },
        { role: "user", content: text }
      ]
    })
  });

  const data = await res.json();
  const reply = data.choices?.[0]?.message?.content || "応答エラー";

  // 最後の「思考中…」を消す
  chat.lastChild.remove();
  addMessage(reply, "black");
}

addMessage("BLACK 起動完了。\n入力を待機中。", "black");
