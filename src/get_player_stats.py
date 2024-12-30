from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.sync_api import Page

"""
Returns two lists, each holding dictionaries of each players performance
in a match as indicated by the url extension supplied. The first list holds
the home team's players, and the second list holds the away teams players.
"""
def get_player_stats(extension: str, page: Page):
    if page == None:
        with sync_playwright() as pw:
            browser = pw.firefox.launch(headless=True)
            page = browser.new_page()
            match_data = get_player_stats(extension, page)
            browser.close()
            return match_data
    
    url = f"https://www.nrl.com{extension}"

    page.goto(url)
    soup = BeautifulSoup(page.content(), "html.parser")

    player_stats_box = soup.find("div", id="tabs-match-centre-4", 
                               class_="tabs__panel").find("div",id="player-stats")
    tables = player_stats_box.find_all("table")

    features = tables[0].find("thead").find_all("tr")[1].find_all("th")

    match_data = []

    for table in tables:
        table_body = table.find("tbody")
        players = table_body.find_all("tr")

        player_dicts = []

        for player in players[0:1]:
            player_data = dict()
            player_stats = player.find_all("td")
            player_name = "_".join(player_stats[1].text.strip().lower().split())
            

            for feature in zip(features,player_stats):
                feature_name = " ".join(feature[0].text.strip().split())
                if feature_name == "":
                    continue
                
                stat = feature[1].text.strip()

                if feature_name == "Number":
                    if int(stat) > 17:
                        stat = 18
                    player_data[feature_name] = int(stat)
                elif stat == "" or stat == "-" or feature_name == "Position" or feature_name == "Player":
                    continue
                elif (feature_name == "Mins Played") or (feature_name == "Stint One") or (feature_name == "Stint Two"):
                    time_crunch = [int(x) for x in stat.split(":")]
                    player_data[feature_name] = (time_crunch[0] * 60) + time_crunch[1]
                elif feature_name == "Tackle Efficiency" or feature_name == "Goal Conversion Rate":
                    player_data[feature_name] = round(float(stat.strip("%")), 2)
                elif feature_name == "Average Play The Ball Speed" or feature_name == "Passes To Run Ratio":
                    player_data[feature_name] = round(float(stat.strip("s")), 2)
                else:
                    player_data[feature_name] = int(stat)

            player_dicts.append(player_data)
        
        match_data.append(player_dicts)
    
    return match_data
