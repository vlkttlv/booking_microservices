# Сервис для бронирования отелей, реализованный с помощью микросервисной архитектуры


## Стек технологий


![fastapi](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)
![https://img.shields.io/badge/PostgreSQL-green?style=for-the-badge](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![sqlalchemy](https://img.shields.io/badge/SQLAlchemy-red?style=for-the-badge)
![rabbitmq](https://img.shields.io/badge/rabbitmq-%23FF6600.svg?&style=for-the-badge&logo=rabbitmq&logoColor=white)
![pydentic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=Pydantic&logoColor=white)
![stripe](https://img.shields.io/badge/Stripe-626CD9?style=for-the-badge&logo=Stripe&logoColor=white)

## Установка и запуск


1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/vlkttlv/booking_microservices.git
   ```
2. Перейдите в папку проекта:
   ```bash
   cd booking_microservices
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Настройте переменные окружения. Создайте файл `.env` в каждом микросервисе и добавьте необходимые параметры.
   
5. Создайте таблицы в БД, используя файд ddl.sql

6. Запуcтите каждый микросервис:
   ```bash
   uvicorn users_service.main:app --reload
   ```
   ```bash
   uvicorn hotels_service.main:app --reload --port 8001
   ```
   ```bash
   uvicorn booking_service.main:app --reload --port 8002
   ```
   ```bash
   uvicorn payment_service.main:app --reload --port 8003
   ```
7. Запустите rabbit:
   ```bash
   python -m rabbit.booking_rabbit
   ```
   ```bash
   python -m rabbit.pay_rabbit
   ```

----
## Запуск микросервиса users_service в контейнере в рамках лабораторной работы:
В корне проекта создайте файл .env:
```bash
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_PORT=
```
В директории users_service создайте файл .env (пример лежит в .env_example)
Запустите контейнер:
```bash
docker-compose up -d --build
```
Теперь микросервис доступен под адресу:
```bash
http://localhost:8000/docs
```
