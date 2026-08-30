# LigaMagic Price Alert

Monitora a página de [Variações de Preço](https://www.ligamagic.com.br/?view=cards/variacao&show=alta)
da LigaMagic e envia um alerta no Telegram sempre que uma carta subir de preço
acima de um limite configurado — por padrão, alta de **50%** ou mais, com
preço atual de pelo menos **R$10**.

A ideia é avisar rapidamente sobre cartas em valorização (útil para quem
compra/revende cartas de Magic), sem precisar ficar checando o site manualmente.
O projeto guarda um histórico local (`state.json`) para não notificar a mesma
alta repetidamente, e pode rodar tanto localmente quanto automaticamente via
GitHub Actions.

## Estrutura

| Arquivo | Função |
|---|---|
| `scraper.py` | Abre a página com Playwright e extrai as cartas em alta |
| `state.py` | Guarda quais cartas já foram notificadas, evita duplicatas |
| `telegram_notify.py` | Envia a mensagem no Telegram |
| `main.py` | Orquestra tudo (busca, filtra, notifica, salva estado) |
| `.github/workflows/check_prices.yml` | Agenda a execução automática |

## Como rodar localmente

### 1. Criar um bot no Telegram e pegar o chat_id

1. Fale com o [@BotFather](https://t.me/BotFather) no Telegram e crie um bot
   (`/newbot`) para obter o `TELEGRAM_BOT_TOKEN`.
2. Mande qualquer mensagem para o seu bot.
3. Acesse `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates` no navegador e
   copie o valor de `"chat":{"id": ...}` — esse é o `TELEGRAM_CHAT_ID`.

### 2. Instalar dependências

Recomenda-se usar um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps chromium
```

### 3. Configurar as credenciais e executar

```bash
export TELEGRAM_BOT_TOKEN="seu_token_aqui"
export TELEGRAM_CHAT_ID="seu_chat_id_aqui"
python main.py
```

## Ajustando os filtros

No `main.py`:

```python
MIN_PRICE = 10.0   # preço mínimo da carta para considerar o alerta
MIN_PCT = 50.0     # % mínimo de alta para disparar o alerta
```

## Rodando automaticamente (GitHub Actions)

1. Suba este repositório para o GitHub.
2. Em **Settings → Secrets and variables → Actions**, adicione os secrets
   `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`.
3. O workflow em `.github/workflows/check_prices.yml` roda a cada 6 horas
   automaticamente (também pode ser disparado manualmente pela aba **Actions**).
