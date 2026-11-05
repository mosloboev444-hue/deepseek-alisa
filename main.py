#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Навык Яндекс.Алисы → DeepSeek.
Ноль внешних зависимостей (только stdlib), чтобы запускалось где угодно.

Запуск:  DEEPSEEK_API_KEY=sk-... python main.py
Порт:    PORT (по умолчанию 8000)
"""
import json
import os
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
PORT = int(os.getenv("PORT", "8000"))

SYSTEM_PROMPT = (
    "Ты — голосовой ассистент в умной колонке Яндекс.Станция. "
    "Отвечай кратко и по делу: 1–3 предложения, без списков и markdown, "
    "текст должен хорошо звучать вслух. Если вопрос требует подробностей — "
    "дай главное и предложи спросить детали."
)

SSL_CTX = ssl.create_default_context()


def ask_deepseek(text: str) -> str:
    body = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "max_tokens": 600,
        "temperature": 0.7,
    }
    req = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=40, context=SSL_CTX) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def alice_response(body: dict, text: str) -> dict:
    return {
        "version": body.get("version", "1.0"),
        "session": body.get("session", {}),
        "response": {
            "end_session": False,
            "text": text,
            "tts": text,
        },
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # тише в логах
        pass

    def _send(self, obj, status=200):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        self._send({"status": "ok", "service": "deepseek-alisa"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send({"error": "bad_json"}, 400)
            return

        req = body.get("request") or {}

        # ping при сохранении навыка в Яндекс.Диалогах
        if req.get("type") == "ping":
            self._send(alice_response(body, ""))
            return

        text = (req.get("original_utterance") or req.get("command") or "").strip()
        if not text:
            self._send(alice_response(body, "Не расслышала. Повтори, пожалуйста."))
            return

        if not DEEPSEEK_API_KEY:
            self._send(alice_response(body, "Не настроен ключ DeepSeek."))
            return

        try:
            answer = ask_deepseek(text)
        except Exception:
            self._send(alice_response(body, "DeepSeek не ответил. Попробуй ещё раз."))
            return

        if len(answer) > 900:
            answer = answer[:900] + "…"

        self._send(alice_response(body, answer))


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"deepseek-skill слушает :{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
