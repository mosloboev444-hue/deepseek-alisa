# Навык Алисы → DeepSeek

Голосовой навык для Яндекс.Алисы, который отвечает через API DeepSeek.

## Что нужно

1. **API-ключ DeepSeek** — получить на https://platform.deepseek.com/ (ключ вида `sk-...`).
2. **Публичный HTTPS-адрес** этого сервера — навык в Яндекс.Диалогах должен быть доступен из интернета.

## Вариант A. Быстро: локальный сервер + туннель (без аккаунтов)

1. Запусти сервер (PowerShell):
   ```powershell
   $env:DEEPSEEK_API_KEY = "sk-..."
   python main.py
   ```
   Сервер слушает `http://localhost:8000`.

2. Во втором окне открой туннель (даст публичный адрес):
   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```
   Скопируй выданный адрес вида `https://xxxx.trycloudflare.com` — это и есть URL навыка.

   > Минус: адрес меняется при перезапуске туннеля. Тогда нужно обновить Webhook URL в Яндекс.Диалогах.

## Вариант B. Надёжно: Render (нужен GitHub + аккаунт Render)

1. Залей папку `deepseek_skill` в свой GitHub-репозиторий.
2. https://render.com → **New → Web Service** → подключи репозиторий.
3. Build Command: `pip install -r requirements.txt` (пустой — зависимостей нет)
4. Start Command: `python main.py`
5. Environment: `DEEPSEEK_API_KEY = sk-...`
6. После деплоя получишь стабильный адрес `https://....onrender.com`.

## Подключение навыка в Алисе

1. Открой https://dialogs.yandex.ru/developer
2. **Создай навык → Диалог**.
3. В поле **Webhook URL** вставь адрес сервера (из варианта A или B).
4. Сохрани и активируй навык (на вкладке «Проверка» можно прогнать тест).
5. Скажи колонке: **«Алиса, запусти DeepSeek»** — и задавай вопросы голосом.

## Проверка сервера вручную

```powershell
curl -X POST http://localhost:8000 `
  -H "Content-Type: application/json" `
  -d '{"version":"1.0","session":{},"request":{"original_utterance":"Сколько будет 2+2?","type":"SimpleUtterance"}}'
```

Должен вернуться JSON с `response.text`.

## Переменные окружения

| Переменная | Назначение |
| --- | --- |
| `DEEPSEEK_API_KEY` | ключ DeepSeek (обязательно) |
| `DEEPSEEK_MODEL` | модель (по умолчанию `deepseek-chat`) |
| `DEEPSEEK_API_URL` | адрес API (по умолчанию `https://api.deepseek.com/v1/chat/completions`) |
| `PORT` | порт (по умолчанию 8000) |
