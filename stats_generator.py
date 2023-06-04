import sqlite3
import pandas as pd
import numpy as np
import sys

class StatsGenerator:
    def __init__(self, df, cur):
        self.df = df
        self.cur = cur

    def get_indexes(self):
        idxs = self.df[self.df['Unnamed: 1'].str.find("Game") == 0].index.tolist() + [self.df.shape[0] - 1]
        return idxs

    def get_games(self, start, end):
        games = self.df.loc[start+1:end- 1,"Unnamed: 2":"Unnamed: 5"]
        games.dropna(axis=0, how='all', inplace=True)
        # games.drop(columns=['Unnamed: 2'], inplace=True)
        headers = ['game_number'] + games.iloc[0].tolist()[1:]
        games = pd.DataFrame(games.values[1:], columns=headers)
        return games

    def get_game_part(self, start):
        if self.df.loc[start+1,"Unnamed: 12"] is not np.nan:
            game_part = self.df.loc[start+1,"Unnamed: 12"].split(' ')[1]
        else:
            game_part = 1
        return int(game_part)

    def get_game_day(self, start):
        game_day = self.df.loc[start, 'Unnamed: 1'].split(' ')[1]
        game_day_reversed = game_day.split('.')[2] + '.' + game_day.split('.')[1] + '.' + game_day.split('.')[0]
        return game_day_reversed

    def get_game_stats(self, games, game_day, game_part): 
        game_stats =[]
        for idx, row in games.iterrows():
            if row['Blue'] is np.nan:
                team_1 = (game_day, game_part, row['game_number'], 'Orange', 1 if row['Orange'] > row['Green'] else 0, 1 if row['Orange'] == row['Green'] else 0, 1 if row['Orange'] < row['Green'] else 0, row['Orange'] - row['Green'], row['Orange'], row['Green'])
                team_2 = (game_day, game_part, row['game_number'], 'Green', 1 if row['Orange'] < row['Green'] else 0, 1 if row['Orange'] == row['Green'] else 0, 1 if row['Orange'] > row['Green'] else 0, row['Green'] - row['Orange'], row['Green'], row['Orange'])
                game_stats.append(team_1)
                game_stats.append(team_2)
            if row['Orange'] is np.nan:
                team_1 = (game_day, game_part, row['game_number'], 'Blue', 1 if row['Blue'] > row['Green'] else 0, 1 if row['Blue'] == row['Green'] else 0, 1 if row['Blue'] < row['Green'] else 0, row['Blue'] - row['Green'], row['Blue'], row['Green'])
                team_2 = (game_day, game_part, row['game_number'], 'Green', 1 if row['Blue'] < row['Green'] else 0, 1 if row['Blue'] == row['Green'] else 0, 1 if row['Blue'] > row['Green'] else 0, row['Green'] - row['Blue'], row['Green'], row['Blue'])
                game_stats.append(team_1)
                game_stats.append(team_2)
            if row['Green'] is np.nan:
                team_1 = (game_day, game_part, row['game_number'], 'Blue', 1 if row['Blue'] > row['Orange'] else 0, 1 if row['Blue'] == row['Orange'] else 0, 1 if row['Blue'] < row['Orange'] else 0, row['Blue'] - row['Orange'], row['Blue'], row['Orange'])
                team_2 = (game_day, game_part, row['game_number'], 'Orange', 1 if row['Blue'] < row['Orange'] else 0, 1 if row['Blue'] == row['Orange'] else 0, 1 if row['Blue'] > row['Orange'] else 0, row['Orange'] - row['Blue'], row['Orange'], row['Blue'])
                game_stats.append(team_1)
                game_stats.append(team_2)
        return game_stats
    
    def get_points(self, game_stats):
        points = pd.DataFrame(game_stats)
        points = points.groupby(3).sum()
        return points

    def get_teams(self, start):
        teams = self.df.loc[start+2:start+8,"Unnamed: 7":"Unnamed: 9"]
        headers = teams.iloc[0].tolist()
        teams  = pd.DataFrame(teams.values[1:], columns=headers)
        return teams
    
    def get_players(self, teams, game_day, game_part):
        players = []
        for team_color in teams.columns:
            for player in teams[team_color]:
                if player is not np.nan:
                    player_info = (game_day, game_part, player[:-4] if player.endswith('(c)') else player, team_color, 1 if player.endswith('(c)') else 0)
                    players.append(player_info)
        return players

    def get_overall_games(self, start, end):
        idxs = self.get_indexes()
        game_dfs = []
        for i in range(start, end):
            games = self.get_games(idxs[i], idxs[i+1])
            game_part = self.get_game_part(idxs[i])
            game_day = self.get_game_day(idxs[i])
            game_stats = self.get_game_stats(games, game_day, game_part)
            game_dfs.extend(game_stats)
        return game_dfs

    def get_overall_players(self, start, end):
        idxs = self.get_indexes()
        player_dfs = []
        for i in range(start, end):
            teams = self.get_teams(idxs[i])
            game_part = self.get_game_part(idxs[i])
            game_day = self.get_game_day(idxs[i])
            players = self.get_players(teams, game_day, game_part)
            player_dfs.extend(players)
        return player_dfs

    def drop_tables(self):
        self.cur.execute("""DROP TABLE players""")
        self.cur.execute("""DROP TABLE games""")
        return
    
    def create_tables(self):
        self.cur.execute("""CREATE TABLE 
                players(
                    date varchar, 
                    game_part int, 
                    name varchar, 
                    team varchar, 
                    captain integer)""")

        self.cur.execute("""CREATE TABLE 
                games(
                    date varchar, 
                    game_part int, 
                    game_number int, 
                    team varchar, 
                    win integer, 
                    draw integer, 
                    lose integer, 
                    goal_difference integer, 
                    goals_scored integer, 
                    goals_conceded integer)""")
        
        return

    def insert_games(self, games):
        for game in games:
            q = f"""INSERT INTO games(date, game_part, game_number, team, win, draw, lose, goal_difference, goals_scored, goals_conceded) VALUES('{(game[0])}',{game[1]},{game[2]},'{game[3]}',{game[4]},{game[5]},{game[6]},{game[7]},{game[8]},{game[9]})"""
            self.cur.execute(q)
        return
    
    def insert_players(self, players):
        for player in players:
            q = f"""INSERT INTO players(date, game_part, name, team, captain) VALUES('{(player[0])}', {player[1]},'{player[2]}','{player[3]}',{player[4]})"""
            self.cur.execute(q)
        return
    
    def get_player_names(self, count_of_games):
        q = f"""SELECT 
                p.name 
            FROM players as p 
            JOIN games as g 
            ON 
                p.team = g.team 
                and 
                p.date = g.date 
                and 
                p.game_part=g.game_part 
            WHERE 
                p.name <> 'Nurseit' 
                and 
                p.name <> 'Nauryzbay' 
                and 
                p.name <> 'Almas A.' 
                GROUP BY p.name 
                having count(*) > {count_of_games}"""
        self.cur.execute(q)
        res = self.cur.fetchall()
        player_names = list(map(lambda x: x[0], res))
        return player_names
    
    def get_overall_stats(self, player_names, num_of_last_games):
        overall_stats = []
        for player_name in player_names:
            q = f"""SELECT 
                        name as Name, 
                        1.0*sum(win*3+draw)/count(*) as 'Pts/G',
                        1.0*sum(goal_difference)/count(*) as 'GD/G', 
                        1.0*sum(goals_scored)/count(*) as 'GF/G', 
                        1.0*sum(goals_conceded)/count(*) as 'GA/G', 
                        count(*) as Games
                    FROM 
                        (SELECT 
                            * 
                        FROM 
                            players as p 
                        JOIN 
                            games as g 

                        ON p.team = g.team 
                            and 
                            p.date = g.date 
                            and 
                            p.game_part=g.game_part 
                        WHERE 
                            p.name = '{player_name}' 
                        ORDER BY 
                            g.date desc, g.game_part desc, g.game_number desc limit {num_of_last_games})"""
            self.cur.execute(q)
            res = self.cur.fetchall()
            overall_stats.extend(res)
        return overall_stats

if __name__ == '__main__':
    con = sqlite3.connect("seoul_nomads.sqlite")
    cur = con.cursor()

    df = pd.read_excel(sys.argv[1], sheet_name="Games")
    print('File Loaded\n')

    sg = StatsGenerator(df, cur)
    print('Class Initalized\n')

    idxs = sg.get_indexes()

    ovrl_gms = sg.get_overall_games(0, len(idxs)-1)
    ovrl_pls = sg.get_overall_players(0, len(idxs)-1)

    sg.insert_games(ovrl_gms)
    sg.insert_players(ovrl_pls)

    player_names = sg.get_player_names(50)
    res = sg.get_overall_stats(player_names, 50)
    print('Stats Recorded\n')

    stats = pd.DataFrame(res)
    stats = stats.sort_values(by=[1, 2], ascending=False).round(2).reset_index(drop=True)
    stats.to_csv('stats.csv')
    print('Stats Saved!\n')