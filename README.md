# Asint: Платформа для управления и оценки активов на базе ИИ

> **Управляйте. Оценивайте. Визуализируйте. Продавайте. — Всё в одном месте!**

Asint — это современная веб-платформа для управления, оценки и отслеживания стоимости ваших объектов недвижимости и автомобилей. Благодаря машинному обучению Asint помогает принимать более взвешенные инвестиционные решения, визуализировать динамику цен и легко выставлять активы на продажу — всё в красивом и интуитивно понятном интерфейсе.

---

## 🚀 Основные возможности

- **Оценка активов на базе ИИ:** Мгновенная оценка стоимости квартир и автомобилей с помощью продвинутых ML-моделей.
- **Исторический трекинг цен:** Автоматическая генерация и ежемесячное обновление истории цен за 12 месяцев для каждого актива.
- **Интерактивные дашборды:** Визуализация динамики активов и рыночных трендов с помощью графиков Chart.js.
- **Управление портфелем:** Организуйте активы в портфели и отслеживайте их рост.
- **Маркетплейс:** Размещайте активы на продажу, просматривайте объявления и связывайтесь с покупателями.
- **Персональный AI-ассистент:** Получайте советы по инвестициям, рыночные инсайты и рекомендации по активам — даже с помощью голосового ввода!
- **PDF-отчёты:** Скачивайте подробные отчёты по вашим активам.
- **Безопасность и приватность:** Все операции защищены, доступ к данным только после авторизации.

---

## 🛠️ Технологии

**Бэкенд:**  
- Django 3.2+  
- Django REST Framework  
- SQLite (по умолчанию, легко заменить на Postgres/MySQL)  
- pandas, scikit-learn, joblib, lightgbm (ML-интеграция)  
- django-cors-headers

**Фронтенд:**  
- HTML, CSS, JavaScript (vanilla)  
- Tailwind CSS  
- Chart.js  
- Lucide Icons

**Другое:**  
- fpdf2 (генерация PDF)  
- python-dateutil

---

## 📈 Как это работает

1. **Регистрация и вход:** Создайте аккаунт и начните формировать свой портфель активов.
2. **Добавление активов:** Введите данные о квартире или автомобиле — система мгновенно рассчитает текущую и историческую стоимость с помощью ML.
3. **Визуализация:** Просматривайте интерактивные графики динамики стоимости и 30-дневных изменений.
4. **Маркетплейс:** Размещайте активы на продажу или ищите выгодные предложения.
5. **AI-ассистент:** Общайтесь в чате или голосом для получения советов, прогнозов и рыночных подсказок.
6. **Скачивание отчётов:** Генерируйте и скачивайте PDF-отчёты по своим активам.

---

## 📦 Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/yourusername/asint_tech.git
   cd asint_tech
   ```
2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Примените миграции:**
   ```bash
   python manage.py migrate
   ```
4. **Запустите сервер:**
   ```bash
   python manage.py runserver
   ```
5. **Откройте фронтенд:**
   - Откройте `frontend/index.html` в браузере (или используйте любой статический сервер).

---

## 🤖 Машинное обучение
- Предобученные модели для оценки недвижимости и автомобилей (см. папку `data/`).
- Модели ML загружаются при запуске и используются для мгновенной и исторической оценки.

---

## 🗂️ Структура проекта

```
asset_manager/      # Django-приложение: модели, вьюхи, утилиты, команды
prediction/         # ML API для предсказаний
frontend/           # HTML, JS, CSS, изображения
homeeval_project/   # Настройки Django-проекта
...
```

---

## 🛡️ Важно
Этот репозиторий не содержит чувствительных данных (БД, секретов, данных пользователей) — всё это исключено через .gitignore. Не добавляйте и не коммитьте личную или секретную информацию!

---

## 📄 Лицензия
[MIT](LICENSE)

---

# 🇬🇧 English version

## Asint: AI-Powered Asset Management & Valuation Platform

> **Track. Evaluate. Visualize. Sell. — All in One Place.**

Asint is a modern web platform for managing, evaluating, and tracking the value of your real estate and vehicle assets. Powered by machine learning, Asint helps you make smarter investment decisions, visualize historical price trends, and seamlessly list assets for sale — all with a beautiful, intuitive interface.

---

## 🚀 Features

- **AI-Powered Asset Valuation:** Instantly estimate the value of apartments and cars using advanced ML models.
- **Historical Price Tracking:** Automatic generation and monthly updates of 12-month price history for every asset.
- **Interactive Dashboards:** Visualize asset performance and market trends with stunning Chart.js graphs.
- **Portfolio Management:** Organize your assets into portfolios and monitor their growth.
- **Marketplace:** List assets for sale, browse listings, and connect with buyers.
- **Personal AI Assistant:** Get investment advice, market insights, and asset recommendations — even via voice input!
- **PDF Reports:** Download detailed evaluation reports for your assets.
- **Secure & Private:** Your data is protected; authentication required for all sensitive operations.

---

## 🛠️ Tech Stack

**Backend:**  
- Django 3.2+  
- Django REST Framework  
- SQLite (default, easy to swap for Postgres/MySQL)  
- pandas, scikit-learn, joblib, lightgbm (ML integration)  
- django-cors-headers

**Frontend:**  
- HTML, CSS, JavaScript (vanilla)  
- Tailwind CSS  
- Chart.js  
- Lucide Icons

**Other:**  
- fpdf2 (PDF generation)  
- python-dateutil

---

## 📈 How It Works

1. **Sign Up & Log In:** Create your account and start building your asset portfolio.
2. **Add Assets:** Enter details for apartments or cars. The system instantly estimates current and historical prices using ML models.
3. **Visualize Trends:** View interactive charts showing value changes, 30-day trends, and more.
4. **Marketplace:** List your assets for sale or browse others' listings.
5. **AI Assistant:** Chat or use voice to get advice, price predictions, and market tips.
6. **Download Reports:** Generate and download PDF reports for your assets.

---

## 📦 Installation

1. **Clone the repo:**
   ```bash
   git clone https://github.com/yourusername/asint_tech.git
   cd asint_tech
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```
4. **Start the server:**
   ```bash
   python manage.py runserver
   ```
5. **Open the frontend:**
   - Open `frontend/index.html` in your browser (or serve via your preferred static server).

---

## 🤖 Machine Learning
- Pre-trained models for real estate and car price prediction (see `data/` directory).
- ML models are loaded at runtime and used for both instant and historical price estimation.

---

## 🗂️ Project Structure

```
asset_manager/      # Django app: models, views, utils, management commands
prediction/         # ML prediction API endpoints
frontend/           # HTML, JS, CSS, images
homeeval_project/   # Django project settings
...
```

---

## 🛡️ Security Notice
This repository excludes sensitive files such as database files, data files, and any credentials or secrets using a .gitignore file. Please ensure you do not add or commit any personal, confidential, or secret information to this repository.

---

## 📄 License
[MIT](LICENSE)
