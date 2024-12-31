from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.sync_api import Page

"""
Returns two lists, each holding dictionaries of each players performance
in a match as indicated by the url extension supplied. The first list holds
the home team's players, and the second list holds the away teams players.
"""
def get_player_stats(extension: str, page: Page):
    try:
        if page == None:
            with sync_playwright() as pw:
                browser = pw.firefox.launch(headless=True)
                page = browser.new_page()
                match_data = get_player_stats(extension, page)
                browser.close()
                return match_data
    except Exception as err:
        raise err
    
    url = f"https://www.nrl.com{extension}"

    retry_count = 0
    while True:
        try:
            page.goto(url)
            break
        except Exception:
            retry_count += 1
            if retry_count == 3:
                print(f"get_player_stats: retry count exceeded, url extension: {extension}")
                raise Exception("get_player_stats: retry count exceeded.")


    soup = BeautifulSoup(page.content(), "html.parser")

    player_stats_box = soup.find("div", id="tabs-match-centre-4", 
                               class_="tabs__panel").find("div",id="player-stats")
    tables = player_stats_box.find_all("table")
    tables = [tables[1], tables[3]]

    features = tables[0].find("thead").find_all("tr")[1].find_all("th")

    match_data = []

    for table in tables:
        features = table.find("thead").find_all("tr")[1].find_all("th")
        table_body = table.find("tbody")
        players = table_body.find_all("tr")

        team_data = []
        last_read = 0
    
        for player in players:
            player_data = dict()
            player_stats = player.find_all("td")
            player_data["Player"] = "_".join(player_stats[1].text.strip().lower().split())

            for feature in zip(features,player_stats):
                feature_name = " ".join(feature[0].text.strip().split())
                if feature_name == "":
                    continue
                
                stat = feature[1].text.strip()

                if feature_name == "Number":
                    if int(stat) > 17: # handle replacement/interchange players with irregular numbers
                        if last_read > 17:
                            last_read += 1
                        else:
                            last_read = 18
                        stat = last_read
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

            team_data.append(player_data)
        match_data.append(team_data)       
    return match_data
