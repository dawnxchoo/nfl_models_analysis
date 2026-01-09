#!/usr/bin/env python3
"""
build_elo_2025.py

Computes final Elo ratings for all NFL teams entering the 2025 playoffs
using regular season games only.

Usage:
    python build_elo_2025.py --season 2025 --k 30 --hfa 55 --out data/elo_2025.csv
"""

import argparse
import pandas as pd
import nflreadpy

# ============================================================================
# STEP 1: Parse command-line arguments
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Build Elo ratings for NFL teams from regular season data'
    )
    parser.add_argument('--season', type=int, default=2025,
                        help='NFL season year (default: 2025)')
    parser.add_argument('--k', type=int, default=30,
                        help='Elo K-factor (default: 30)')
    parser.add_argument('--hfa', type=int, default=55,
                        help='Home field advantage in Elo points (default: 55)')
    parser.add_argument('--out', type=str, default='data/elo_2025.csv',
                        help='Output CSV file path (default: data/elo_2025.csv)')
    return parser.parse_args()


# ============================================================================
# STEP 2: Load schedule data from nflreadpy
# ============================================================================

def load_schedule(season):
    """Load NFL schedule for given season using nflreadpy."""
    print(f"Loading {season} NFL schedule from nflreadpy...")
    df = nflreadpy.load_schedules([season])
    # Convert to pandas DataFrame
    df = df.to_pandas()
    print(f"✓ Loaded {len(df)} total games")
    return df


# ============================================================================
# STEP 3: Filter to regular season games only
# ============================================================================

def filter_regular_season(df):
    """Filter schedule to regular season games only."""
    print("\nFiltering to regular season games...")

    # Regular season games have game_type == 'REG'
    regular_season = df[df['game_type'] == 'REG'].copy()

    # Remove games that haven't been played yet (no result)
    regular_season = regular_season[regular_season['result'].notna()].copy()

    print(f"✓ {len(regular_season)} regular season games completed")
    return regular_season


# ============================================================================
# STEP 4: Sort games chronologically
# ============================================================================

def sort_games_chronologically(df):
    """Sort games by gameday (chronological order)."""
    print("\nSorting games chronologically...")
    df_sorted = df.sort_values('gameday').reset_index(drop=True)
    print(f"✓ Games sorted from {df_sorted['gameday'].min()} to {df_sorted['gameday'].max()}")
    return df_sorted


# ============================================================================
# STEP 5: Initialize Elo ratings
# ============================================================================

def initialize_elo_ratings(df, initial_elo=1500):
    """Initialize all teams at starting Elo rating."""
    print(f"\nInitializing Elo ratings at {initial_elo}...")

    # Get all unique teams (both home and away)
    home_teams = df['home_team'].unique()
    away_teams = df['away_team'].unique()
    all_teams = set(list(home_teams) + list(away_teams))

    # Initialize dictionary
    elo_ratings = {team: initial_elo for team in all_teams}

    print(f"✓ Initialized {len(elo_ratings)} teams at Elo {initial_elo}")
    return elo_ratings


# ============================================================================
# STEP 6: Compute Elo win probability
# ============================================================================

def compute_win_probability(elo_home, elo_away, hfa):
    """
    Compute home team's win probability from Elo ratings.

    Formula:
        diff = (elo_home + HFA) - elo_away
        p_home = 1 / (1 + 10^(-diff/400))
    """
    diff = (elo_home + hfa) - elo_away
    p_home = 1 / (1 + 10 ** (-diff / 400))
    return p_home


# ============================================================================
# STEP 7: Update Elo ratings after each game
# ============================================================================

def update_elo_ratings(elo_ratings, df, k_factor, hfa):
    """
    Process all games chronologically and update Elo ratings.

    Returns:
        Updated elo_ratings dictionary
        DataFrame with game-by-game Elo tracking
    """
    print(f"\nUpdating Elo ratings (K={k_factor}, HFA={hfa})...")

    game_log = []

    for idx, row in df.iterrows():
        home_team = row['home_team']
        away_team = row['away_team']
        home_score = row['home_score']
        away_score = row['away_score']

        # Get current Elo ratings
        elo_home = elo_ratings[home_team]
        elo_away = elo_ratings[away_team]

        # Compute expected win probability
        p_home_win = compute_win_probability(elo_home, elo_away, hfa)

        # Determine actual outcome (1 if home wins, 0 otherwise)
        actual_home = 1 if home_score > away_score else 0

        # Compute Elo change
        delta = k_factor * (actual_home - p_home_win)

        # Update ratings
        new_elo_home = elo_home + delta
        new_elo_away = elo_away - delta

        # Log this game
        game_log.append({
            'gameday': row['gameday'],
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'elo_home_before': elo_home,
            'elo_away_before': elo_away,
            'p_home_win': p_home_win,
            'actual_home_win': actual_home,
            'delta': delta,
            'elo_home_after': new_elo_home,
            'elo_away_after': new_elo_away
        })

        # Apply updates
        elo_ratings[home_team] = new_elo_home
        elo_ratings[away_team] = new_elo_away

    print(f"✓ Processed {len(game_log)} games")

    return elo_ratings, pd.DataFrame(game_log)


# ============================================================================
# STEP 8: Save final Elo ratings
# ============================================================================

def save_elo_ratings(elo_ratings, output_path):
    """Save final Elo ratings to CSV."""
    print(f"\nSaving Elo ratings to {output_path}...")

    # Convert to DataFrame
    elo_df = pd.DataFrame([
        {'team': team, 'final_elo': elo}
        for team, elo in sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
    ])

    # Save to CSV
    elo_df.to_csv(output_path, index=False)

    print(f"✓ Saved {len(elo_df)} team Elo ratings")
    print("\n📊 Top 5 teams by Elo:")
    print(elo_df.head(5).to_string(index=False))
    print("\n📊 Bottom 5 teams by Elo:")
    print(elo_df.tail(5).to_string(index=False))

    return elo_df


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    args = parse_args()

    print("=" * 80)
    print("NFL ELO RATING BUILDER - 2025 REGULAR SEASON")
    print("=" * 80)

    # Load schedule
    schedule_df = load_schedule(args.season)

    # Filter to regular season
    regular_season_df = filter_regular_season(schedule_df)

    # Sort chronologically
    sorted_games = sort_games_chronologically(regular_season_df)

    # Initialize Elo ratings
    elo_ratings = initialize_elo_ratings(sorted_games)

    # Update Elo ratings game by game
    final_elo_ratings, game_log_df = update_elo_ratings(
        elo_ratings, sorted_games, args.k, args.hfa
    )

    # Save final ratings
    elo_df = save_elo_ratings(final_elo_ratings, args.out)

    print("\n" + "=" * 80)
    print("✓ ELO RATING COMPUTATION COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
