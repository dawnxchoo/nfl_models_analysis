# Replit Prompt: Interactive Animated NFL Playoff Monte Carlo Simulator

## Project Overview

Create an interactive web application that visualizes NFL playoff bracket simulations in real-time with smooth animations. Users can watch individual playoff brackets being simulated, see winners advance through rounds, and track which teams win the Super Bowl across multiple Monte Carlo runs.

## Core Features

### 1. Input Controls (Top of Page)
- **Number of simulations** input field (default: 10)
- **Start/Run Simulation** button
- Clean, simple UI with modern styling

### 2. Animated Playoff Bracket Display

#### Layout Structure
- **Split screen**: AFC bracket on LEFT | NFC bracket on RIGHT
- **Super Bowl section**: Center bottom where conference champions meet
- **Scoreboard**: Right sidebar or bottom panel showing all 14 playoff teams

#### Bracket Design - IMPORTANT: Dynamic/Adaptive Format
This is **NOT a traditional fixed bracket**. The NFL uses **reseeding** in the Divisional Round, so matchups are calculated dynamically based on Wild Card results.

**Round structure:**
- **Wild Card Round**: 3 games per conference (seeds 2v7, 3v6, 4v5; seed 1 gets bye)
- **Divisional Round** (with reseeding):
  - Seed 1 hosts the LOWEST remaining seed
  - Other two winners play each other (higher seed hosts)
- **Conference Championship**: Higher seed hosts
- **Super Bowl**: Neutral site (center of screen)

### 3. Animation Sequence (Per Game)

**Timing**: 1 second per game

**Visual flow:**
1. **Highlight current matchup** - animate a glowing border or pulsing effect around the game box
2. **Show both team names** in the matchup box with their seeds (e.g., "(1) DEN vs (6) BUF")
3. **Determine winner** based on Elo probability
4. **Winner animation**:
   - Brighten/bold the winning team name
   - Fade out or gray out the losing team name
5. **Advance winner** - smooth CSS transition/slide animation moving winning team to next round's position

**Special transitions:**
- **Between Wild Card and Divisional**: Show "Reseeding Divisional Round..." message for 0.5 seconds
- **Between rounds**: Brief pause (0.3s) to let users see the bracket state

### 4. Super Bowl Finale

When Super Bowl winner is determined:
1. **Dramatic animation**: Winning team name "drops" from Super Bowl box to bottom of screen with smooth fall animation
2. **Play victory sound effect** (short, celebratory - single play, not looping)
3. **Confetti or sparkle effect** (optional but nice)
4. **Update scoreboard** immediately

### 5. Scoreboard/Tally Display

**Location**: Right sidebar or bottom panel

**Contents**:
- List all 14 playoff teams with their Super Bowl win counts
- Format: "SEA: 3 wins | DEN: 2 wins | PHI: 1 win" etc.

**Behavior**:
- **Auto-resort after each simulation** - highest win count always at top
- **Highlight/flash** the team that just won (brief 0.5s glow effect)
- **Smooth reordering animation** when teams change positions

### 6. Between Simulations

**3-second countdown timer** displayed prominently:
```
Starting next simulation in 3...
Starting next simulation in 2...
Starting next simulation in 1...
```

Then immediately start the next bracket simulation.

## Technical Implementation

### Technology Stack
- **HTML/CSS/JavaScript** (vanilla or React - your choice)
- **CSS animations** for smooth transitions
- **Web Audio API** for sound effect (or simple `<audio>` tag)

### Data Files Needed

You will receive these files to integrate:

1. **`elo_2025.csv`** - Final Elo ratings for all 32 NFL teams
   ```
   team,final_elo
   SEA,1650.21
   DEN,1637.45
   PHI,1621.44
   ...
   ```

2. **`playoff_seeds.json`** (you'll need to create this from the data):
   ```json
   {
     "AFC": {
      "1": "DEN",
      "2": "NE",
      "3": "JAX",
      "4": "PIT",
      "5": "HOU",
      "6": "BUF",
      "7": "LAC"
    },
    "NFC": {
      "1": "SEA",
      "2": "CHI",
      "3": "PHI",
      "4": "CAR",
      "5": "LA",
      "6": "SF",
      "7": "GB"
    }
  }
   ```

### Core JavaScript Logic

#### 1. Load Elo Ratings
Parse `elo_2025.csv` into a JavaScript object:
```javascript
const eloRatings = {
  'SEA': 1650.21,
  'DEN': 1637.45,
  // ... etc
}
```

#### 2. Win Probability Calculation
```javascript
function computeWinProbability(eloHome, eloAway, hfa = 55, isNeutral = false) {
  const diff = isNeutral
    ? eloHome - eloAway
    : (eloHome + hfa) - eloAway;

  return 1 / (1 + Math.pow(10, -diff / 400));
}
```

#### 3. Simulate Single Game
```javascript
function simulateGame(teamHome, teamAway, eloRatings, hfa = 55, isNeutral = false) {
  const eloHome = eloRatings[teamHome];
  const eloAway = eloRatings[teamAway];
  const pHomeWin = computeWinProbability(eloHome, eloAway, hfa, isNeutral);

  const randomDraw = Math.random();
  return randomDraw < pHomeWin ? teamHome : teamAway;
}
```

#### 4. Playoff Bracket Simulation

**Wild Card Round:**
```javascript
function simulateWildCard(conference, seeds, eloRatings) {
  const winners = [seeds[1]]; // Seed 1 gets bye

  // Matchups: 2v7, 3v6, 4v5
  const matchups = [[2,7], [3,6], [4,5]];

  for (let [seedHome, seedAway] of matchups) {
    const teamHome = seeds[seedHome];
    const teamAway = seeds[seedAway];
    const winner = simulateGame(teamHome, teamAway, eloRatings);

    // ANIMATE THIS GAME (1 second)
    await animateGame(teamHome, teamAway, winner, 'wild-card', conference);

    winners.push(winner);
  }

  return winners;
}
```

**Divisional Round (with reseeding):**
```javascript
function simulateDivisional(conference, wildCardWinners, seeds, eloRatings) {
  // Map teams back to seeds
  const teamToSeed = {};
  for (let seed in seeds) {
    teamToSeed[seeds[seed]] = parseInt(seed);
  }

  // Get remaining seeds sorted
  const remainingSeeds = wildCardWinners
    .map(team => teamToSeed[team])
    .sort((a, b) => a - b);

  // Seed 1 hosts lowest seed
  const seed1Team = seeds[1];
  const lowestSeed = Math.max(...remainingSeeds);
  const lowestTeam = seeds[lowestSeed];

  // Other two teams play each other
  const otherSeeds = remainingSeeds.filter(s => s !== 1 && s !== lowestSeed);
  const higherSeed = Math.min(...otherSeeds);
  const lowerSeed = Math.max(...otherSeeds);

  // Simulate games
  const winner1 = simulateGame(seed1Team, lowestTeam, eloRatings);
  await animateGame(seed1Team, lowestTeam, winner1, 'divisional', conference);

  const winner2 = simulateGame(seeds[higherSeed], seeds[lowerSeed], eloRatings);
  await animateGame(seeds[higherSeed], seeds[lowerSeed], winner2, 'divisional', conference);

  return [winner1, winner2];
}
```

**Conference Championship:**
```javascript
function simulateConfChampionship(conference, divisionalWinners, seeds, eloRatings) {
  const teamToSeed = {};
  for (let seed in seeds) {
    teamToSeed[seeds[seed]] = parseInt(seed);
  }

  const remainingSeeds = divisionalWinners.map(t => teamToSeed[t]).sort();
  const higherSeed = remainingSeeds[0];
  const lowerSeed = remainingSeeds[1];

  const teamHome = seeds[higherSeed];
  const teamAway = seeds[lowerSeed];

  const winner = simulateGame(teamHome, teamAway, eloRatings);
  await animateGame(teamHome, teamAway, winner, 'conf-championship', conference);

  return winner;
}
```

**Super Bowl:**
```javascript
function simulateSuperBowl(afcChamp, nfcChamp, eloRatings) {
  const winner = simulateGame(afcChamp, nfcChamp, eloRatings, 55, true); // neutral site

  await animateSuperBowl(afcChamp, nfcChamp, winner);
  await dropWinnerAnimation(winner);
  playVictorySound();

  return winner;
}
```

#### 5. Animation Functions

```javascript
async function animateGame(teamHome, teamAway, winner, round, conference) {
  // 1. Highlight matchup box (border glow)
  highlightMatchupBox(round, conference);

  // 2. Show team names
  displayTeams(teamHome, teamAway, round, conference);

  await sleep(500); // Wait 0.5s

  // 3. Reveal winner (brighten winner, fade loser)
  revealWinner(winner, round, conference);

  await sleep(500); // Wait 0.5s

  // 4. Advance winner to next round
  await slideWinnerToNextRound(winner, round, conference);
}

async function dropWinnerAnimation(winner) {
  // Animate team name dropping to bottom with gravity effect
  const winnerElement = document.getElementById('super-bowl-winner');
  winnerElement.textContent = winner;
  winnerElement.classList.add('drop-animation');

  await sleep(1000);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

#### 6. Scoreboard Update

```javascript
const superBowlWins = {
  'DEN': 0, 'NE': 0, 'JAX': 0, 'PIT': 0, 'HOU': 0, 'BUF': 0, 'LAC': 0,
  'SEA': 0, 'CHI': 0, 'PHI': 0, 'CAR': 0, 'LA': 0, 'SF': 0, 'GB': 0
};

function updateScoreboard(winner) {
  superBowlWins[winner]++;

  // Resort scoreboard
  const sorted = Object.entries(superBowlWins)
    .sort((a, b) => b[1] - a[1]); // Descending by wins

  // Update DOM with smooth reordering animation
  renderScoreboard(sorted, winner);
}

function renderScoreboard(sortedTeams, highlightTeam) {
  const scoreboardElement = document.getElementById('scoreboard');
  scoreboardElement.innerHTML = '';

  sortedTeams.forEach(([team, wins]) => {
    const row = document.createElement('div');
    row.className = 'scoreboard-row';
    if (team === highlightTeam) {
      row.classList.add('highlight-flash'); // CSS animation
    }
    row.textContent = `${team}: ${wins} win${wins !== 1 ? 's' : ''}`;
    scoreboardElement.appendChild(row);
  });
}
```

#### 7. Main Simulation Loop

```javascript
async function runSimulations(numSims) {
  for (let i = 0; i < numSims; i++) {
    // Simulate full playoff bracket
    const afcWinners = await simulateWildCard('AFC', PLAYOFF_SEEDS.AFC, eloRatings);
    const nfcWinners = await simulateWildCard('NFC', PLAYOFF_SEEDS.NFC, eloRatings);

    // Show reseeding message
    await showMessage('Reseeding Divisional Round...', 500);

    const afcDivWinners = await simulateDivisional('AFC', afcWinners, PLAYOFF_SEEDS.AFC, eloRatings);
    const nfcDivWinners = await simulateDivisional('NFC', nfcWinners, PLAYOFF_SEEDS.NFC, eloRatings);

    const afcChamp = await simulateConfChampionship('AFC', afcDivWinners, PLAYOFF_SEEDS.AFC, eloRatings);
    const nfcChamp = await simulateConfChampionship('NFC', nfcDivWinners, PLAYOFF_SEEDS.NFC, eloRatings);

    const superBowlWinner = await simulateSuperBowl(afcChamp, nfcChamp, eloRatings);

    updateScoreboard(superBowlWinner);

    // Countdown between simulations (if not last sim)
    if (i < numSims - 1) {
      await countdown(3);
    }

    // Clear bracket for next simulation
    clearBracket();
  }

  showMessage('All simulations complete!', 2000);
}

async function countdown(seconds) {
  for (let i = seconds; i > 0; i--) {
    showMessage(`Starting next simulation in ${i}...`, 1000);
    await sleep(1000);
  }
}
```

## UI/UX Design Guidelines

### Color Scheme
- **AFC teams**: Shades of blue/red (classic AFC colors)
- **NFC teams**: Shades of green/blue (classic NFC colors)
- **Neutral/background**: Dark gray or light gray for contrast
- **Highlighted matchup**: Bright border (yellow/gold glow)
- **Winner**: Bold green or bright color
- **Loser**: Faded gray

### Typography
- **Team names**: Bold, sans-serif (e.g., Arial, Helvetica)
- **Seeds**: Smaller text in parentheses next to team name
- **Scoreboard**: Monospace font for clean alignment

### Layout Mockup

```
┌─────────────────────────────────────────────────────────────────┐
│                  NFL Playoff Monte Carlo Simulator               │
│  [Number of Sims: ___] [▶ Start Simulation]                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────┬──────────────────────┐
│   AFC BRACKET        │                     │   NFC BRACKET        │
│                      │                     │                      │
│  WILD CARD           │                     │  WILD CARD           │
│  ┌──────────┐        │                     │  ┌──────────┐        │
│  │(2) NE    │        │                     │  │(2) CHI   │        │
│  │(7) LAC   │───┐    │                     │  │(7) GB    │───┐    │
│  └──────────┘   │    │                     │  └──────────┘   │    │
│                 │    │                     │                 │    │
│  ┌──────────┐   │    │                     │  ┌──────────┐   │    │
│  │(3) JAX   │───┤    │                     │  │(3) PHI   │───┤    │
│  │(6) BUF   │   │    │                     │  │(6) SF    │   │    │
│  └──────────┘   │    │                     │  └──────────┘   │    │
│                 ├──► │   DIVISIONAL        │                 ├──► │
│  ┌──────────┐   │    │                     │  ┌──────────┐   │    │
│  │(4) PIT   │───┤    │                     │  │(4) CAR   │───┤    │
│  │(5) HOU   │   │    │                     │  │(5) LA    │   │    │
│  └──────────┘   │    │                     │  └──────────┘   │    │
│                 │    │                     │                 │    │
│  (1) DEN (BYE)───┘   │                     │  (1) SEA (BYE)───┘    │
│                      │                     │                      │
└──────────────────────┴─────────────────────┴──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        SUPER BOWL                                │
│              [AFC CHAMP]  vs  [NFC CHAMP]                        │
│                                                                  │
│                      🏆 WINNER DROPS HERE 🏆                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         SCOREBOARD                               │
│  SEA: 5 wins  ⭐                                                 │
│  DEN: 4 wins                                                     │
│  PHI: 2 wins                                                     │
│  BUF: 1 win                                                      │
│  ...                                                             │
└─────────────────────────────────────────────────────────────────┘
```

## Sound Effect

Include ONE short victory sound (0.5-1 second):
- **Format**: MP3 or WAV
- **Trigger**: Only when Super Bowl winner is revealed
- **Volume**: Moderate, not jarring
- **Suggestions**: Crowd cheer, trophy clank, victory horn

You can use a free sound from:
- https://freesound.org/
- https://mixkit.co/free-sound-effects/

## Deliverables

1. **index.html** - Main HTML structure
2. **style.css** - All styling and CSS animations
3. **script.js** - All JavaScript logic (Elo calculations, simulations, animations)
4. **elo_2025.csv** - Team Elo ratings (provided by user)
5. **victory.mp3** - Victory sound effect
6. **README.md** - Brief instructions on how to use the app

## Files You Will Receive

1. **`elo_2025.csv`** - Contains all 32 NFL teams and their final Elo ratings

That's it! The playoff seeds are hardcoded in the prompt above.

## Testing Checklist

- [ ] Can input number of simulations
- [ ] Bracket animates smoothly (1 second per game)
- [ ] Winners correctly advance to next round
- [ ] Divisional Round shows "Reseeding..." message
- [ ] Super Bowl winner drops with animation
- [ ] Victory sound plays exactly once per Super Bowl
- [ ] Scoreboard updates and resorts correctly
- [ ] Highlighted team flashes briefly in scoreboard
- [ ] 3-second countdown appears between simulations
- [ ] All 10+ simulations complete without errors
- [ ] Responsive design works on different screen sizes

## Stretch Goals (Optional)

- Pause/Resume button during simulation
- Speed control slider (0.5x, 1x, 2x speed)
- Export scoreboard results as CSV
- Dark mode toggle
- Team logos instead of just abbreviations
- Probability percentages shown during each game
- "Skip to end" button to run remaining simulations instantly

---

**Good luck! This should be a fun, visually engaging Monte Carlo simulator.**
