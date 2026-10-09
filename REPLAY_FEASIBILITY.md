# Replays et vidéo : voie d'enrichissement vérifiée

## État constaté le 2026-10-09

- Aucun client League of Legends, fichier `.rofl` ou VOD de partie LoL n'a été trouvé dans les emplacements locaux examinés. L'API Replay locale `https://127.0.0.1:2999/replay/game` refuse la connexion, car aucun replay n'est ouvert.
- Le [support Riot sur les replays](https://support.riotgames.com/fr-fr/league-of-legends/gameplay/replays-faq-pro-tips/) indique que les fichiers `.rofl` se téléchargent via le client, restent valables pendant un cycle de patch et que seules les 20 dernières parties sont accessibles dans l'historique du client. Le chat de partie n'est pas inclus dans le replay.
- La [documentation Riot Replay API](https://developer.riotgames.com/docs/lol) fournit des commandes de lecture, seek, caméra/rendu et enregistrement pour **un replay déjà ouvert dans le client local**. Elle ne fournit pas d'endpoint de téléchargement des replays historiques par match ID. L'API match-v5 utilisée ici expose match et timeline, pas la vidéo ni la perspective de Faker.

## Chemin concret si des replays/vidéos deviennent disponibles

1. Enregistrer localement des `.rofl` du patch courant ou des VOD liées à des match IDs précis. Conserver la provenance, le patch, le match ID et la synchronisation entre horloge vidéo et timeline.
2. Ouvrir les `.rofl` dans le client Riot. Activer l'API Replay officielle, régler la caméra et la vision de l'équipe, puis exporter une vidéo via l'API de recording. Ne pas traiter la vue spectateur globale comme la vision de Faker.
3. Sur la vidéo exportée, extraire les images de minimap et annoter les positions visibles, wards et pings avec des horodatages et un score de confiance. Vérifier manuellement un petit échantillon ; les icônes et l'interface changent selon le patch.
4. Joindre ces annotations au dataset **par match ID et temps**, sans regarder les minutes futures. Comparer, sur les mêmes parties test, la vue proxy actuelle, la vue omnisciente et la vue issue de la vidéo.
5. Si une VOD contient un commentaire parlé, le transcrire séparément et l'identifier comme commentaire du créateur de la VOD. Un `.rofl` ne fournit ni le chat de la partie, ni une transcription vocale des communications de l'équipe.

Ce module vidéo ne peut pas être validé pour les 470 parties actuelles sans replay ou VOD correspondante. Construire une interface qui prétend extraire la vision ou les communications de Faker depuis les JSON match-v5 fabriquerait des données. Le pipeline actuel conserve les JSON localement et une séparation des vues pour accueillir des annotations vidéo plus tard.
