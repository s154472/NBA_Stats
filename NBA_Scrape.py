import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll

class NBAPlayerStatsTracker:
    def __init__(self):
        # Initialize player database
        self.players_db = players.get_players()
        # Mapping of stat types to NBA API column names
        self.stat_mapping = {
            'points': 'PTS',
            'rebounds': 'REB',
            'assists': 'AST',
            'steals': 'STL',
            'blocks': 'BLK',
            '3-pointers': 'FG3M',
            'turnovers': 'TOV'
        }

    def find_player_id(self, player_name):
        """
        Find NBA player ID based on full or partial name
        """
        matching_players = [
            player for player in self.players_db 
            if player_name.lower() in player['full_name'].lower()
        ]
        
        if not matching_players:
            print(f"No player found matching {player_name}")
            return None
        
        # If multiple matches, let user choose
        if len(matching_players) > 1:
            print("Multiple players found:")
            for i, player in enumerate(matching_players, 1):
                print(f"{i}. {player['full_name']} (ID: {player['id']})")
            
            try:
                choice = int(input("Enter the number of the correct player: ")) - 1
                return matching_players[choice]['id']
            except (ValueError, IndexError):
                print("Invalid selection. Using the first match.")
                return matching_players[0]['id']
        
        return matching_players[0]['id']

    def get_player_stats(self, player_name, stat_type='points'):
        """
        Retrieve recent game stats for a specific stat
        
        :param player_name: Name of the NBA player
        :param stat_type: Type of stat to retrieve
        """
        # Mapping of stat types to NBA API column names
        
        
        # Normalize stat type
        stat_type = stat_type.lower()
        if stat_type not in self.stat_mapping:
            print(f"Unsupported stat type. Choose from: {', '.join(self.stat_mapping.keys())}")
            return pd.DataFrame()

        # Find player ID
        player_id = self.find_player_id(player_name)
        if not player_id:
            return pd.DataFrame()

        try:
            # Fetch game log for the player
            gamelog = playergamelog.PlayerGameLog(
                player_id=player_id, 
                season=SeasonAll.default
            )
            
            # Convert to DataFrame
            df = gamelog.get_data_frames()[0]
            
            # Explicitly parse date with specified format
            # Use a try-except to handle potential date format variations
            try:
                # Try with specific format first
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%m/%d/%Y')
            except:
                # Fallback to more flexible parsing if specific format fails
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], errors='coerce')
            
            # Get the specific stat column
            stat_column = self.stat_mapping[stat_type]
            
            # Convert stat column to numeric
            df[stat_column] = pd.to_numeric(df[stat_column], errors='coerce')
            
            # Sort by date (most recent first)
            df = df.sort_values('GAME_DATE', ascending=False)
            
            # Take last 10 games
            last_10_games = df.head(10)
            
            # Print analysis
            print(f"\n{player_name} - {stat_type.capitalize()} Analysis:")
            print(f"Average in Last 10 Games: {last_10_games[stat_column].mean():.2f}")
            print(f"Best Performance: {last_10_games[stat_column].max()}")
            print(f"Worst Performance: {last_10_games[stat_column].min()}")
            print("\nRecent Games:")
            print(last_10_games[['GAME_DATE', stat_column]])
            
            return last_10_games
        
        except Exception as e:
            print(f"Error retrieving player stats: {e}")
            return pd.DataFrame()

def main():
    tracker = NBAPlayerStatsTracker()
    
    while True:
        print("\n--- NBA Player Stats Tracker ---")
        print("1. Get Player Stats")
        print("2. Exit")
        
        choice = input("Enter your choice (1/2): ")
        
        if choice == '1':
            player_name = input("Enter player name (e.g., Stephen Curry): ")
            stat_type = input("Enter stat type (points/rebounds/assists/steals/blocks/3-pointers/turnovers): ")
            
            # Fetch and display player stats
            tracker.get_player_stats(player_name, stat_type)
        
        elif choice == '2':
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

