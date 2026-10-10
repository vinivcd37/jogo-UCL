#!/usr/bin/env python3
"""Busca jogos da Champions na football-data.org e atualiza data/matches.json.
Requer a variavel FOOTBALL_DATA_TOKEN. SEASONS=2025,2026 (ano de inicio) opcional."""
import json, os, sys, datetime as dt, urllib.request, urllib.error
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "matches.json"
STAGES = {"LEAGUE_STAGE": "Fase de liga", "PLAYOFFS": "Playoffs", "LAST_16": "Oitavas",
          "QUARTER_FINALS": "Quartas", "SEMI_FINALS": "Semifinal", "FINAL": "Final"}
ALIASES = {"Paris Saint-Germain": "PSG", "Paris Saint-Germain FC": "PSG", "FC Bayern München": "Bayern",
           "Bayern Munich": "Bayern", "Manchester City FC": "Man City", "Manchester United FC": "Man United",
           "Club Atlético de Madrid": "Atlético de Madrid", "Atleti": "Atlético de Madrid",
           "FC Internazionale Milano": "Inter", "Inter Milan": "Inter", "FC Barcelona": "Barcelona",
           "Real Madrid CF": "Real Madrid", "Sporting CP": "Sporting CP", "Borussia Dortmund": "Dortmund",
           "Liverpool FC": "Liverpool", "Arsenal FC": "Arsenal", "Chelsea FC": "Chelsea"}

def team(t):
    n = t.get("shortName") or t.get("name") or "?"
    return ALIASES.get(n, ALIASES.get(t.get("name"), n))

def fetch(season):
    if os.environ.get("MOCK_FILE"):
        return json.load(open(os.environ["MOCK_FILE"]))["matches"]
    req = urllib.request.Request(
        f"https://api.football-data.org/v4/competitions/CL/matches?season={season}",
        headers={"X-Auth-Token": os.environ["FOOTBALL_DATA_TOKEN"]})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["matches"]

def convert(m, season):
    st = {"FINISHED": "FT", "IN_PLAY": "LIVE", "PAUSED": "LIVE"}.get(m["status"])
    if not st:
        return None  # agendado/adiado: nao entra
    s, dur = m["score"], m["score"].get("duration", "REGULAR")
    out = {"season": f"{season}/{str(season + 1)[2:]}", "date": m["utcDate"][:10],
           "stage": STAGES.get(m.get("stage"), m.get("stage", "")),
           "home": team(m["homeTeam"]), "away": team(m["awayTeam"]), "status": st}
    if dur == "PENALTY_SHOOTOUT":  # fullTime pode incluir os penaltis: soma tempo normal + prorrogacao
        rt, et, pk = s.get("regularTime") or {}, s.get("extraTime") or {}, s.get("penalties") or {}
        out["hg"] = (rt.get("home") or 0) + (et.get("home") or 0)
        out["ag"] = (rt.get("away") or 0) + (et.get("away") or 0)
        out["pen"] = f'{pk.get("home")}-{pk.get("away")}'
    else:
        ft = s.get("fullTime") or {}
        out["hg"], out["ag"] = ft.get("home") or 0, ft.get("away") or 0
        if dur == "EXTRA_TIME":
            out["aet"] = True
    return f'fd-{m["id"]}', out

def main():
    now = dt.date.today()
    default = now.year if now.month >= 7 else now.year - 1
    seasons = [int(x) for x in os.environ.get("SEASONS", str(default)).split(",")]
    old = json.load(open(OUT)) if OUT.exists() else {"matches": {}}
    matches = dict(old["matches"])
    for y in seasons:
        label = f"{y}/{str(y + 1)[2:]}"
        try:
            raw = fetch(y)
        except urllib.error.HTTPError as e:
            sys.exit(f"Erro HTTP {e.code} na temporada {y}: {e.read()[:200]!r}")
        matches = {k: v for k, v in matches.items() if v["season"] != label}  # substitui a temporada
        for m in raw:
            c = convert(m, y)
            if c:
                matches[c[0]] = c[1]
    if matches == old["matches"]:
        print("Sem mudancas."); return
    OUT.write_text(json.dumps({"updated": dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds") + "Z",
                               "matches": dict(sorted(matches.items()))}, ensure_ascii=False, indent=1))
    print(f"Atualizado: {len(matches)} partidas.")

if __name__ == "__main__":
    main()
