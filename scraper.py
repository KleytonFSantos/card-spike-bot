import json
import re
from dataclasses import dataclass
from playwright.sync_api import sync_playwright

URL = "https://www.ligamagic.com.br/?view=cards/variacao&show=alta"

CARDSJSON_PATTERN = re.compile(r"var cardsjson\s*=\s*(\[.*?\]);", re.DOTALL)


@dataclass
class CardPriceChange:
    name: str
    edition: str
    old_price: float
    new_price: float
    pct_change: float


def _to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _item_to_change(item: dict):
    name = item.get("sNomePortugues") or item.get("sNomeIngles") or ""
    edition = item.get("ed_sNomePortugues") or item.get("ed_sNome") or ""

    new_price = _to_float(item.get("preco_sem_formatacao"))
    variance_abs = _to_float(item.get("varianciaSemFormat"))

    if new_price <= 0 or variance_abs <= 0:
        return None

    old_price = new_price - variance_abs
    if old_price <= 0:
        return None  # evita divisão por zero / cartas "novas" sem preço anterior real

    pct_change = (variance_abs / old_price) * 100

    return CardPriceChange(
        name=name.strip(),
        edition=edition.strip(),
        old_price=old_price,
        new_price=new_price,
        pct_change=pct_change,
    )


def _extract_cardsjson(html: str) -> list:
    match = CARDSJSON_PATTERN.search(html)
    if not match:
        return []
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"Aviso: falha ao decodificar cardsjson: {e}")
        return []


def fetch_price_increases(min_price: float = 10.0, min_pct: float = 50.0, max_load_more_clicks: int = 15):
    all_items = {}  # chave = IDE_CartaPrincipal, evita duplicatas

    def register_items(items):
        for item in items:
            if not isinstance(item, dict):
                continue
            key = str(item.get("IDE_CartaPrincipal") or item.get("id") or id(item))
            all_items[key] = item

    def handle_response(response):
        try:
            content_type = response.headers.get("content-type", "")
            if "json" in content_type:
                data = response.json()
                if isinstance(data, list):
                    register_items(data)
                elif isinstance(data, dict):
                    for value in data.values():
                        if isinstance(value, list) and value and isinstance(value[0], dict):
                            register_items(value)
            elif "html" in content_type or "text" in content_type:
                text = response.text()
                register_items(_extract_cardsjson(text))
        except Exception:
            pass  # resposta não relevante ou não parseável, ignora

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            locale="pt-BR",
        )
        page = context.new_page()
        page.on("response", handle_response)

        page.goto(URL, wait_until="networkidle", timeout=60000)

        try:
            page.screenshot(path="debug_screenshot.png", full_page=True)
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
        except Exception as e:
            print(f"Aviso: não foi possível salvar arquivos de debug: {e}")

        register_items(_extract_cardsjson(page.content()))

        for _ in range(max_load_more_clicks):
            button = page.query_selector(".card-load-more-button")
            if not button or not button.is_visible():
                break
            try:
                button.click()
                page.wait_for_timeout(1500)
            except Exception:
                break

        browser.close()

    results = []
    for item in all_items.values():
        change = _item_to_change(item)
        if change and change.new_price >= min_price and change.pct_change >= min_pct:
            results.append(change)

    results.sort(key=lambda c: c.pct_change, reverse=True)
    return results


if __name__ == "__main__":
    changes = fetch_price_increases(min_price=10.0, min_pct=50.0)
    for c in changes:
        print(f"{c.name} ({c.edition}): R${c.old_price:.2f} -> R${c.new_price:.2f} ({c.pct_change:.1f}%)")
    print(f"\nTotal encontrado: {len(changes)}")
