# OCC Énergie — parcours départ → réseau → implantation → façade

## Objet

À partir d’un nom ou repère de départ, conserver la sélection dans les vues de
l’application jusqu’à la position documentaire de la case sur la façade.

Cette fonctionnalité aide à retrouver un équipement ; **elle ne valide aucun
cheminement physique de câble, aucun état de fermeture de disjoncteur, et
aucune manœuvre**.

## Mode opératoire

1. Dans **Réseau**, saisir un nom, une case ou un repère dans la recherche
   prédictive ; choisir le bon élément parmi les suggestions.
2. La vue **Schéma complet** est activée pour les départs ; le chemin amont
   documentaire apparaît sous forme de repères cliquables. Les **segments
   existants sur le SVG**, correspondant au chemin choisi, prennent une
   surbrillance jaune (orange pointillé si incertains).
3. Cliquer sur **Localiser sur l’usine**. La vue aérienne centre le bâtiment
   uniquement si `loc.bat` correspond explicitement à une zone du site.
   Aucun point précis n’est deviné.
4. Si le tableau figure dans un plan du local, choisir **Voir l’implantation
   du tableau**. Le bon tableau est ciblé ; le départ sélectionné reste
   identifié dans le bandeau.
5. Si le départ est présent dans `D.facades`, choisir **Ouvrir la façade et
   surligner le départ** : zoom/halo sur l'appareil et sa case documentée.
   Sinon, l'interface indique que la position exacte n’est pas renseignée.

## Traçabilité et limites importantes

- Le moteur `bestPath()` sélectionne **un parcours normal décrit par le
  modèle** ; d'autres cheminements théoriques peuvent exister (couplages,
  secours). Ce parcours n'est ni une mesure de tension ni une configuration
  actuellement observée. Les divergences documentaires restent actives.
- Tous les départs ne sont pas représentés graphiquement individuellement
  sur le schéma de principe. Leur chemin complet est accessible sous forme de
  repères ; **seuls les vrais segments SVG dessinés** peuvent être surlignés.
  Aucun câble supplémentaire n'est tracé entre deux bâtiments.
- Le périmètre d'un bâtiment affiché sur orthophoto ne donne pas l'emplacement
  exact d'une armoire. Un plan local ou une façade n'est accessible que si sa
  référence existe dans les données.
- Une case n'est mise en évidence que si elle est associée dans le modèle
  photographique ou vectoriel à un identifiant d'équipement.
- Une source ou liaison `probable`, `a_verifier` ou `inconnu` ne devient
  pas `confirme` parce qu'elle figure à l'écran.
- Les incohérences TR1A/TR2A et les noms divergents des sous-stations doivent
  rester visibles tant qu’elles n’ont pas été validées sur le terrain.

## Contrôles automatiques

Le test Playwright `tests/smoke_reseau.py` vérifie l’accès à une recherche,
la mise en évidence des segments, l'ouverture du bâtiment, du plan local,
puis de la façade, sur un départ du TGBT 2 renseigné dans le modèle.
La CI reconstruit le HTML et compare les fichiers générés ; la PR doit
rester ouverte si un contrôle est rouge.

## Travail documentaire restant

Établir pour chaque équipement : tableau amont, repère de départ, bâtiment
et local vérifiés, plan d'implantation, numéro de colonne et position en
façade, et source/date du relevé. Les façades ou localisations absentes
doivent rester explicitement manquantes, jamais remplacées par un dessin fictif.
