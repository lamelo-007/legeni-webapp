# Rapport – Chaîne CI/CD Legeni WebApp

## 1. Ce qui a été réalisé
- Image Docker multi-stage (flake8 + pytest), utilisateur non-root, HEALTHCHECK, version injectée par argument de build.
- Qualité et sécurité : hadolint sans erreur, scan Trivy sans faille CRITICAL corrigeable.
- Ansible : `provision.yml` installe Minikube (idempotent), `deploy.yml` déploie sur Kubernetes, secrets chiffrés avec Ansible Vault.
- Kubernetes : namespaces `legeni-staging` et `legeni-prod` ; Redis en StatefulSet avec volume persistant ; mot de passe dans un Secret ; sondes `/ready` et `/health` ; RollingUpdate avec `maxUnavailable: 0`.
- Rollback automatique (`block/rescue`) démontré avec une version inexistante (9.9.9).

## 2. Preuves (captures)
| Capture | Ce qu'elle prouve |
|---|---|
| `kubectl get all -n legeni-prod` | 3 copies de l'application et Redis tournent en production |
| PLAY RECAP staging | le même playbook déploie l'environnement de test |
| PLAY RECAP 9.9.9 (`rescued=1`) | un déploiement raté déclenche un retour arrière automatique |
| `kubectl get deploy -o wide` | après l'échec, la production est revenue à la version saine |
| 2e passage `failed=0` | rejouer le déploiement ne casse rien |
| PLAY RECAP `provision.yml` | l'installation est idempotente |
| Trivy code retour 0 | aucune faille critique corrigeable dans l'image |

## 3. Difficultés rencontrées et solutions
- Ansible ignorait `ansible.cfg` (dossier accessible en écriture à tous dans Codespaces) : `chmod o-w` et option `-i inventory.ini`.
- Pods en `ImagePullBackOff` : le tag chargé dans Minikube (`1.0.0`) ne correspondait pas au tag déployé (`1.0.0-0`) : `docker tag` puis `minikube image load`.

## 4. Limites (honnêteté)
- Jenkins n'a pas été configuré (credentials, job multibranch, webhook) : le pipeline n'a pas été exécuté de bout en bout.
- Image non publiée sur Docker Hub (image locale chargée dans Minikube) ; pas de notification.

## 5. Pistes d'amélioration
Terminer le pipeline Jenkins, Ingress + TLS, HPA, Prometheus/Grafana.

## 6. Incident de sécurité et correction
Lors d'un `git add .` sur `main`, le fichier `.vault_pass` a été commité et poussé par erreur. Actions menées :
- historique de `main` réécrit (`git reset` puis `git push --force-with-lease`) : `git log --all -- .vault_pass` ne renvoie plus rien ;
- mot de passe du coffre Ansible Vault et mots de passe Redis régénérés, secrets Kubernetes réappliqués par Ansible ;
- `.vault_pass` ajouté au `.gitignore`, et `git add` désormais fait fichier par fichier après contrôle de `git status`.
Limite : GitHub peut conserver quelque temps d'anciens commits accessibles par leur numéro, d'où la rotation des secrets.
