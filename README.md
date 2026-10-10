# Champions League · Dashboard automático

1. Crie uma conta grátis em https://www.football-data.org/client/register e copie o token (plano grátis inclui a Champions).
2. Crie um repositório **público** no GitHub e envie esta pasta (público = Actions sem limite de minutos).
3. Settings → Secrets and variables → Actions → New secret: `FOOTBALL_DATA_TOKEN` = seu token.
4. Settings → Pages → Source: *Deploy from a branch* → `main` / root.
5. Aba Actions → "Atualizar dados da Champions" → *Run workflow* para testar a 1ª execução.

O workflow roda a cada 10 min (ter–qui, 15h–23h UTC) e a cada 3 h nos demais horários, e só faz commit quando algo mudou.
O site relê `data/matches.json` a cada 60 s. Para trazer temporadas passadas: rode localmente
`FOOTBALL_DATA_TOKEN=... SEASONS=2024,2025,2026 python scripts/update.py` (o plano grátis pode limitar o histórico).
