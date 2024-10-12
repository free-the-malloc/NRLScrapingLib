# nrl-scraping-lib

A set of functions for scraping match statistics from the National Rugby League website.

The functions require a working version of Chrome. The functions can be a bit heavy on the computer as the webpages are loaded using Selenium, which essentially automates the process of opening a webpage and reading the webpage. Reading the data using simple page requests didn't seem to work, as such I have attempted to make the functions less intensive by playing around with the driver options.

- **get_match_data** takes in the match extension (the url extension of the particular match following *www.nrl.com*) and a list of attributes. The *attributes.txt* file contains a list of the team match statistics that are reported. The function returns a dictionary object containing the home and away match statistics.

- **get_round_data** takes in the round, season, and list of attributes to be scraped. It returns a list of dictionary objects (returned from the get_match_data function as well as some general match data). Finals matches can be scraped using this function. If the regular season has 27 rounds, and the finals have 4 rounds, then the first week of the finals will be read as round 28, and the last round of the finals (the grand final) would be round 31.

# Action List

- Include functionality for FireFox.
- Include some sample scripts for scraping season and slices of seasons.
