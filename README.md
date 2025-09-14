# synchronizer

Minimalny kontener do uruchamiania zadań rclone zdefiniowanych w /config/jobs.json.

## Konfiguracja (jedyny sposób)
Zamontuj katalog z plikami konfiguracyjnymi pod ścieżką /config w kontenerze.
Wymagane pliki:
- rclone.conf
- jobs.json

Struktura lokalna przykładowo:
```
config/
  rclone.conf
  jobs.json
```

## Plik jobs.json
Struktura podstawowa:
```
{
  "dry-run": false,            // opcjonalne; gdy true dodaje --dry-run do rclone
  "schedule": "0 2 * * *",    // opcjonalne; 5-polowy cron (min godz dzien mies dzien_tyg) lub skrót @hourly/@daily/@weekly/@monthly
  "jobs": [
    { "source": "remote1:/path", "destination": "remote2:/other_path" },
    { "source": "remote3:/", "destination": "remote4:/backup" }
  ]
}
```
Każdy obiekt w `jobs` musi mieć pola `source` i `destination` w formacie akceptowanym przez rclone (REMOTE:path).

### Harmonogram (schedule)
Jeśli pole `schedule` jest pominięte – zadania uruchamiane są raz i kontener kończy pracę.
Jeśli `schedule` jest ustawione – używany jest APScheduler (CronTrigger) i kontener pozostaje aktywny.

Obsługiwane skróty:
- `@hourly`  -> `0 * * * *`
- `@daily`   -> `0 0 * * *`
- `@weekly`  -> `0 0 * * 0`
- `@monthly` -> `0 0 1 * *`

Przykład: codziennie o 02:00
```
{
  "schedule": "0 2 * * *",
  "jobs": [ { "source": "r1:/", "destination": "r2:/backup" } ]
}
```

### Zmienne środowiskowe
- `ONESHOT=1` – ignoruje schedule i wykonuje pojedyncze uruchomienie.
- `RUN_IMMEDIATELY=0` – przy aktywnym schedule pomija natychmiastowe uruchomienie i czeka do pierwszego slotu (domyślnie = natychmiastowy run + dalsze wg cron).

Przykład jednorazowego testu (mimo ustawionego schedule):
```
# docker run -e ONESHOT=1 ...
{
  "schedule": "0 2 * * *",
  "dry-run": true,
  "jobs": [ { "source": "r1:/", "destination": "r2:/" } ]
}
```

### Tryb testowy (dry-run)
Aby zobaczyć planowane operacje bez zmian:
```
{
  "dry-run": true,
  "jobs": [ { "source": "remote1:/", "destination": "remote2:/backup" } ]
}
```

### Logika wykonywania
1. Walidacja plików rclone.conf i jobs.json.
2. (Opcjonalnie) pojedynczy run jeśli brak schedule lub ustawiono ONESHOT.
3. Przy schedule tworzony jest BlockingScheduler + CronTrigger.
4. `max_instances=1` i `coalesce=true` – nakładające się ticki nie spowodują równoległych synców; zaległe zostaną scalone.

### Uwaga
Wyrażenie cron musi mieć dokładnie 5 pól lub być jednym ze skrótów. Błędny format zakończy proces z komunikatem błędu.
