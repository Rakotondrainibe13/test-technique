# RAKOTONDRAINIBE Sambatra Mario- CODE REVIEW
=========
## Ordre de priorité pour la revue de code:
- Remarques bloquantes (must fix)
- Correctifs

1) Remarques bloquantes (must fix)
-------------------------------------
1. Authentification dangereuse : le code compare directement `user.password == password` — un password doit toujours être crypté.
2. L'API d'auth ne retourne pas de token JWT ou session sécurisée, donc pas de gestion d'état utilisateur.Utiliser le JWT et le DRF.
3. Pas de validation ni sérialisation : lecture directe de `json.loads(request.body)` et assignation brute -> erreurs et injection possible.
4. Gestion d'erreur minimale : `objects.get()` lève 500 si rien, aucune gestion 404/400, pas de codes HTTP corrects.
6. Le `print()` en synchrone c'est inutile et bloquant. Utilise plutôt des logging et déplace l'envoi d'email dans une tâche asynchrone.

2) Correctifs 
--------------------------
- Remplacer la logique de login par Django : utiliser `authenticate()` et `djangorestframework-simplejwt` pour renvoyer access/refresh tokens.
- Remplacer `json.loads(request.body)` + `JsonResponse` par des vues DRF (`APIView`/`ViewSet`) et `serializers` pour valider `title`, `content`, `status`.
- Remplacer `Article.objects.get()` par `get_object_or_404()` ou gérer `DoesNotExist` et renvoyer `Response(..., status=404)`.
- Ne pas accepter `author_id` non vérifié : utiliser `request.user` comme auteur par défaut.
- Remplacer `print()` par `logging` et déplacer l'envoi d'email dans une tâche asynchrone (ou au moins `send_mail` hors requête).


