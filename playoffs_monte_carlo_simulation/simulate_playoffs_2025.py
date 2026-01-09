#!/usr/bin/env python3
"""
simulate_playoffs_2025.py

Monte Carlo simulation of 2025 NFL playoffs using frozen Elo ratings.

Supports two modes:
    --sims 1   : Debug mode with bracket visualization
    --sims > 1 : Aggregation mode with probability estimates

Usage:
    python simulate_playoffs_2025.py --elo_csv data/elo_2025.csv --sims 1 --seed 42
    python simulate_playoffs_2025.py --elo_csv data/elo_2025.csv --sims 10000 --out results/playoff_odds_2025.csv
"""

import argparse
import pandas as pd
import numpy as np
from collections import defaultdict

# ============================================================================
# PLAYOFF BRACKET STRUCTURE (HARDCODED)
# ============================================================================

PLAYOFF_SEEDS = {
    "AFC": {
        1: "DEN",
        2: "NE",
        3: "JAX",
        4: "PIT",
        5: "HOU",
        6: "BUF",
        7: "LAC"
    },
    "NFC": {
        1: "SEA",
        2: "CHI",
        3: "PHI",
        4: "CAR",
        5: "LA",  # LA Rams (nflreadpy uses "LA" not "LAR")
        6: "SF",
        7: "GB"
    }
}


# ============================================================================
# STEP 1: Parse command-line arguments
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Simulate 2025 NFL playoffs using Monte Carlo method'
    )
    parser.add_argument('--elo_csv', type=str, default='data/elo_2025.csv',
                        help='Path to Elo ratings CSV (default: data/elo_2025.csv)')
    parser.add_argument('--sims', type=int, default=1,
                        help='Number of simulations (default: 1 for debug mode)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--hfa', type=int, default=55,
                        help='Home field advantage in Elo points (default: 55)')
    parser.add_argument('--out', type=str, default='results/playoff_odds_2025.csv',
                        help='Output CSV file path (default: results/playoff_odds_2025.csv)')
    return parser.parse_args()


# ============================================================================
# STEP 2: Load Elo ratings
# ============================================================================

def load_elo_ratings(elo_csv_path):
    """Load frozen Elo ratings from CSV."""
    print(f"Loading Elo ratings from {elo_csv_path}...")
    elo_df = pd.read_csv(elo_csv_path)
    elo_dict = dict(zip(elo_df['team'], elo_df['final_elo']))
    print(f"✓ Loaded Elo ratings for {len(elo_dict)} teams")
    return elo_dict


# ============================================================================
# STEP 3: Compute win probability from Elo
# ============================================================================

def compute_win_probability(elo_home, elo_away, hfa, is_neutral=False):
    """
    Compute home team's win probability.

    Args:
        elo_home: Home team's Elo rating
        elo_away: Away team's Elo rating
        hfa: Home field advantage in Elo points
        is_neutral: If True, ignore HFA (Super Bowl)

    Returns:
        Probability that home team wins (0 to 1)
    """
    if is_neutral:
        diff = elo_home - elo_away
    else:
        diff = (elo_home + hfa) - elo_away

    p_home_win = 1 / (1 + 10 ** (-diff / 400))
    return p_home_win


# ============================================================================
# STEP 4: Simulate a single game
# ============================================================================

def simulate_game(team_home, team_away, elo_dict, hfa, is_neutral=False):
    """
    Simulate a single playoff game.

    Returns:
        winner: Team abbreviation of the winner
        p_home_win: Probability that home team won (for debugging)
    """
    elo_home = elo_dict[team_home]
    elo_away = elo_dict[team_away]

    p_home_win = compute_win_probability(elo_home, elo_away, hfa, is_neutral)

    # Monte Carlo draw
    u = np.random.random()
    if u < p_home_win:
        winner = team_home
    else:
        winner = team_away

    return winner, p_home_win


# ============================================================================
# STEP 5: Simulate Wild Card Round
# ============================================================================

def simulate_wild_card(conference, seeds, elo_dict, hfa, debug=False):
    """
    Simulate Wild Card round for one conference.

    Matchups:
        2 hosts 7
        3 hosts 6
        4 hosts 5

    Seed 1 receives a bye.

    Returns:
        List of winners (including seed 1)
    """
    if debug:
        print(f"\n--- {conference} WILD CARD ROUND ---")

    winners = [seeds[1]]  # Seed 1 gets a bye

    matchups = [
        (2, 7),
        (3, 6),
        (4, 5)
    ]

    for seed_home, seed_away in matchups:
        team_home = seeds[seed_home]
        team_away = seeds[seed_away]

        winner, p_home_win = simulate_game(team_home, team_away, elo_dict, hfa)
        winners.append(winner)

        if debug:
            print(f"  ({seed_home}) {team_home} vs ({seed_away}) {team_away}: "
                  f"P({team_home} wins) = {p_home_win:.3f} → Winner: {winner}")

    return winners


# ============================================================================
# STEP 6: Simulate Divisional Round (with reseeding)
# ============================================================================

def simulate_divisional(conference, wild_card_winners, seeds, elo_dict, hfa, debug=False):
    """
    Simulate Divisional round with reseeding.

    Logic:
        - Seed 1 hosts the lowest remaining seed
        - The other two teams play each other (higher seed hosts)

    Returns:
        List of 2 winners
    """
    if debug:
        print(f"\n--- {conference} DIVISIONAL ROUND ---")

    # Map teams back to their original seeds
    team_to_seed = {team: seed for seed, team in seeds.items()}
    remaining_seeds = sorted([team_to_seed[team] for team in wild_card_winners])

    # Seed 1 hosts lowest remaining seed
    seed_1_team = seeds[1]
    lowest_seed = max(remaining_seeds)
    lowest_team = seeds[lowest_seed]

    # Other two teams play each other
    other_seeds = [s for s in remaining_seeds if s != 1 and s != lowest_seed]
    higher_seed = min(other_seeds)
    lower_seed = max(other_seeds)

    # Game 1: Seed 1 hosts lowest seed
    winner_1, p_win_1 = simulate_game(seed_1_team, lowest_team, elo_dict, hfa)

    if debug:
        print(f"  (1) {seed_1_team} vs ({lowest_seed}) {lowest_team}: "
              f"P({seed_1_team} wins) = {p_win_1:.3f} → Winner: {winner_1}")

    # Game 2: Higher seed hosts lower seed
    team_higher = seeds[higher_seed]
    team_lower = seeds[lower_seed]
    winner_2, p_win_2 = simulate_game(team_higher, team_lower, elo_dict, hfa)

    if debug:
        print(f"  ({higher_seed}) {team_higher} vs ({lower_seed}) {team_lower}: "
              f"P({team_higher} wins) = {p_win_2:.3f} → Winner: {winner_2}")

    return [winner_1, winner_2]


# ============================================================================
# STEP 7: Simulate Conference Championship
# ============================================================================

def simulate_conference_championship(conference, divisional_winners, seeds, elo_dict, hfa, debug=False):
    """
    Simulate Conference Championship.

    Higher seed hosts.

    Returns:
        Conference champion (team abbreviation)
    """
    if debug:
        print(f"\n--- {conference} CONFERENCE CHAMPIONSHIP ---")

    # Map teams to seeds
    team_to_seed = {team: seed for seed, team in seeds.items()}
    remaining_seeds = sorted([team_to_seed[team] for team in divisional_winners])

    higher_seed = min(remaining_seeds)
    lower_seed = max(remaining_seeds)

    team_home = seeds[higher_seed]
    team_away = seeds[lower_seed]

    winner, p_home_win = simulate_game(team_home, team_away, elo_dict, hfa)

    if debug:
        print(f"  ({higher_seed}) {team_home} vs ({lower_seed}) {team_away}: "
              f"P({team_home} wins) = {p_home_win:.3f} → Winner: {winner}")

    return winner


# ============================================================================
# STEP 8: Simulate Super Bowl
# ============================================================================

def simulate_super_bowl(afc_champ, nfc_champ, elo_dict, hfa, debug=False):
    """
    Simulate Super Bowl (neutral site - no HFA).

    For display purposes, we'll list AFC team first (as "home").

    Returns:
        Super Bowl champion
    """
    if debug:
        print(f"\n--- SUPER BOWL (Neutral Site) ---")

    winner, p_afc_win = simulate_game(afc_champ, nfc_champ, elo_dict, hfa, is_neutral=True)

    if debug:
        print(f"  {afc_champ} (AFC) vs {nfc_champ} (NFC): "
              f"P({afc_champ} wins) = {p_afc_win:.3f} → Winner: {winner}")

    return winner


# ============================================================================
# STEP 9: Simulate one full playoff bracket
# ============================================================================

def simulate_one_bracket(elo_dict, hfa, debug=False):
    """
    Simulate one complete playoff bracket.

    Returns:
        Dictionary tracking which teams reached each round
    """
    results = {
        'divisional': [],
        'conf_champ': [],
        'super_bowl': [],
        'champion': None
    }

    # AFC Playoffs
    afc_seeds = PLAYOFF_SEEDS["AFC"]
    afc_wc_winners = simulate_wild_card("AFC", afc_seeds, elo_dict, hfa, debug)
    results['divisional'].extend(afc_wc_winners)

    afc_div_winners = simulate_divisional("AFC", afc_wc_winners, afc_seeds, elo_dict, hfa, debug)
    results['conf_champ'].extend(afc_div_winners)

    afc_champ = simulate_conference_championship("AFC", afc_div_winners, afc_seeds, elo_dict, hfa, debug)
    results['super_bowl'].append(afc_champ)

    # NFC Playoffs
    nfc_seeds = PLAYOFF_SEEDS["NFC"]
    nfc_wc_winners = simulate_wild_card("NFC", nfc_seeds, elo_dict, hfa, debug)
    results['divisional'].extend(nfc_wc_winners)

    nfc_div_winners = simulate_divisional("NFC", nfc_wc_winners, nfc_seeds, elo_dict, hfa, debug)
    results['conf_champ'].extend(nfc_div_winners)

    nfc_champ = simulate_conference_championship("NFC", nfc_div_winners, nfc_seeds, elo_dict, hfa, debug)
    results['super_bowl'].append(nfc_champ)

    # Super Bowl
    champion = simulate_super_bowl(afc_champ, nfc_champ, elo_dict, hfa, debug)
    results['champion'] = champion

    return results


# ============================================================================
# STEP 10: Run Monte Carlo simulations
# ============================================================================

def run_simulations(elo_dict, hfa, num_sims, debug=False):
    """
    Run multiple playoff simulations and aggregate results.

    Returns:
        DataFrame with probabilities for each team
    """
    print(f"\nRunning {num_sims} playoff simulation(s)...")

    # Track counts for each team
    counts = defaultdict(lambda: {
        'divisional': 0,
        'conf_champ': 0,
        'super_bowl': 0,
        'champion': 0
    })

    for sim in range(num_sims):
        if num_sims > 1 and (sim + 1) % 1000 == 0:
            print(f"  Completed {sim + 1}/{num_sims} simulations...")

        # Run one bracket
        results = simulate_one_bracket(elo_dict, hfa, debug=(debug and sim == 0))

        # Update counts
        for team in results['divisional']:
            counts[team]['divisional'] += 1

        for team in results['conf_champ']:
            counts[team]['conf_champ'] += 1

        for team in results['super_bowl']:
            counts[team]['super_bowl'] += 1

        if results['champion']:
            counts[results['champion']]['champion'] += 1

    # Convert counts to probabilities
    prob_data = []
    for team, team_counts in counts.items():
        prob_data.append({
            'team': team,
            'pct_make_divisional': team_counts['divisional'] / num_sims,
            'pct_make_conf_champ': team_counts['conf_champ'] / num_sims,
            'pct_make_superbowl': team_counts['super_bowl'] / num_sims,
            'pct_win_superbowl': team_counts['champion'] / num_sims
        })

    prob_df = pd.DataFrame(prob_data)
    prob_df = prob_df.sort_values('pct_win_superbowl', ascending=False).reset_index(drop=True)

    print(f"✓ Simulations complete")
    return prob_df


# ============================================================================
# STEP 11: Save results
# ============================================================================

def save_results(prob_df, output_path):
    """Save probability results to CSV."""
    print(f"\nSaving results to {output_path}...")
    prob_df.to_csv(output_path, index=False)
    print(f"✓ Results saved")

    print("\n📊 Playoff Probabilities (Top 10):")
    print(prob_df.head(10).to_string(index=False))


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    args = parse_args()

    # Set random seed if provided
    if args.seed is not None:
        np.random.seed(args.seed)
        print(f"Random seed set to {args.seed}")

    print("=" * 80)
    print("NFL PLAYOFF MONTE CARLO SIMULATION - 2025 SEASON")
    print("=" * 80)

    # Load Elo ratings
    elo_dict = load_elo_ratings(args.elo_csv)

    # Debug mode (--sims 1)
    debug_mode = (args.sims == 1)

    if debug_mode:
        print("\n⚠️  DEBUG MODE: Running single simulation with bracket visualization")

    # Run simulations
    prob_df = run_simulations(elo_dict, args.hfa, args.sims, debug=debug_mode)

    # Save results (only if multiple sims)
    if args.sims > 1:
        save_results(prob_df, args.out)
    else:
        print("\n✓ Single simulation complete (debug mode)")

    print("\n" + "=" * 80)
    print("✓ PLAYOFF SIMULATION COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
