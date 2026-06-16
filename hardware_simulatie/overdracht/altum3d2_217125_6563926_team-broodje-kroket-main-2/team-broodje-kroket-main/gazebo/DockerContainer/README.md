# DockerContainer

Minimale Docker setup voor het teamproject.

## Vereisten
- Docker Desktop

## Gebruik
Open een terminal in deze map (`team-broodje-kroket/DockerContainer`) en run:

```bash
docker compose up -d
```

Ga daarna de container in:

```bash
docker compose exec team-project bash
```

Stoppen:

```bash
docker compose down
```

## Opmerking
De projectmap wordt gemount op `/workspace`, zodat alle teamleden met dezelfde bestanden werken na `git clone` of `git pull`.
De compose setup gebruikt image `s4_2026:latest`.

Als die nog niet lokaal bestaat, laad hem eerst in:

```bash
docker load -i /pad/naar/s4_2026.tar
```

## Dev Container (VS Code)
Er is ook een devcontainer-config aanwezig op `team-broodje-kroket/.devcontainer/devcontainer.json`.

1. Open de repo in VS Code.
2. Zorg dat Docker Desktop draait.
3. Kies `Dev Containers: Reopen in Container`.

Daarna werk je direct in dezelfde container-omgeving als de rest van het team.
