# 🚀 Project Setup Guide

This guide will help you set up the development environment, run the application in Docker, and apply database migrations.

# Build images
```
docker compose build
```

# Start containers
```
docker compose up
```

# Apply Django Migrations Inside Container
After the containers are up, run:
```
docker exec -it conversion-web-1 sh -c "python manage.py makemigrations homepage && python manage.py migrate"
```

💡 Tip:
If conversion-web-1 is not your container name, run:
```
docker ps
```
and find the web container replace conversion-web-1 with your web container
