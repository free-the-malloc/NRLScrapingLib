from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.sync_api import Page

from .get_match_data import get_match_data

def grd_matches(round: int, year: int, attributes: list[str], page: Page) -> list[dict]:
    round_data = []

    attribute_tag = ["h3", "p", 
                    "p", "div", 
                    "p", "div"]
    
    attribute_class = ["u-visually-hidden", "match-header__title", 
                    "match-team__name--home", "match-team__score--home", 
                    "match-team__name--away", "match-team__score--away"]
    
    attribute_name = ["Details","Date",
                    "Home","Home Score",
                    "Away","Away Score"]
    
    url = f"https://www.nrl.com/draw/?competition=111&round={round}&season={year}"

    page.goto(url)

    soup = BeautifulSoup(page.content(), "html.parser")

    # Get each match tile
    matches = soup.find_all("div", class_="match o-rounded-box o-shadowed-box")

    for match in matches:
        # Get the extension for the match
        match_extension = match.find("a", class_ = "match--highlighted u-flex-column u-flex-align-items-center u-width-100")

        match_general = {}
        
        match_general["Round"] = round

        for i in range(0,6):
            match_general[attribute_name[i]] = match.find(attribute_tag[i],class_=attribute_class[i]).text.strip()

        match_general["Details"] = match_general["Details"].replace("Match: ","")            
        match_general["Home Score"] = int(match_general["Home Score"].replace("Scored","").replace("points","").strip())
        match_general["Away Score"] = int(match_general["Away Score"].replace("Scored","").replace("points","").strip())

        # Get the statistics for the match
        match_stats = get_match_data(match_extension["href"],attributes, page)
        
        # If the stats from a round couldn't be scraped, return none
        if match_stats == None:
            return None
        # Otherwise append the match stats to the array
        round_data.append({**match_general,**match_stats})
    
    return round_data


def get_round_data(round: int,year: int, attributes: list[str], page: Page) -> list[dict]:
    '''
    Maintain a single browser session, parsing each match page into a 
    BeautifulSoup object then passing that over to the get_match_data function 
    for parsing. 
    '''
    try:
        if page == None:
            with sync_playwright() as pw:
                browser = pw.firefox.launch(headless=True)
                page = browser.new_page()
                round_data = get_round_data(round, year, attributes, page)
                browser.close()
                return round_data
    except Exception as err:
        raise err
    
    round_data = []

    attribute_tag = ["h3", "p", 
                    "p", "div", 
                    "p", "div"]
    
    attribute_class = ["u-visually-hidden", "match-header__title", 
                    "match-team__name--home", "match-team__score--home", 
                    "match-team__name--away", "match-team__score--away"]
    
    attribute_name = ["Details","Date",
                    "Home","Home Score",
                    "Away","Away Score"]
    
    url = f"https://www.nrl.com/draw/?competition=111&round={round}&season={year}"

    retry_count = 0
    while True:
        try:
            page.goto(url)
            break
        except Exception:
            retry_count += 1
            if retry_count == 3:
                print(f"get_round_data: couldn't load season {year} round {round} page")
                raise Exception("get_round_data")

    soup = BeautifulSoup(page.content(), "html.parser")

    # Get each match tile
    matches = soup.find_all("div", class_="match o-rounded-box o-shadowed-box")

    for match in matches:
        # Get the extension for the match
        match_extension = match.find("a", class_ = "match--highlighted u-flex-column u-flex-align-items-center u-width-100")

        match_general = {}
        
        match_general["Round"] = round

        for i in range(0,6):
            match_general[attribute_name[i]] = match.find(attribute_tag[i],class_=attribute_class[i]).text.strip()

        match_general["Details"] = match_general["Details"].replace("Match: ","")            
        match_general["Home Score"] = int(match_general["Home Score"].replace("Scored","").replace("points","").strip())
        match_general["Away Score"] = int(match_general["Away Score"].replace("Scored","").replace("points","").strip())

        # Get the statistics for the match
        try:
            match_stats = get_match_data(match_extension["href"],attributes, page)
        except Exception as err:
            raise err
        
        # If the stats from a round couldn't be scraped, return none
        if match_stats == None:
            return None
        # Otherwise append the match stats to the array
        round_data.append({**match_general,**match_stats})
    
    return round_data
    
