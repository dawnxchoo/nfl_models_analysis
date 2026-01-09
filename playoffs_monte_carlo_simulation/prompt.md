

# Monte Carlo NFL Playoff Simulation (2025 Season)

## 1. Goal

Build a Monte Carlo simulation to estimate each NFL playoff team’s probability of:

* Reaching the Super Bowl
* Winning the Super Bowl

The simulation represents **pre-playoff probabilities**, using information available **at the start of the 2025 postseason**.

---

## 2. Season Context

* NFL **2025 season**
* Elo ratings are derived from **regular season games only**
* Playoff results are simulated; they do **not** update team strength

---

## 3. Data Source

Use the `nflreadpy` Python library.

* Load schedules via:

  ```python
  nflreadpy.load_schedules([2025])
  ```
* Use **regular season games only** to compute Elo ratings
* Postseason games are **not** used to update Elo

---

## 4. Playoff Teams & Seeds

Lower seed number = better seed.

```json
{
  "AFC": {
    "1": "Broncos",
    "2": "Patriots",
    "3": "Jaguars",
    "4": "Steelers",
    "5": "Texans",
    "6": "Bills",
    "7": "Chargers"
  },
  "NFC": {
    "1": "Seahawks",
    "2": "Bears",
    "3": "Eagles",
    "4": "Panthers",
    "5": "Rams",
    "6": "49ers",
    "7": "Packers"
  }
}
```

These seeds are hardcoded inputs. Do **not** attempt to derive playoff seeding or tiebreakers programmatically.

---

## 5. Playoff Format Rules

Apply separately for AFC and NFC.

### Wild Card Round

* Seed **1** receives a bye
* Matchups:

  * 2 hosts 7
  * 3 hosts 6
  * 4 hosts 5

### Divisional Round (Reseeding)

* Seed 1 hosts the **lowest remaining seed**
* The other two remaining teams play each other
* Higher seed hosts

### Conference Championship

* Higher seed hosts

### Super Bowl

* Neutral site
* **No home-field advantage**

---

## 6. Elo Ratings

### Initialization

* All teams start at **Elo = 1500**

### Parameters

* **K-factor:** 30
* **Home-field advantage (HFA):** 55 Elo points

### Scope

* Elo ratings are computed using **regular season games only**
* Elo ratings are **frozen once the postseason begins**

---

## 7. Elo Update Procedure (Regular Season Only)

Process regular season games in **chronological order**.

For each game:

1. Compute Elo difference:

   ```
   diff = (elo_home + HFA) − elo_away
   ```

2. Convert to expected home win probability:

   ```
   p_home = 1 / (1 + 10 ** (-diff / 400))
   ```

3. Define actual outcome:

   * `actual_home = 1` if home team wins
   * `actual_home = 0` otherwise

4. Update Elo ratings:

   ```
   delta = K * (actual_home − p_home)
   elo_home += delta
   elo_away -= delta
   ```

Properties:

* Winner and loser gain/lose equal magnitude
* Unexpected outcomes produce larger updates

---

## 8. Win Probability from Elo (Playoffs)

For any playoff game:

1. Compute:

   ```
   diff = (elo_home + HFA) − elo_away
   ```

   * **Exception:** Super Bowl uses no HFA

2. Convert to probability:
   [
   P(\text{home wins}) = \frac{1}{1 + 10^{-diff/400}}
   ]

Properties:

* `P(home wins) + P(away wins) = 1`
* Compute **only one probability per game** (home perspective)

---

## 9. Monte Carlo Game Resolution

For each simulated game:

1. Compute `p_home_win`
2. Draw `u ~ Uniform(0, 1)`
3. If `u < p_home_win`, home team wins
4. Else, away team wins
5. Advance winner in the bracket

---

## 10. Single-Simulation Debug Mode (`--sims 1`)

When running the simulation with **one iteration**:

* Simulate exactly **one full playoff bracket**
* Output a **bracket tree visualization** that includes:

  * Round structure (Wild Card → Divisional → Conference Championship → Super Bowl)
  * Matchups with home vs away clearly labeled
  * Win probability (`p_home_win`) for each game
  * Winners advancing between rounds
  * Reseeding behavior explicitly visible

Visualization format:

* Mermaid diagram **or**
* Clean ASCII / text-based tree

Goal:

* Debug bracket logic and reseeding
* Verify probabilities and hosts
* Aesthetics are secondary to correctness

---

## 11. Monte Carlo Aggregation Mode (`--sims > 1`)

When running multiple simulations:

* Aggregate outcomes across all runs
* Track per-team counts for:

  * Making Divisional Round
  * Making Conference Championship
  * Making Super Bowl
  * Winning Super Bowl

Convert counts to probabilities.

---

## 12. Deliverables

### Script 1: `build_elo_2025.py`

**Purpose**

* Load 2025 regular season data
* Compute final Elo ratings entering playoffs

**Inputs**

* `--season 2025` (default)
* `--k 30`
* `--hfa 55`
* `--out data/elo_2025.csv`

**Outputs**

* `data/elo_2025.csv` (team, final_elo)
* Optional cached schedule CSV for debugging

---

### Script 2: `simulate_playoffs_2025.py`

**Purpose**

* Run playoff simulation using frozen Elo ratings
* Support both debug and aggregation modes

**Inputs**

* `--elo_csv data/elo_2025.csv`
* `--sims` (default 1)
* `--seed` (random seed for reproducibility)
* `--hfa 55`
* `--out results/playoff_odds_2025.csv`

**Outputs**

* If `--sims 1`:

  * `results/bracket_run_2025.txt` or `.md`
* If `--sims > 1`:

  * `results/playoff_odds_2025.csv` with probabilities

---

### Script 3: `plot_results.py`

**Purpose**

* Visualize aggregated simulation results

**Inputs**

* `--in results/playoff_odds_2025.csv`
* `--out_dir results/plots/`

**Outputs**

* Bar chart: teams sorted by `pct_make_superbowl`
* Bar chart: teams sorted by `pct_win_superbowl`
* (Optional) scatter: make SB vs win SB

---

## 13. Modeling Assumptions

* No ties
* No injuries or roster changes
* Team strength does not change during playoffs
* Elo represents true underlying team strength at playoff start

---

## 14. Intentional Non-Goals

* No play-by-play data
* No live in-season updating
* No injury modeling
* No betting market calibration
* No automatic seeding derivation

---

## Completeness Check (sanity)

✔ Data source defined
✔ Elo fully specified (init, K, HFA, update rule)
✔ Playoff format unambiguous (bye, reseeding, hosting)
✔ Monte Carlo mechanics explicit
✔ Debug vs aggregate behavior separated
✔ Deliverables and responsibilities clear
✔ No conflicting assumptions

This spec is **complete and implementable** as written.

When you’re ready, next steps could be:

* turning this into a **single Claude Code “generate the scripts” prompt**, or
* writing a **gold-standard example of what a correct `--sims 1` bracket output should look like** so you know instantly if something’s wrong.
