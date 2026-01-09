# NFL Playoff Monte Carlo Simulation (2025 Season)

Monte Carlo simulation to estimate each NFL playoff team's probability of reaching and winning the Super Bowl.

## Quick Start

```bash
# Step 1: Build Elo ratings from 2025 regular season
python build_elo_2025.py

# Step 2: Run 10,000 playoff simulations
python simulate_playoffs_2025.py --sims 10000 --seed 42

# Step 3: Generate visualizations
python plot_results.py
```

## Scripts

### 1. `build_elo_2025.py`
Computes Elo ratings from regular season games.

**Usage:**
```bash
python build_elo_2025.py --season 2025 --k 30 --hfa 55 --out data/elo_2025.csv
```

**Parameters:**
- `--season`: NFL season year (default: 2025)
- `--k`: Elo K-factor (default: 30)
- `--hfa`: Home field advantage in Elo points (default: 55)
- `--out`: Output CSV file path (default: data/elo_2025.csv)

**Output:**
- `data/elo_2025.csv`: Final Elo ratings for all teams

---

### 2. `simulate_playoffs_2025.py`
Monte Carlo simulation of 2025 playoffs.

**Debug Mode (single simulation with bracket visualization):**
```bash
python simulate_playoffs_2025.py --sims 1 --seed 42
```

**Aggregation Mode (multiple simulations):**
```bash
python simulate_playoffs_2025.py --sims 10000 --seed 42
```

**Parameters:**
- `--elo_csv`: Path to Elo ratings CSV (default: data/elo_2025.csv)
- `--sims`: Number of simulations (default: 1)
- `--seed`: Random seed for reproducibility (optional)
- `--hfa`: Home field advantage in Elo points (default: 55)
- `--out`: Output CSV file path (default: results/playoff_odds_2025.csv)

**Output:**
- `results/playoff_odds_2025.csv`: Playoff probabilities for each team

---

### 3. `plot_results.py`
Generates visualizations from simulation results.

**Usage:**
```bash
python plot_results.py --in results/playoff_odds_2025.csv --out_dir results/plots/
```

**Parameters:**
- `--in`: Input CSV with playoff probabilities (default: results/playoff_odds_2025.csv)
- `--out_dir`: Output directory for plots (default: results/plots/)

**Outputs:**
- `superbowl_appearance_probs.png`: Probability of making Super Bowl
- `superbowl_win_probs.png`: Probability of winning Super Bowl
- `scatter_make_vs_win_sb.png`: Make SB vs Win SB scatter plot
- `all_rounds_progression.png`: Probabilities for all playoff rounds

---

## Playoff Format

### Wild Card Round
- Seed 1 receives a bye
- Matchups: 2 vs 7, 3 vs 6, 4 vs 5 (higher seed hosts)

### Divisional Round (with reseeding)
- Seed 1 hosts lowest remaining seed
- Other two teams play each other (higher seed hosts)

### Conference Championship
- Higher seed hosts

### Super Bowl
- Neutral site (no home-field advantage)

---

## 2025 Playoff Seeds

**AFC:**
1. Denver Broncos
2. New England Patriots
3. Jacksonville Jaguars
4. Pittsburgh Steelers
5. Houston Texans
6. Buffalo Bills
7. Los Angeles Chargers

**NFC:**
1. Seattle Seahawks
2. Chicago Bears
3. Philadelphia Eagles
4. Carolina Panthers
5. Los Angeles Rams
6. San Francisco 49ers
7. Green Bay Packers

---

## Results (10,000 simulations)

Run the 2025 simulation to populate `results/playoff_odds_2025.csv`.

---

## Methodology

### Elo Ratings
- **Initialization:** All teams start at Elo = 1500
- **K-factor:** 30
- **Home-field advantage:** 55 Elo points
- **Scope:** Regular season games only (playoffs do not update Elo)

### Win Probability
```
diff = (elo_home + HFA) - elo_away
P(home wins) = 1 / (1 + 10^(-diff/400))
```

### Monte Carlo Simulation
For each game:
1. Compute win probability
2. Draw random number u ~ Uniform(0, 1)
3. If u < p_home_win, home team advances
4. Otherwise, away team advances

Aggregate results across all simulations to estimate probabilities.

---

## Dependencies

```bash
pip install pandas numpy matplotlib nflreadpy
```
