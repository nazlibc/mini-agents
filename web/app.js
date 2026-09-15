// 1. FIND the elements we need (by the id= we gave them)
const messagesEl = document.getElementById("messages");
const formEl     = document.getElementById("chat-form");
const inputEl    = document.getElementById("input");
const agentEl    = document.getElementById("agent");

// 2. CREATE a message block; returns handles so we can fill it in later
function addMessage(who) {
  const wrap  = document.createElement("div");
  wrap.className = "msg";
  const head  = document.createElement("b");        // "you" / "A01"
  const chips = document.createElement("span");     // tool chips go here
  const body  = document.createElement("div");      // the text
  body.className = "body";
  wrap.append(head, chips, body);
  messagesEl.append(wrap);
  return { head, chips, body };
}

async function* parseSSE(res) {
  const reader  = res.body.getReader();   // read the response in chunks
  const decoder = new TextDecoder();      // bytes → text
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let idx;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const raw = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);

      let event = "message";
      let data = "";
      for (const line of raw.split("\n")) {
        if (line.startsWith("event: ")) event = line.slice(7);
        else if (line.startsWith("data: ")) data = line.slice(6);
      }
      if (data) yield { event, data: JSON.parse(data) };
    }
    }
    }
    

// 3. REACT to the form being submitted
formEl.addEventListener("submit", async (e) => {
  e.preventDefault();          // stop the browser reloading the page
  const text = inputEl.value.trim();
  if (!text) return;

  addMessage("you").body.textContent = text;
  const bot = addMessage("bot");
  inputEl.value = "";

  const res = await fetch("/api/chat/stream", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ message: text, agent: agentEl.value }),
  });

    for await (const { event, data } of parseSSE(res)) {
    if (event === "agent") {
      bot.head.textContent = data.agent;} 
    else if (event === "tool_call") {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = data.name;
        bot.chips.append(chip);} 
    else if (event === "text_delta") {
        bot.body.textContent += data.text;} 
    else if (event === "error") {
        bot.body.textContent = "⚠ " + data.message;
    }
  }   
});