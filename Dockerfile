# Используйте официальный образ Python в качестве базового образа
FROM python:3.9-slim

# Установите рабочую директорию в контейнере
WORKDIR /app

# Скопируйте файлы requirements.txt в рабочую директорию
COPY requirements.txt .

# Установите зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте остальные файлы в рабочую директорию контейнера
COPY . .

# Укажите команду для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
