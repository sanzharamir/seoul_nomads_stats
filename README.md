# README

This is a script that generates statistics from a dataset of games using the Seoul Nomads SQLite database.

## Prerequisites

To run this script, make sure you have the following installed:

- Python (version 3.0 or higher)

## Installation

1. Clone or download the repository to your local machine.
2. Open a command prompt or terminal and navigate to the directory where the script is located.
3. Install the required dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Make sure you have the necessary database file ("seoul_nomads.sqlite") in the same directory as the script. If it is located elsewhere, modify the script accordingly.
2. Prepare your dataset file in Excel format.
3. Open a command prompt or terminal and navigate to the directory where the script is located.
4. Run the script using the following command:
   ```
   python stats_generator.py /path/to/dataset_file.xlsx
   ```
   Replace "/path/to/dataset_file.xlsx" with the actual file path to your dataset file.

## Output

The script performs the following steps:

1. Connects to the "seoul_nomads.sqlite" database.
2. Loads the dataset from the specified Excel file.
3. Initializes the `StatsGenerator` class.
4. Retrieves the indexes from the dataset.
5. Retrieves overall game statistics.
6. Retrieves overall player statistics.
7. Inserts the game statistics into the database.
8. Inserts the player statistics into the database.
9. Retrieves player names.
10. Retrieves overall player statistics for the top 50 players.
11. Saves the statistics to a CSV file named "stats.csv".

## Note

- Make sure you have the necessary permissions to read the dataset file and write the output CSV file.
- Modify the script if the database file is located in a different directory or has a different name.
- Provide the complete file path to the dataset file when running the script.

Feel free to modify the script to suit your specific requirements.