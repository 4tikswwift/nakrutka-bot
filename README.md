# 🚀 Накрутка — Telegram Mini App + Bot

Telegram-бот с Mini App для накрутки лайков и просмотров.

---

## Структура проекта

```
BOT TG/
├── bot.py          # Telegram-бот + HTTP-сервер (aiogram 3 + aiohttp)
├── index.html      # Mini App (один HTML-файл, vanilla JS)
├── requirements.txt
├── .env            # Секреты (не коммитить!)
├── .env.example    # Шаблон переменных
├── Procfile        # Для Railway
└── README.md
```

---

## Запуск локально (для теста)

### 1. Установи Python 3.11+
Скачай с https://python.org

### 2. Установи зависимости
```bash
cd "BOT TG"
pip install -r requirements.txt
```

### 3. Заполни .env
```
BOT_TOKEN=8844433664:AAH13hdvK2hY70aYqYV9czp5nYzXTfs7rZk
WEBAPP_URL=https://your-app.up.railway.app   # ← после деплоя
PORT=8080
```

### 4. Запусти
```bash
python bot.py
```

> Локально Mini App работает только по HTTPS-ссылке (требование Telegram).
> Поэтому сначала задеплой на Railway, потом пропиши WEBAPP_URL.

---

## Деплой на Railway (бесплатно)

### Шаг 1 — Загрузи проект на GitHub

1. Зайди на https://github.com/new
2. Создай репозиторий (например `nakrutka-bot`)
3. В терминале:
```bash
cd "BOT TG"
git init
git add .
git commit -m "init"
git remote add origin https://github.com/ТВОЙ_НИК/nakrutka-bot.git
git push -u origin main
```

### Шаг 2 — Создай сервис на Railway

1. Зайди на https://railway.app и войди через GitHub
2. Нажми **New Project → Deploy from GitHub repo**
3. Выбери репозиторий `nakrutka-bot`
4. Railway сам обнаружит `Procfile` и запустит `python bot.py`

### Шаг 3 — Добавь переменные окружения

В Railway → твой проект → вкладка **Variables**, добавь:

| Переменная   | Значение                                      |
|--------------|-----------------------------------------------|
| `BOT_TOKEN`  | твой токен из @BotFather                          |
| `WEBAPP_URL` | (пока пусто, заполним на следующем шаге)      |
| `PORT`       | `8080`                                        |

### Шаг 4 — Получи публичный URL

1. В Railway → **Settings → Networking → Generate Domain**
2. Ты получишь URL вида `https://nakrutka-bot-production.up.railway.app`
3. Скопируй его и вставь в переменную `WEBAPP_URL`
4. Railway автоматически перезапустит сервис

### Шаг 5 — Зарегистрируй Mini App в BotFather

1. Открой @BotFather в Telegram
2. Напиши `/newapp`
3. Выбери своего бота `@nakrutka1rub_bot`
4. Вставь URL из Railway как Web App URL

### Шаг 6 — Проверь

Напиши `/start` своему боту — должна появиться кнопка **🚀 Открыть сервис** и слева кнопка **НАКРУТИТЬ**.

---

## Как работает Mini App

| Шаг | Экран |
|-----|-------|
| 1 | Выбор платформы (Like / TikTok / YouTube / Instagram) |
| 2 | Ввод никнейма → лоадер 3 сек |
| 3 | Слайдер 100–10 000 + цена 1 ₽ |
| 4 | Подтверждение → лоадер 3 сек → зелёный баннер |
| 5 | Кнопка **ПОЛУЧИТЬ ХАЛЯВУ 🎁** → переход на партнёрскую ссылку |

---

## Troubleshooting

**Бот не отвечает** — проверь что `BOT_TOKEN` правильный в Railway Variables.

**Mini App не открывается** — убедись что `WEBAPP_URL` начинается с `https://` и домен активен в Railway.

**"Blocked: mixed content"** — Telegram требует HTTPS. Railway даёт его автоматически.
