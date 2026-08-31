import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_telegram_message(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN e/ou TELEGRAM_CHAT_ID não configurados. "
            "Defina como variáveis de ambiente (ou Secrets no GitHub Actions)."
        )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    response = requests.post(url, data=payload, timeout=15)
    response.raise_for_status()
    return True


def format_alert(name: str, edition: str, old_price: float, new_price: float, pct_change: float) -> str:
    return (
        f"🔺 *{name}* ({edition}) subiu {pct_change:.1f}%\n"
        f"R$ {old_price:.2f} → R$ {new_price:.2f}"
    )
