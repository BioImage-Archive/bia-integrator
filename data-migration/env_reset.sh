cd ../api
docker compose down -v
docker compose --env-file ./.env_compose up -d

echo "Waiting for the api to start"
sleep 3

curl -H "Content-Type: application/json" \
    --request POST \
    --data '{"email": "test@example.com", "password_plain": "test", "secret_token": "DUMMY1234" }' \
    http://localhost:8080/auth/users/register
