# RAKOTONDRAINIBE Sambatra Mario - Test Technique

## Exigences
---------
- Docker & Docker Compose
- (Optionnel local) Python 3.11 + virtualenv

## Démarrage rapide (Docker)
-------------------------
Depuis la racine du repo :

## Build et lancer (en arrière-plan)
docker-compose build web && docker-compose up -d

## Suivre les logs (facultatif)
docker-compose logs -f web

## Commandes utiles
----------------
### Superuser et comptes de test
### Les 3 comptes de test sont créés automatiquement au démarrage (script d'init dans l'image)
### - Admin : username `admin` / password `adminpass`
### - Editor: username `editor` / password `editorpass`
### - Reader: username `reader` / password `readerpass`

### Si vous avez besoin d'un superuser supplémentaire (par exemple pour accéder à l'admin Django), créez‑le explicitement :
### (zsh)
#### docker-compose run --rm web python manage.py createsuperuser

### Lancer les tests de l'application articles (dans le conteneur)
docker-compose run --rm web python manage.py test articles


### Profils de test (déjà créés par le script d'init)
-------------------------------------------------
Pour tester rapidement l'API vous pouvez utiliser ces comptes :
- Admin : username `admin` / password `adminpass`
- Editor: username `editor` / password `editorpass`
- Reader: username `reader` / password `readerpass`


### Collections Postman
-------------------
Les collections Postman sont dans le dossier `collections/` : importez-les dans Postman pour tests rapides:
- `API Articles.postman_collection.json` : endpoints articles
- `User.postman_collection.json` : endpoints auth/utilisateurs

### Notes rapides
-------------
- Si Postgres a déjà un volume initialisé, les variables POSTGRES_* sont prises en compte seulement à la première initialisation du volume.
- Si les migrations échouent au démarrage, relancer après `docker-compose run --rm web python manage.py migrate`.

##### Remarques: Pour exécuter manuellement une commande Django dans le conteneur, l'exemple suivant lance les migrations :
docker-compose run --rm web python manage.py migrate --noinput