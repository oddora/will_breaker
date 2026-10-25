# Session 041 Sports Forecast Ledger (Cryptographically Sealed)

- **Date:** 2026-10-25 19:00:49 UTC
- **Model:** KAT MoE 35B (`kat` on `:18283`)
- **Games Evaluated:** 11 (5 NFL, 5 NBA)
- **Sealed Commitments:** 22 (10 ATS, 10 Moneyline)
- **Registry:** `notes/crypto_predictions_registry.jsonl`

| Sport | Matchup | Market Line | KAT ATS Pick | Prob | ATS Seal | KAT Moneyline | Prob | ML Seal |
|-------|---------|-------------|--------------|------|----------|---------------|------|---------|
| NFL | Denver Broncos @ Arizona Cardinals | Arizona Cardinals -1.5 | **Arizona Cardinals -1.5** | 0.53 | `commit_cf7bd514b3d6` | **Arizona Cardinals** | 0.54 | `commit_a3bf8b58762f` |
| NFL | Green Bay Packers @ Detroit Lions | Detroit Lions -4.5 | **Detroit Lions -4.5** | 0.54 | `commit_48679b5ac33b` | **Detroit Lions** | 0.64 | `commit_53b31c4acaa8` |
| NFL | Los Angeles Rams @ Las Vegas Raiders | Los Angeles Rams -3.0 | **Los Angeles Rams -3.0** | 0.54 | `commit_c42377c30e95` | **Los Angeles Rams** | 0.62 | `commit_3afb12d96ef2` |
| NFL | Kansas City Chiefs @ Seattle Seahawks | Seattle Seahawks -2.5 | **Seattle Seahawks -2.5** | 0.53 | `commit_36f8c7aa39e3` | **Kansas City Chiefs** | 0.54 | `commit_4dfeac61a351` |
| NBA | Indiana Pacers @ Brooklyn Nets | Indiana Pacers -7.5 | **Indiana Pacers -7.5** | 0.55 | `commit_a57f38f73c68` | **Indiana Pacers** | 0.65 | `commit_a58e848177f1` |
| NBA | Orlando Magic @ New York Knicks | New York Knicks -7.5 | **New York Knicks -7.5** | 0.58 | `commit_92f3d184216f` | **New York Knicks** | 0.72 | `commit_05362974ec17` |
| NBA | Toronto Raptors @ Minnesota Timberwolves | Minnesota Timberwolves -1.5 | **Minnesota Timberwolves -1.5** | 0.53 | `commit_8c1c5bf8f435` | **Minnesota Timberwolves** | 0.54 | `commit_1cf13eaa0bef` |
| NBA | Detroit Pistons @ Philadelphia 76ers | Philadelphia 76ers -1.5 | **Philadelphia 76ers -1.5** | 0.53 | `commit_280e97e5cc87` | **Philadelphia 76ers** | 0.54 | `commit_271c8313e66e` |
| NBA | Los Angeles Lakers @ Utah Jazz | Los Angeles Lakers -6.5 | **Los Angeles Lakers -6.5** | 0.56 | `commit_a0e4be7f855f` | **Los Angeles Lakers** | 0.64 | `commit_0da95a37a230` |
| NBA | LA Clippers @ Oklahoma City Thunder | Oklahoma City Thunder -15.5 | **Oklahoma City Thunder -15.5** | 0.58 | `commit_9d8fbdefbd55` | **Oklahoma City Thunder** | 0.82 | `commit_c26464d5f1e7` |
| NBA | Memphis Grizzlies @ Sacramento Kings | Memphis Grizzlies -3.5 | **Memphis Grizzlies -3.5** | 0.54 | `commit_83ecb0667db6` | **Memphis Grizzlies** | 0.58 | `commit_bd3d1721f482` |

### Analytical Rationales

- **Denver Broncos @ Arizona Cardinals (NFL):** Cardinals at home on fast turf at State Farm Stadium give Arizona a slight edge in a near pick'em market. The 41.5 total is below league average, but Arizona's offensive upside at home on a quick surface pushes the over slightly above fair value.
- **Green Bay Packers @ Detroit Lions (NFL):** Lions' high-powered indoor offense at Ford Field gives them a clear edge against a vulnerable Packers secondary. The 51.5 total is well-suited for two pass-heavy offenses, and Detroit's home-field advantage in a dome environment supports both the spread and the over.
- **Los Angeles Rams @ Las Vegas Raiders (NFL):** Rams' balanced offensive scheme and superior roster talent give them a slight edge in a divisional-adjacent matchup; the low 43.5 total reflects both defenses' ability to limit explosive plays, with Vegas' home-field advantage keeping the spread tight but the under offering the cleaner quantitative edge.
- **Kansas City Chiefs @ Seattle Seahawks (NFL):** Low total (42.5) signals defensive struggle; Chiefs' Mahomes efficiency gives them edge on moneyline despite road underdog status, while Seattle's home-field advantage at Lumen justifies the -2.5 spread cover.
- **Indiana Pacers @ Brooklyn Nets (NBA):** Pacers' top-5 pace and elite offensive rating should exploit Brooklyn's bottom-10 defensive efficiency, favoring Indiana to cover and win. The high-tempo matchup pushes the total over despite Brooklyn's slow pace, as Indiana's volume three-point shooting and transition game provide sufficient scoring floor.
- **Orlando Magic @ New York Knicks (NBA):** Knicks at MSG with a -7.5 spread project a ~72% win probability based on home-court advantage and Orlando's slow pace (top-5 in lowest possessions). The UNDER is favored as Orlando's top-3 slowest pace and New York's top-5 defensive rating both suppress scoring, making 224.5 an inflated total for this matchup.
- **Toronto Raptors @ Minnesota Timberwolves (NBA):** Target Center pace projects above league average; Raptors' defensive efficiency trends below median, creating elevated scoring environment. Minnesota's home-court edge in a near pick'em spread justifies a lean, while the 232.5 total aligns with both teams' offensive tempo profiles.
- **Detroit Pistons @ Philadelphia 76ers (NBA):** Philadelphia's elite offensive ceiling with Embiid/Maxey gives them a slight edge over Detroit's developing roster; the high total reflects both teams' pace and defensive vulnerabilities, favoring the over in what should be a relatively open-scoring affair.
- **Los Angeles Lakers @ Utah Jazz (NBA):** Lakers' veteran offensive efficiency and AD's interior dominance give them a clear edge over a young Jazz squad; Utah's pace-driven style and three-point volume support the over, but the spread is tight enough to favor the more proven side.
- **LA Clippers @ Oklahoma City Thunder (NBA):** Thunder's elite defensive rating and home-court advantage at Paycom Center project a comfortable cover against a Clippers team with roster instability and injury concerns. The 226.5 total is inflated for an early-season game where OKC's top-5 defense should suppress pace and scoring efficiency.
- **Memphis Grizzlies @ Sacramento Kings (NBA):** Both teams rank in the top-8 in pace this season, and Golden 1 Center historically inflates scoring. Memphis' elite transition defense and Ja Morant's playmaking give them a slight edge in controlling tempo, while Sacramento's home-court advantage keeps the spread tight. The 235 total is well-suited for two high-octane offenses, making the over the stronger side.
