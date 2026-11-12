# Isometrisch Opperdoes

Gebied: RD New EPSG:28992, 132500–135500 / 528500–531500 (3 × 3 km).
PDOK woonplaatsmiddelpunt: 134006.545, 530038.617.

De README van het voorbeeld is behouden als documentatie van de pijplijn.
Lokale aanpassingen staan in config.py, fetch.py, landmarks.py, build_history.py en de viewer.
De Helenaveense rondleiding is leeg en verborgen; lokale verhalen kunnen later worden toegevoegd.
De twee kerken, De Skoôt en het wandelstartpunt zijn gebaseerd op de opgehaalde OSM-data.
Wandelroutes waren tijdens deze bouw niet beschikbaar (Overpass-time-out).

Bouwen: ./build.sh. Lokaal bekijken: python3 -m http.server 8000 -d site.
Publiceren: ./deploy.sh (naar origin, nooit naar upstream).

Licenties en bronvermelding: viewer/credits.html. De voorbeeldrepository bevat geen softwarelicentie;
er wordt daarom geen eigen licentie over de overgenomen code geplaatst.
