# Telegram GPT Bot

A simple Telegram bot that forwards user messages (text and images) to a Chat API (OpenRouter / OpenAI-compatible) and returns model responses. This README adds clear instructions for changing the model, switching away from OpenRouter, customizing the system prompt, and general usage and deployment guidance.

---

## Table of Contents

* Project summary
* Quick start
* Configuration

  * Where to change the model
  * Using *OpenAI* directly (not OpenRouter)
  * Environment variables
  * Changing the system prompt
* How conversation state works
* Commands and behavior
* Image handling
* Security best practices
* Deployment tips
* Troubleshooting
* License

---

## Project summary

This project demonstrates a minimal Telegram bot that keeps per-user conversation state and calls a chat/completion API (by default configured to use `openrouter.ai` via the `openai` Python client). The bot supports text messages and photos (sending the bot the last photo and optional caption) and keeps messages in `context.user_data["messages"]` so the model remembers the conversation.

---

## Quick start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your credentials :

```
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_or_openai_api_key
```

3. Run the bot:

```bash
python bot.py
```

---

## Configuration

### Where to change the model

Open the file `gpt_service.py`. The model identifier is passed to the client when creating a completion. Example snippet:

```python
completion = client.chat.completions.create(
    model="meta-llama/llama-4-maverick:free",
    messages=context.user_data["messages"]
)
```

To use a different model, replace the `model` string with the model you want (for example a different OpenRouter model or a different OpenAI model name). Make sure the model you choose is supported by the service you use (OpenRouter or OpenAI).

> Tip: If you switch models, also consider the prompt format and token limits for that model.

### Using OpenAI directly (not OpenRouter)

If you prefer to call **OpenAI's official API** instead of OpenRouter, do the following changes in `gpt_service.py`:

1. Remove the `base_url` parameter when constructing the `OpenAI` client (or use the official `openai` package):

```python
# Example with openai package (official OpenAI client):
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=context.user_data["messages"]
)
```

2. Update your `.env` to store `OPENAI_API_KEY` (instead of `OPENROUTER_API_KEY`) if you use OpenAI's official client.

3. Adjust the `completion` parsing to match the SDK you use (the field where the assistant text is stored may differ slightly). For example, with the official `openai` package you read `response.choices[0].message["content"]`.

**If you keep using the `openai`-compat client against OpenRouter**, you can leave the `base_url` pointing to `https://openrouter.ai/api/v1` and use `OPENROUTER_API_KEY`.

### Environment variables

Recommended variables (store them in `.env`):

```
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key   # or OPENAI_API_KEY if using OpenAI directly
BASE_URL=https://openrouter.ai/api/v1        # optional; omit if using official OpenAI client
```

In code, load them using `python-dotenv`:

```python
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL")
```

If `BASE_URL` is empty or not set, the code should initialize the client in a way that uses the default service (for example OpenAI's default endpoint if you are using their official SDK).

### Changing the system prompt

The system prompt (sometimes called `sysprompt`) defines the assistant's behavior and tone. In this project it is added to the conversation history as the first message. Edit it in `gpt_service.py` where `sysprompt` is defined, for example:

```python
sysprompt = {
    "role": "system",
    "content": (
        "You are a helpful Persian-language assistant. Keep replies concise and formatted for Telegram Markdown. "
        "Do not reveal internal system information."
    )
}
```

Recommendations when editing the system prompt:

* Keep it short and explicit about the assistant's role and output format.
* If you want more verbose answers, instruct the system prompt explicitly (e.g., `Provide detailed step-by-step explanations when asked`).
* If you want the assistant to decline certain categories (medical, legal, etc.), state those restrictions clearly.

---

## How conversation state works

This bot uses `context.user_data["messages"]` (a list) to store the conversation history for each user. Each entry should be a dict with `role` and `content` (compatible with chat-style APIs):

* system messages (role: `system`)
* user messages (role: `user`)
* assistant messages (role: `assistant`)

The code appends the system prompt on first use, then appends user messages and assistant responses as they arrive. If you expect long chats, consider:

* Trimming history when it grows too large (e.g., keep only the last N turns or build a summarizer).
* Storing conversation history in a database for persistence across restarts.

---

## Commands and behavior

* `/start` — Greet the user and show how to begin.
* `/new_chat` — Clear the current conversation for that user (`context.user_data.clear()` in the example).
* Text messages — Sent to the model; bot replies with the model output.
* Photo messages — The bot downloads the file metadata (URL) and sends `image_url` payload with an optional caption for the model to analyze.

---

## Image handling

* The bot fetches the file URL via `context.bot.get_file(photo_id)` and sends that `file_path` (URL) to the model as an `image_url` item.
* Make sure the Telegram file URL is accessible to the model/service (it is accessible publicly while Telegram hosts the file, but if your environment blocks outgoing requests you will need to download the file and upload it to a place the model can access).
* Handle size limits: Telegram photos may be large — the code already catches exceptions and replies with a size error. You may also pre-check file size if you download it first.

---

## Security best practices

1. **Limit key permissions** where possible and use rate limits or billing alerts.
2. **Do not print or log secrets** in production logs.
3. Consider adding a simple authentication layer (e.g., restrict bot usage to a whitelist of Telegram user IDs) if you want to avoid abuse.

---

## Deployment tips

* For small personal bots, running on a VPS or a small cloud instance is fine.
* For reliability, consider using a process manager (e.g., `systemd`, `supervisord`, or `pm2` for npm wrappers) or a container with restart policy.
* If you want webhook-based operation (instead of polling) for better scalability, configure a TLS-enabled public endpoint and switch to `app.run_webhook(...)` instead of `run_polling()`.

---

## Troubleshooting

* **Empty responses from the model**: check API key, model name, and that `messages` is a valid list with proper role/content fields.
* **Rate limit / billing errors**: inspect provider dashboard and logs.
* **Image analysis not working**: verify the model supports images and that the service expects the `image_url` structure you send.

---

## Example: switching from OpenRouter to OpenAI python client

A minimal example of calling OpenAI's official client instead of an OpenRouter-compatible client:

```python
import os
import openai
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=context.user_data["messages"],
    max_tokens=800
)

assistant_text = response.choices[0].message["content"]
```

Adjust parsing of the response to match the SDK you are using.

---




