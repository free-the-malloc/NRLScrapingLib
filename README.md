# nrl-scraping-lib

A set of functions I put together to scrape match statistics from the National Rugby League website.

We have a function to read a single match, get_match_data, which takes in the extension of the match url (the string that follows after "www.nrl.com") and the array of attributes to be scraped. Returns a dictionary object.

There is a function for reading all the matches in a given round, get_round_data, which takes in a season, round, and a list of attributes, and returns an array of dictionaries, each dict holding the data from a match. 

