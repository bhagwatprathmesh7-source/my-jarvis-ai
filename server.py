import os
import uvicorn
import requests
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# OpenRouter द्वारे Google Gemini मॉडेल
OPENROUTER_API_KEY = "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"
OWNER_SECRET_KEY = "jarvis_boss_2026"

app = FastAPI(title="JARVIS Private AI")

class ChatRequest(BaseModel):
    message: str

def verify_token(x_auth_token: str = Header(None)):
    if x_auth_token != OWNER_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JARVIS AI</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
            body { background-color: #0d1117; color: #c9d1d9; display: flex; flex-direction: column; height: 100vh; }
            #header { padding: 15px 20px; background: #161b22; border-bottom: 1px solid #30363d; display: flex; justify-content: space-between; align-items: center; }
            #header h1 { font-size: 1.1rem; color: #58a6ff; }
            #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
            .msg { max-width: 85%; padding: 12px 16px; border-radius: 8px; line-height: 1.5; font-size: 0.95rem; }
            .user-msg { align-self: flex-end; background: #1f6feb; color: #fff; }
            .ai-msg { align-self: flex-start; background: #161b22; border: 1px solid #30363d; }
            #input-container { padding: 15px 20px; background: #161b22; border-top: 1px solid #30363d; display: flex; gap: 10px; }
            input[type="text"] { flex: 1; padding: 12px 16px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #fff; outline: none; }
            button { padding: 12px 20px; background: #238636; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
        </style>
    </head>
    <body>
        <div id="header">
            <h1>⚡ JARVIS INTELLIGENCE</h1>
            <span style="font-size: 0.8rem; color: #7ee787;">● ONLINE (PRIVATE)</span>
        </div>
        <div id="chat-container">
            <div class="msg ai-msg">Good day Boss. I am ready. How can I assist you?</div>
        </div>
        <div id="input-container">
            <input type="text" id="userInput" placeholder="Ask Jarvis anything..." onkeydown="if(event.key==='Enter') sendMsg()">
            <button onclick="sendMsg()">Send</button>
        </div>
        <script>
            let token = localStorage.getItem("jarvis_token");
            if (!token) {
                token = prompt("Enter Security Passcode:");
                localStorage.setItem("jarvis_token", token);
            }
            async function sendMsg() {
                const input = document.getElementById("userInput");
                const text = input.value.trim();
                if (!text) return;
                const chat = document.getElementById("chat-container");
                chat.innerHTML += `<div class="msg user-msg">${text}</div>`;
                input.value = "";
                chat.scrollTop = chat.scrollHeight;
                try {
                    const res = await fetch("/api/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json", "x-auth-token": token },
                        body: JSON.stringify({ message: text })
                    });
                    if (res.status === 401) {
                        localStorage.removeItem("jarvis_token");
                        alert("Access Denied: Invalid Passcode!");
                        location.reload();
                        return;
                    }
                    const data = await res.json();
                    chat.innerHTML += `<div class="msg ai-msg">${data.reply}</div>`;
                } catch (e) {
                    chat.innerHTML += `<div class="msg ai-msg" style="color:#f85149;">Connection error.</div>`;
                }
                chat.scrollTop = chat.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/chat")
async def process_chat(req: ChatRequest, _ = Depends(verify_token)):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {"role": "system", "content": "You are JARVIS, an autonomous, highly advanced, ultra-intelligent private AI. Address the user as Boss. Be direct, comprehensive, witty, and precise."},
            {"role": "user", "content": req.message}
        ]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        data = response.json()
        if "choices" in data:
            return {"reply": data["choices"][0]["message"]["content"]}
        else:
            return {"reply": f"Error: {data}"}
    except Exception as e:
        return {"reply": f"Error: {e}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
    
