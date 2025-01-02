# NRL Scraping Library

A set of functions for scraping match statistics from the National Rugby League website.

Utilises Playwright for accessing page data.

- **get_match_data** takes in the match extension (the url extension of the particular match following *www.nrl.com*) and a list of attributes. The *attributes.txt* file contains a list of the team match statistics that are reported. The function returns a dictionary object containing the home and away match statistics.

- **get_round_data** takes in the round, season, and list of attributes to be scraped. It returns a list of dictionary objects (returned from the get_match_data function as well as some general match data). Finals matches can be scraped using this function. If the regular season has 27 rounds, and there are four rounds of the finals, then the first week of the finals will be read as round 28, and the last round of the finals (the grand final) would be round 31.

- **get_player_stats** takes the extension for a particular match, and returns two lists. Each list holds dictionaries of the match statistics for each player in the match. The first list holds the home player statistics, and the second list holds the away player statistics.
