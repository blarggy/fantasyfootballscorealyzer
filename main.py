import pandas as pd

# Data collected from https://www.pro-football-reference.com/years/2022/defense.htm

# Current settings
offense_points = {
    'Rec': 0.5,
    'YScm': 0.10,
    'RRTD': 6,
    'Att': 0.10,
    '1D': 0.5,
    'Fmb': -1.5
}

defense_points = {
    'Int': 4,
    'TD': 10,
    'PD': 6,
    'FF': 4,
    'FR': 4,
    'Sk': 4,
    'Solo': 1,
    'Ast': 0.5,
    'TFL': 2,
    'QBHits': 1,
    'Sfty': 8
}

# Changed settings
# offense_points = {
#     'Rec': 0.5,
#     'YScm': 0.10,
#     'RRTD': 6,
#     'Att': 0.10,
#     '1D': 0.5,
#     'Fmb': -1.5
# }
#
# defense_points = {
#     'Int': 6,
#     'TD': 8,
#     'PD': 4,
#     'FF': 4,
#     'FR': 4,
#     'Sk': 4,
#     'Solo': 1,
#     'Ast': 0.5,
#     'TFL': 2,
#     'QBHits': 1,
#     'Sfty': 10
# }


def calculate_offense_fantasy_points(row):
    points = 0
    for key, value in offense_points.items():
        if key in row:
            points += row[key] * value
    return points


def calculate_defense_fantasy_points(row):
    points = 0
    for key, value in defense_points.items():
        if key in row:
            points += row[key] * value
    return points


offense_df = pd.read_csv('data/nfl_2022_offense_stats.csv', skiprows=1)
columns_to_fill_with_zero = ['Rec', 'YScm', 'RRTD', 'Att', '1D', 'Fmb']
offense_df[columns_to_fill_with_zero] = offense_df[columns_to_fill_with_zero].fillna(0)
defense_df = pd.read_csv('data/nfl_2022_defense_stats.csv', skiprows=1)
columns_to_fill_with_zero = ['Int', 'PD', 'FF', 'FR', 'Sk', 'Solo', 'Ast', 'TFL', 'QBHits', 'Sfty']
defense_df[columns_to_fill_with_zero] = defense_df[columns_to_fill_with_zero].fillna(0)

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

defense_df = defense_df[defense_df['Pos'] != 'QB']

defense_df.sort_values(by='Fantasy Points', ascending=False, inplace=True)
defense_df['Rk'] = range(1, len(defense_df) + 1)
defense_df.reset_index(drop=True, inplace=True)

defense_df.to_csv('fantasy_stats_defense.csv', index=False)
