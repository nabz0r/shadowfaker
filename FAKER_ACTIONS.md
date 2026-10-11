# Shadow Faker — événements attribués à Faker dans les 10 secondes

**Mise à jour M18/M19 :** le [challenger assaini](DATA_SANITATION.md) contrôle les sources et ajoute onze variables connues à la dernière frame ; sur les mêmes 46 matchs de validation, l'AP moyenne des quatre actes observables passe de 14,93 % à 17,40 %. Les dix anciennes distances par rôle utilisent toutefois `teamPosition` du match achevé, une métadonnée potentiellement rétrospective. Le [nouvel export IoC strict](IOC_LEDGER.md) les retire pour les expériences futures. Le modèle M16 décrit ci-dessous reste gelé comme référence ; aucune nouvelle cohorte indépendante n'a encore confirmé le gain.

![Précision moyenne par famille sur 46 parties de validation](docs/figures/faker_actions_10s.png)

## Ce que le modèle prédit

À un instant `t` pris toutes les dix secondes, le modèle reçoit **la dernière frame Riot disponible** et les événements déjà horodatés `≤ t`. Il produit sept probabilités distinctes : au moins un événement explicitement attribué au PUUID cible dans `(t, t+10 s]` pour chacune des familles ci-dessous. Plusieurs familles peuvent être positives dans la même fenêtre. Les features d'état viennent du [modèle d'horloge événementielle](src/shadowfaker/event_clock.py) ; leur vue des dix joueurs est omnisciente et **n'est pas la minimap réellement visible de Faker**.

| Famille | Champ Riot qui attribue l'événement | Sens |
|---|---|---|
| Achat | `ITEM_PURCHASED.participantId` | Achat enregistré ; choix d'objet non prédit ici. |
| Compétence | `SKILL_LEVEL_UP.participantId` | Point dépensé ; slot non prédit ici. |
| Ward posée | `WARD_PLACED.creatorId` | Pose enregistrée ; lieu non fourni pour cette cohorte. |
| Ward détruite | `WARD_KILL.killerId` | Destruction enregistrée. |
| Kill | `CHAMPION_KILL.killerId` | **Issue** favorable attribuée, pas intention de tuer. |
| Mort | `CHAMPION_KILL.victimId` | **Issue** défavorable attribuée. |
| Assistance | `CHAMPION_KILL.assistingParticipantIds` | Participation attribuée à une issue. |

Les événements automatiques `LEVEL_UP` et `ITEM_DESTROYED` sont exclus. Le label est zéro si aucun événement de la famille n'a été observé dans la fenêtre. Il ne signifie pas que Faker n'a rien fait : clics, mouvement et communication ne sont pas observés. Les timestamps exactement à `t` sont déjà passés ; ceux au-delà de `t+10 s` ne sont pas labels. Un premier délai par famille est conservé localement pour une future tête temporelle, sans être exploité comme feature.

## Cohorte et séparation

Pilote : **5 matchs**, 737 fenêtres (420 train, 317 validation), avec tests sur attribution et frontière temporelle. Corpus complet : **465 matchs** et **73 482 fenêtres**, 0 erreur ; split préexistant par match **373 train / 46 validation / 46 test**, soit 58 974 / 7 480 / 7 028 fenêtres. Le test historique et la future cohorte ne servent ni au choix d'époque ni aux chiffres ci-dessous. Les fenêtres se chevauchent dans un match ; l'intervalle de confiance rééchantillonne les **matchs**, pas les fenêtres.

Un MLP de **13 575 paramètres** lit les 37 variables historiques déjà extraites, avec sept sorties sigmoid. Entraînement BCE, seed 42, AdamW et arrêt après quatre époques sans baisse de perte de validation ; meilleur checkpoint à l'époque **25**, fin à l'époque **29**. Petit modèle exécuté sur CPU. Deux références sont ajustées uniquement sur train : fréquence globale par classe et fréquence par phase (<10, 10–20, ≥20 min), toutes deux lissées. Le modèle n'utilise pas de score final de partie en entrée ; la provenance rétrospective possible des tags de rôle est signalée ci-dessus.

## Résultat exploratoire sur 46 matchs de validation

La **perte log moyenne par famille et fenêtre** est **0,19427** pour Shadow, **0,20481** pour la règle par phase et **0,20745** pour la fréquence globale. Gain apparié sur la règle par phase : **0,01054** en perte log (IC bootstrap par match 95 % **[0,00906 ; 0,01211]**). Brier : **0,04944** contre **0,05103**. La précision moyenne (*average precision*, aire sous la courbe précision–rappel à seuils successifs) vaut **0,12110** en moyenne simple des sept familles, contre **0,06600** pour la règle par phase. Ce n'est ni une accuracy de 12,1 %, ni une réussite à 90 %.

| Famille | Fenêtres positives | Prévalence | Shadow AP | Phase AP |
|---|---:|---:|---:|---:|
| Achat | 616 | 8,24 % | **24,09 %** | 8,68 % |
| Compétence | 712 | 9,52 % | **18,54 %** | 12,14 % |
| Ward posée | 486 | 6,50 % | **10,52 %** | 6,74 % |
| Ward détruite | 240 | 3,21 % | **6,57 %** | 4,64 % |
| Kill (issue) | 307 | 4,10 % | **7,67 %** | 5,01 % |
| Mort (issue) | 222 | 2,97 % | **7,52 %** | 3,65 % |
| Assistance (issue) | 289 | 3,86 % | **9,86 %** | 5,35 % |

Le signal d'achat est le plus net. Les kills restent rares et difficiles : une AP de 7,67 % signifie un classement un peu meilleur qu'une règle par phase, **pas** que Shadow sait annoncer un kill individuel. Dire systématiquement « aucun événement » réussirait **49 488/52 360 = 94,51 %** des décisions binaires par famille, tout en ratant **les 2 872 positifs**. C'est pourquoi 90 % d'accuracy brute ne serait pas un progrès. La performance varie selon la phase ; le panneau Scores du site suit la chronologie commune et permet de revenir au total. Cette validation a déjà servi à d'autres expériences ; ses chiffres sont du **développement**, pas une confirmation indépendante. La cible reste « événement dans les dix secondes », sans lieu exact, temps exact, vision, pression causale ni probabilité de victoire.

## Reproduire depuis le cache local

```bash
PYTHONPATH=src .venv/bin/python scripts/run_faker_actions.py --pilot-only
PYTHONPATH=src .venv/bin/python scripts/run_faker_actions.py
PYTHONPATH=src .venv/bin/python scripts/train_faker_actions.py --pilot-only
PYTHONPATH=src .venv/bin/python scripts/train_faker_actions.py
.venv/bin/python scripts/render_faker_actions.py
.venv/bin/python -m pytest -q tests/test_faker_actions.py
```

Les fichiers NPZ par match, les identifiants, les pertes par match et le checkpoint restent sous `data/`, `artifacts/` et `models/`, exclus de Git. Le [JSON public](docs/data/public_faker_actions_10s.json) ne contient que des agrégats. L'ancienne [analyse de disponibilité à la seconde](SECOND_SCALE.md) explique pourquoi ces probabilités d'événement ne peuvent être converties en trajectoires de Faker. La prochaine preuve est une **nouvelle cohorte** pour le score événementiel et un **replay/POV aligné** pour les positions plus fréquentes.
