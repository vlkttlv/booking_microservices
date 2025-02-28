# Сервис для бронирования отелей, реализованный с помощью микросервисной архитектуры

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
   uvicorn pay_service.main:app --reload --port 8003
   ```
7. Запустите rabbit:
   ```bash
   python -m rabbit.rabbit
   ```
