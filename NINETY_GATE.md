# Shadow Faker — le vrai seuil de 90 %

![Précision exacte selon la part des décisions auxquelles Shadow répond](docs/figures/ninety_exact_gate.png)

## Cible mesurée

À partir de l'état disponible à la minute `t`, Shadow propose **une seule des 64 cases 8×8** où le compte attribué à Faker se trouvera à la prochaine frame Riot, environ une minute plus tard. Une réponse est juste seulement si cette **case unique** est la case observée. La « couverture » du graphique ci-dessus est la **part de transitions auxquelles le modèle accepte de répondre** ; elle ne désigne jamais une surface de carte. La [couverture top-k](RESULTS.md) avec 41 cases candidates sur 64 est une autre mesure et ne satisfait pas cette cible.

| Transitions servies, classées par confiance | Réponses justes | Précision exacte | Borne Wilson 95 % |
|---:|---:|---:|---:|
| 5 % · 64/1 275 | 31 | **48,44 %** | 36,63 % |
| 10 % · 128/1 275 | 48 | 37,50 % | 29,59 % |
| 20 % · 255/1 275 | 95 | 37,25 % | 31,55 % |
| 50 % · 638/1 275 | 178 | 27,90 % | 24,56 % |
| 100 % · 1 275/1 275 | 223 | 17,49 % | 15,50 % |

La confiance aide à classer quelques cas : les 5 % les plus confiants font mieux que la moyenne. **Même ce groupe reste très loin de 90 %.** Deux moitiés de **23 matchs chacune** choisissent réciproquement un seuil sur l'une puis l'appliquent à l'autre. Aucun seuil ne satisfait le contrat fixé avant l'audit : au moins **10 %** des transitions et **50 exemples** servis, avec borne inférieure Wilson 95 % ≥ **90 %** sur calibration **et** évaluation. Ce résultat mesure un échec du seuil, pas une preuve d'impossibilité universelle.

## Provenance et verrouillage

- **Modèle :** checkpoint M3 hiérarchique « full » et prior rôle/phase déjà enregistrés, SHA-256 vérifié avant l'inférence. Le pilote de cinq parties a donné 143 transitions ; l'audit complet a lu les **46 parties de validation / 1 275 transitions**. Ni l'ancien test historique ni le lockbox prospectif n'ont été chargés.
- **Ordre des opérations :** le modèle trie par sa probabilité maximale d'une case unique. Les couvertures 5/10/20/50/100 % sont fixées dans le code. Les deux moitiés de matchs sont choisies par seed 42, sans partage de frame entre calibration et évaluation. L'intervalle de Wilson prend les réponses exactes parmi les transitions servies ; il ne remplace pas un bootstrap par match sur une cohorte future.
- **Limite fondamentale :** ce checkpoint, son époque et son prior ont **déjà été choisis sur ces 46 parties de validation** dans les expériences M3. La séparation réciproque des seuils évite de choisir un seuil sur les labels de sa moitié d'évaluation, mais **ne rend pas le modèle indépendant de la cohorte**. Tous les chiffres restent exploratoires.
- **Disponibilité :** le snapshot Riot `20261011` a reçu HTTP 401 avec la clé locale expirée. Le lockbox M0 reste à **0/100 nouvelles parties utilisables** ; aucun score futur n'a été ouvert. La clé doit être renouvelée dans `.env` pour poursuivre la collecte. Ne jamais publier cette clé.

## Ce qui peut réellement faire progresser le modèle

1. **Ajouter des observations, pas seulement des pixels.** Les timelines disponibles donnent une position environ par minute ; la décision, les clics, les pings, la voix et la vision exacte de Faker ne sont pas observés. Un replay ou une VOD autorisés et alignés avec un match identifié peut fournir des annotations plus proches de la seconde, avec leur point de vue et leurs zones inconnues explicités.
2. **Construire des labels d'action vérifiables.** Déplacement, reset, contestation d'objectif et pression doivent être horodatés et distingués de l'intention supposée. Une annotation par deux personnes sur un pilote de cinq parties et un accord interannotateurs précèdent tout entraînement.
3. **Geler une nouvelle cohorte.** Réentraîner uniquement sur des parties de développement et préenregistrer la cible, la résolution, les baselines, l'abstention éventuelle et la couverture minimale. Une future cohorte d'au moins 100 parties, strictement postérieure au gel, est nécessaire pour une affirmation prospective. Le seuil de 90 % doit être atteint sur **la case exacte**, avec couverture et intervalle publiés ; une classe « pas d'action » dominante ou une grande zone proposée ne compte pas.

Reproduire l'audit local :

```bash
.venv/bin/python scripts/run_ninety_gate.py --pilot-only
.venv/bin/python scripts/run_ninety_gate.py
.venv/bin/python scripts/render_ninety_gate.py
.venv/bin/python scripts/run_prospective.py --offline
```

Le JSON public [public_ninety_gate.json](docs/data/public_ninety_gate.json) ne contient aucun identifiant de partie ou prédiction individuelle. Les parties brutes et le checkpoint demeurent locaux.
