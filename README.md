# Newswire

## Installation

Comment out 'members' from INSTALLED_APPS

```
docker-compose build
docker-compose run --rm web python manage.py migrate auth
docker-compose run --rm web python manage.py migrate
docker-compose run --rm web python manage.py createsuperuser
```

Un-comment 'members' from INSTALLED_APPS

```docker-compose build
docker-compose run --rm web python manage.py migrate
```
