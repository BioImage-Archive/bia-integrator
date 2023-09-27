cd ../api
docker compose down -v
docker compose --env-file ./.env_compose up -d

echo "Waiting for the api to start"
sleep 5

curl -H "Content-Type: application/json" \
    --request POST \
    --data '{"email": "test@example.com", "password_plain": "test", "secret_token": "00123456789==" }' \
    http://127.0.0.1:8080/auth/users/register
