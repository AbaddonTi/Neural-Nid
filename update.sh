# Проверка и создание сети Docker, если она еще не создана
docker network ls | grep -q my-network || docker network create my-network


# Обновление кода из репозитория
cd /root/Neural-Nid/
git fetch origin
git reset --hard origin/master
git pull origin master


# Сборка и запуск бэкенда
cd ~/Neural-Nid/backend
docker stop neural-nid-backend || true
docker rm neural-nid-backend || true
docker build -t neural-nid-backend .
docker run -d --restart always --name neural-nid-backend --network=my-network -p 5500:5500 \
-e OPENAI_API_KEY=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 \
-e STATISTICS_SERVICE_URL=http://statistics-collector:5600/log \
neural-nid-backend


# Сборка и запуск сервиса сбора статистики
cd ~/Neural-Nid/statistics
docker stop statistics-collector || true
docker rm statistics-collector || true
docker build -t statistics-collector .
docker run -d --restart always --name statistics-collector --network=my-network -p 5600:5600 \
-v ~/Neural-Nid/logs:/app/logs \
statistics-collector


# Сборка и запуск фронтенда
cd ~/Neural-Nid/frontend
docker stop neural-nid-frontend || true
docker rm neural-nid-frontend || true
docker build -t neural-nid-frontend .
docker run -d --restart always --network=my-network -p 8080:80 --name neural-nid-frontend neural-nid-frontend
