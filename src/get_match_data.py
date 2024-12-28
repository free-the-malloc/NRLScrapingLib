from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.sync_api import Page

def get_match_data(extension: str, attributes: list[str], page: Page) -> dict:
    match_data = {}

    stats_class = ["stats-bar-chart__label stats-bar-chart__label--home",
                    "stats-bar-chart__label stats-bar-chart__label--home u-font-weight-700",
                    "stats-bar-chart__label stats-bar-chart__label--away",
                    "stats-bar-chart__label stats-bar-chart__label--away u-font-weight-700"]
    
    possession_class = ["match-centre-card-donut__value match-centre-card-donut__value--home",
                        "match-centre-card-donut__value match-centre-card-donut__value--home u-font-weight-500",
                        "match-centre-card-donut__value match-centre-card-donut__value--away u-font-weight-500",
                        "match-centre-card-donut__value match-centre-card-donut__value--away"]

    completion_class = ["match-centre-card-donut__value match-centre-card-donut__value--footer u-font-weight-500",
                        "match-centre-card-donut__value match-centre-card-donut__value--footer"]

    play_the_ball_class = "donut-chart-stat__value"

    '''
    Check whether a BeautifulSoup object has already been given, if not then
    attempt to parse the page. Handle a TimeoutError or WebError and return 
    None.
    '''

    try:
        url = f"https://www.nrl.com{extension}"
        if page == None:
            with sync_playwright() as pw:
                browser = pw.firefox.launch(headless=True)
                page = browser.new_page()

                page.goto(url)
                soup = BeautifulSoup(page.content(), "html.parser")
                browser.close()
        else:
            page.goto(url)
            soup = BeautifulSoup(page.content(), "html.parser")
    except Exception:
        print("page timed out")
        return None

    # Get the main team stats tile, then locate each individual stats tile
    team_stats_box = soup.find("div", id="tabs-match-centre-3", 
                               class_="tabs__panel")
    stats_tiles = team_stats_box.find_all("div",
                    class_ = "u-spacing-pb-24 u-spacing-pt-16 u-width-100")

    for stats_box_i in stats_tiles:
        elements = []

        stat_box_label = stats_box_i.find(["h3","figcaption"])

        if stat_box_label != None and stat_box_label.text in attributes:
            stat_box_label = stat_box_label.text
        else:
            continue

        '''
        The following set of if statements deals with different stats tiles.
        Barring Completion Rate, the relevant figures are scraped from each 
        tile and parsed into the elements array. The final if statement 
        ensures that two figures have been placed into the elements array.
        Completion rate is different in that it is actually split into two
        new variables, Completed Sets and Total Sets. 
        '''
        if stat_box_label == "Completion Rate":
            completion_rate = stats_box_i.find_all("p", class_ = completion_class)
            
            if len(completion_rate) != 2:
                continue
            
            completion_rate = [ x.text.split("/") for x in completion_rate]
            completion_rate = [[int(x) for x in y] for y in completion_rate]

            match_data["Home Completed Sets"] = completion_rate[0][0]
            match_data["Home Total Sets"] = completion_rate[0][1]

            match_data["Away Completed Sets"] = completion_rate[1][0]
            match_data["Away Total Sets"] = completion_rate[1][1]

            continue
        
        elif stat_box_label == "Average Play The Ball Speed":
            elements = stats_box_i.find_all("p", class_ = play_the_ball_class)
            elements = [float(x.text.replace('s','')) for x in elements]

        elif stat_box_label == "Kick Defusal %" or stat_box_label == "Effective Tackle %":
            type = int
            
            if stat_box_label == "Effective Tackle %":
                type = float
            
            elements = stats_box_i.find_all("p", class_ = "donut-chart-stat__value")
            elements = [type(x.text.replace("%","")) for x in elements]

        elif stat_box_label == "Possession %":
            elements = stats_box_i.find_all("p", class_ = possession_class)
            elements = [int(x.text.replace("%","")) for x in elements]

        elif stat_box_label == "Average Set Distance":
            elements = stats_box_i.find_all("dd", class_ = stats_class)
            elements = [float(x.text) for x in elements]

        elif stat_box_label == "Time In Possession":
            elements = stats_box_i.find_all("dd", class_ = stats_class)
            elements = [x.text.strip().split(":") for x in elements]
            elements = [int(x[0]) + (int(x[1]) / 60) for x in elements]

        else:
            elements = stats_box_i.find_all("dd", class_ = stats_class)
            elements = [int(x.text.replace(",","")) for x in elements]


        if len(elements) == 2:
            match_data[f"Home {stat_box_label}"] = elements[0]
            match_data[f"Away {stat_box_label}"] = elements[1]

    return match_data
   
