"""
Orquestra o fluxo completo:
1. Faz scraping da página de variações de preço da LigaMagic
2. Filtra cartas com alta >= 50% e preço atual >= R$10
3. Ignora cartas já notificadas (a menos que tenham subido ainda mais)
4. Envia notificação via Telegram para as novidades
5. Salva o estado atualizado
"""
from scraper import fetch_price_increases
from telegram_notify import send_telegram_message, format_alert
from state import load_state, save_state, should_notify, record_notification

MIN_PRICE = 10.0
MIN_PCT = 30.0


def main():
    print("Buscando variações de preço na LigaMagic...")
    changes = fetch_price_increases(min_price=MIN_PRICE, min_pct=MIN_PCT)
    print(f"{len(changes)} cartas encontradas acima do filtro (>= {MIN_PCT}%, preço >= R${MIN_PRICE}).")

    state = load_state()
    to_notify = []

    for change in changes:
        if should_notify(state, change.name, change.edition, change.new_price, change.pct_change):
            to_notify.append(change)
            record_notification(state, change.name, change.edition, change.new_price, change.pct_change)

    print(f"{len(to_notify)} cartas novas para notificar.")

    for change in to_notify:
        message = format_alert(change.name, change.edition, change.old_price, change.new_price, change.pct_change)
        try:
            send_telegram_message(message)
            print(f"Notificado: {change.name} ({change.edition}) - R$ {change.new_price:.2f} (+{change.pct_change:.1f}%)")
        except Exception as e:
            print(f"Erro ao notificar {change.name}: {e}")

    save_state(state)
    print("Concluído.")


if __name__ == "__main__":
    main()
