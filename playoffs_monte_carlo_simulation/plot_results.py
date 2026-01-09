#!/usr/bin/env python3
"""
plot_results.py

Visualizes Monte Carlo playoff simulation results.

Generates:
    - Bar chart: Teams sorted by probability of making Super Bowl
    - Bar chart: Teams sorted by probability of winning Super Bowl
    - Scatter plot: Make SB vs Win SB probabilities

Usage:
    python plot_results.py --in results/playoff_odds_2025.csv --out_dir results/plots/
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os

# ============================================================================
# STEP 1: Parse command-line arguments
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Visualize playoff simulation results'
    )
    parser.add_argument('--in', dest='input_csv', type=str,
                        default='results/playoff_odds_2025.csv',
                        help='Input CSV with playoff probabilities (default: results/playoff_odds_2025.csv)')
    parser.add_argument('--out_dir', type=str, default='results/plots/',
                        help='Output directory for plots (default: results/plots/)')
    return parser.parse_args()


# ============================================================================
# STEP 2: Load playoff probability data
# ============================================================================

def load_playoff_data(csv_path):
    """Load playoff probability results from CSV."""
    print(f"Loading playoff data from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded data for {len(df)} teams")
    return df


# ============================================================================
# STEP 3: Create output directory if needed
# ============================================================================

def ensure_output_dir(out_dir):
    """Create output directory if it doesn't exist."""
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        print(f"✓ Created output directory: {out_dir}")
    else:
        print(f"✓ Output directory exists: {out_dir}")


# ============================================================================
# STEP 4: Plot Super Bowl appearance probabilities
# ============================================================================

def plot_superbowl_appearance(df, out_dir):
    """
    Bar chart: Teams sorted by probability of making Super Bowl.
    """
    print("\nGenerating Super Bowl appearance probability chart...")

    # Sort by pct_make_superbowl descending
    df_sorted = df.sort_values('pct_make_superbowl', ascending=False).reset_index(drop=True)

    # Create figure
    plt.figure(figsize=(12, 6))

    # Bar chart
    plt.bar(df_sorted['team'], df_sorted['pct_make_superbowl'] * 100,
            color='steelblue', edgecolor='black')

    # Labels and title
    plt.xlabel('Team', fontsize=12, fontweight='bold')
    plt.ylabel('Probability (%)', fontsize=12, fontweight='bold')
    plt.title('Probability of Making Super Bowl - 2025 NFL Playoffs',
              fontsize=14, fontweight='bold')

    # Grid and layout
    plt.grid(alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save
    output_path = os.path.join(out_dir, 'superbowl_appearance_probs.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


# ============================================================================
# STEP 5: Plot Super Bowl win probabilities
# ============================================================================

def plot_superbowl_win(df, out_dir):
    """
    Bar chart: Teams sorted by probability of winning Super Bowl.
    """
    print("\nGenerating Super Bowl win probability chart...")

    # Sort by pct_win_superbowl descending
    df_sorted = df.sort_values('pct_win_superbowl', ascending=False).reset_index(drop=True)

    # Create figure
    plt.figure(figsize=(12, 6))

    # Bar chart
    plt.bar(df_sorted['team'], df_sorted['pct_win_superbowl'] * 100,
            color='darkgreen', edgecolor='black')

    # Labels and title
    plt.xlabel('Team', fontsize=12, fontweight='bold')
    plt.ylabel('Probability (%)', fontsize=12, fontweight='bold')
    plt.title('Probability of Winning Super Bowl - 2025 NFL Playoffs',
              fontsize=14, fontweight='bold')

    # Grid and layout
    plt.grid(alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save
    output_path = os.path.join(out_dir, 'superbowl_win_probs.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


# ============================================================================
# STEP 6: Plot scatter: Make SB vs Win SB
# ============================================================================

def plot_scatter_make_vs_win(df, out_dir):
    """
    Scatter plot: Probability of making SB vs winning SB.
    """
    print("\nGenerating scatter plot (Make SB vs Win SB)...")

    # Create figure
    plt.figure(figsize=(10, 8))

    # Scatter plot
    plt.scatter(df['pct_make_superbowl'] * 100,
                df['pct_win_superbowl'] * 100,
                s=100, alpha=0.7, color='coral', edgecolor='black')

    # Annotate each point with team name
    for idx, row in df.iterrows():
        plt.annotate(row['team'],
                     xy=(row['pct_make_superbowl'] * 100, row['pct_win_superbowl'] * 100),
                     xytext=(5, 5), textcoords='offset points',
                     fontsize=9, alpha=0.8)

    # Labels and title
    plt.xlabel('Probability of Making Super Bowl (%)', fontsize=12, fontweight='bold')
    plt.ylabel('Probability of Winning Super Bowl (%)', fontsize=12, fontweight='bold')
    plt.title('Super Bowl Appearance vs Win Probability - 2025 NFL Playoffs',
              fontsize=14, fontweight='bold')

    # Grid and layout
    plt.grid(alpha=0.3)
    plt.tight_layout()

    # Save
    output_path = os.path.join(out_dir, 'scatter_make_vs_win_sb.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


# ============================================================================
# STEP 7: Plot all round probabilities (stacked comparison)
# ============================================================================

def plot_all_rounds(df, out_dir):
    """
    Stacked bar chart showing progression through playoff rounds.
    """
    print("\nGenerating all-rounds progression chart...")

    # Sort by pct_win_superbowl descending
    df_sorted = df.sort_values('pct_win_superbowl', ascending=False).reset_index(drop=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 7))

    # Define bar positions
    x = range(len(df_sorted))
    width = 0.2

    # Plot each round
    ax.bar([i - 1.5*width for i in x], df_sorted['pct_make_divisional'] * 100,
           width, label='Divisional Round', color='lightblue', edgecolor='black')
    ax.bar([i - 0.5*width for i in x], df_sorted['pct_make_conf_champ'] * 100,
           width, label='Conf. Championship', color='skyblue', edgecolor='black')
    ax.bar([i + 0.5*width for i in x], df_sorted['pct_make_superbowl'] * 100,
           width, label='Super Bowl', color='steelblue', edgecolor='black')
    ax.bar([i + 1.5*width for i in x], df_sorted['pct_win_superbowl'] * 100,
           width, label='Win Super Bowl', color='darkgreen', edgecolor='black')

    # Labels and title
    ax.set_xlabel('Team', fontsize=12, fontweight='bold')
    ax.set_ylabel('Probability (%)', fontsize=12, fontweight='bold')
    ax.set_title('Playoff Progression Probabilities - 2025 NFL Playoffs',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(df_sorted['team'], rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3, axis='y')

    plt.tight_layout()

    # Save
    output_path = os.path.join(out_dir, 'all_rounds_progression.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    args = parse_args()

    print("=" * 80)
    print("NFL PLAYOFF SIMULATION RESULTS - VISUALIZATION")
    print("=" * 80)

    # Load data
    df = load_playoff_data(args.input_csv)

    # Ensure output directory exists
    ensure_output_dir(args.out_dir)

    # Generate plots
    plot_superbowl_appearance(df, args.out_dir)
    plot_superbowl_win(df, args.out_dir)
    plot_scatter_make_vs_win(df, args.out_dir)
    plot_all_rounds(df, args.out_dir)

    print("\n" + "=" * 80)
    print("✓ ALL VISUALIZATIONS COMPLETE")
    print("=" * 80)
    print(f"\nPlots saved to: {args.out_dir}")


if __name__ == '__main__':
    main()
