import pandas as pd

"""
    Defense Data collected from https://www.pro-football-reference.com/years/2022/defense.htm
    Offense data collected from https://www.pro-football-reference.com/years/2023/scrimmage.htm
    Sack yards: https://www.footballdb.com/statistics/nfl/player-stats/defense/2023/regular-season
"""

# Current settings
# offense_points = {
#     'Rec': 0.5,
#     'YScm': 0.10,
#     'RRTD': 6,
#     '1DRec': 0.5,
#     '1DRush': 0.5,
#     'Fmb': -1,
#     'Lost': -1
# }
#
# defense_points = {
#     'Int': 4,
#     'IntRetYds': 0,
#     'IntTD': 10,
#     'FumTD': 10,
#     'PD': 6,
#     'FF': 4,
#     'FR': 4,
#     'FumRetYds': 0,
#     'Sk': 4,
#     'SackYdsL': 0.1,
#     'Solo': 1,
#     'Ast': 0.5,
#     'TFL': 2,
#     'QBHits': 1,
#     'Sfty': 8
# }

# Changed settings
offense_points = {
    'Rec': 0.5,
    'YScm': 0.10,
    'RRTD': 6,
    '1DRec': 0.5,
    '1DRush': 0.5,
    'Fmb': -1,
    'Lost': -1
}

defense_points = {
    'Int': 6,
    'IntRetYds': 0.1,
    'IntTD': 6,
    'FumTD': 6,
    'PD': 3,
    'FF': 4,
    'FR': 4,
    'FumRetYds': 0.1,
    'Sk': 4,
    'SackYdsL': 0.1,
    'Solo': 1,
    'Ast': 0.5,
    'TFL': 2,
    'QBHits': 1,
    'Sfty': 8
}

"""
NFL Stats are a funny thing. They're expensive to get exactly what you want. so I have to collect them and format them the way I need.
PFR doesn't include data for sack yards lost, and for offense it doesn't include lost fumbles, only total fumbles. So first, have to combine them.
"""


def get_valid_defense_data():
    # For this file, change Def Interceptions "Yds" to "IntRetYds", change Def Interceptions "TD" to "IntTD", change Fumbles "TD" to "FumTD", change Fumbles "Yds" to "FumRetYds"
    # Also remove instances of "*" and "+" for both files since PFR includes info about pro bowl
    initial_defense_stats_df = pd.read_csv('data/nfl_2023_defense_stats.csv', skiprows=1)
    sack_yds_df = pd.read_csv('data/nfl_2023_sack_yards.csv')
    initial_defense_stats_df.set_index('Player', inplace=True)
    sack_yds_df.set_index('Player', inplace=True)
    initial_defense_stats_df.index.name = 'Player'
    merged_df = pd.merge(initial_defense_stats_df, sack_yds_df, how='left', left_index=True, right_index=True)
    merged_df.reset_index(inplace=True)
    merged_df.dropna(subset=['Player'], inplace=True)
    merged_df.fillna(0, inplace=True)
    # merged_df.loc[merged_df['Pos'].isin(['CB', 'S'])] = 'DB'
    # merged_df.loc[merged_df['Pos'].isin(['DE'])] = 'DT'
    # merged_df.loc[merged_df['Pos'].isin(['OLB'])] = 'LB'
    merged_df.to_csv('data/nfl_2023_defense_merged_stats.csv', index=False)


def get_valid_offense_data():
    # Change Receiving 1D to "1DRec", change Rushing 1D to "1DRush"
    # Also remove instances of "*" and "+" for both files since PFR includes info about pro bowl
    initial_offense_stats_df = pd.read_csv('data/nfl_2023_offense_stats.csv', skiprows=1)
    fum_lost_df = pd.read_csv('data/nfl_2023_fumbles_lost.csv')
    initial_offense_stats_df.set_index('Player', inplace=True)
    fum_lost_df.set_index('Player', inplace=True)
    initial_offense_stats_df.index.name = 'Player'
    merged_df = pd.merge(initial_offense_stats_df, fum_lost_df, how='left', left_index=True, right_index=True)
    merged_df.reset_index(inplace=True)
    merged_df.dropna(subset=['Player'], inplace=True)
    merged_df.fillna(0, inplace=True)
    merged_df.to_csv('data/nfl_2023_offense_merged_stats.csv', index=False)


def calculate_offense_fantasy_points(row):
    points = 0
    for key, value in offense_points.items():
        if key == 'Rec':
            # Handle special case for TE
            if row['Pos'] == 'TE':
                points += row.get(key, 0) * 1  # Update Rec value to 1 for TE
            else:
                points += row.get(key, 0) * value
        else:
            points += row.get(key, 0) * value
    return points


def calculate_defense_fantasy_points(row):
    points = 0
    for key, value in defense_points.items():
        if key in row:
            points += row[key] * value
    return points


get_valid_defense_data()
get_valid_offense_data()

offense_df = pd.read_csv('data/nfl_2023_offense_merged_stats.csv')
# columns_to_fill_with_zero = ['Rec', 'YScm', 'RRTD', 'Att', '1D', 'Fmb', 'IntRetYds', 'FumRetYds', 'SackYdsL']  # need filler values to avoid errors
# offense_df[columns_to_fill_with_zero] = offense_df[columns_to_fill_with_zero].fillna(0)
offense_df.fillna(0)
defense_df = pd.read_csv('data/nfl_2023_defense_merged_stats.csv')
# columns_to_fill_with_zero = ['Int', 'PD', 'FF', 'FR', 'Sk', 'Solo', 'Ast', 'TFL', 'QBHits', 'Sfty'] # need filler values to avoid errors
# defense_df[columns_to_fill_with_zero] = defense_df[columns_to_fill_with_zero].fillna(0)
defense_df.fillna(0)

offense_df['Fantasy Points'] = offense_df.apply(calculate_offense_fantasy_points, axis=1)
defense_df['Fantasy Points'] = defense_df.apply(calculate_defense_fantasy_points, axis=1)

combined_df = pd.concat([offense_df, defense_df])
combined_df = combined_df[combined_df['Pos'] != 'QB']

combined_df.sort_values(by='Fantasy Points', ascending=False, inplace=True)
combined_df['Rk'] = range(1, len(combined_df) + 1)

combined_df.reset_index(drop=True, inplace=True)
combined_df.to_csv('fantasy_stats.csv', index=False)

offense_df = offense_df[offense_df['Pos'] != 'QB']

offense_df.sort_values(by='Fantasy Points', ascending=False, inplace=True)
offense_df['Rk'] = range(1, len(offense_df) + 1)
offense_df.reset_index(drop=True, inplace=True)

offense_df.to_csv('fantasy_stats_offense.csv', index=False)

# defense_df = defense_df[defense_df['Pos'] != 'QB']

defense_df.sort_values(by='Fantasy Points', ascending=False, inplace=True)
defense_df['Rk'] = range(1, len(defense_df) + 1)
defense_df.reset_index(drop=True, inplace=True)

defense_df.to_csv('fantasy_stats_defense.csv', index=False)
