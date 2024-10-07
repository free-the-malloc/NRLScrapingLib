from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def get_match_data(extension,attributes):
    # Setup the driver and get the match page source
    url = f"https://www.nrl.com{extension}"
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--headless')
    options.add_experimental_option(
        "prefs", {
            "profile.managed_default_content_settings.images": 2,
        }
    )
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(45)
    try:
        driver.get(url)
    except:
        driver.quit()
        return None

    page_source = driver.page_source
    driver.quit()
    
    time.sleep(6)
 
    # Parse the webpage source into a BeautifulSoup object
    soup = BeautifulSoup(page_source, "html.parser")

    # Get the team stats tile
    team_stats_box = soup.find_all("div",class_="u-spacing-pb-24 u-spacing-pt-16 u-width-100")

    # Actual data we're looking for will be in an element under these classes
    home_stats_class = ["stats-bar-chart__label stats-bar-chart__label--home",
                        "stats-bar-chart__label stats-bar-chart__label--home u-font-weight-700"]
    away_stats_class = ["stats-bar-chart__label stats-bar-chart__label--away",
                        "stats-bar-chart__label stats-bar-chart__label--away u-font-weight-700"]
    
    home_possession_class = ["match-centre-card-donut__value match-centre-card-donut__value--home",
                             "match-centre-card-donut__value match-centre-card-donut__value--home u-font-weight-500"]
    away_possession_class = ["match-centre-card-donut__value match-centre-card-donut__value--away u-font-weight-500",
                             "match-centre-card-donut__value match-centre-card-donut__value--away"]

    completion_class = ["match-centre-card-donut__value match-centre-card-donut__value--footer u-font-weight-500",
                        "match-centre-card-donut__value match-centre-card-donut__value--footer"]

    play_the_ball_class = "donut-chart-stat__value"
    
    match_data = {}

    for stats_box_i in team_stats_box:
        stat_box_label = stats_box_i.find("h3")
        if stat_box_label != None:
            stat_box_label = stat_box_label.text
            
            if stat_box_label in attributes:
                if stat_box_label == "Completion Rate":
                    completion_rate = stats_box_i.find_all("p",{"class":completion_class})
                    
                    home_completion_rate = completion_rate[0].text.strip().split("/")
                    match_data["Home Completed Sets"] = int(home_completion_rate[0])
                    match_data["Home Total Sets"] = int(home_completion_rate[1])

                    away_completion_rate = completion_rate[1].text.strip().split("/")
                    match_data["Away Completed Sets"] = int(away_completion_rate[0])
                    match_data["Away Total Sets"] = int(away_completion_rate[1])
                
                if stat_box_label == "Average Play The Ball Speed":
                    play_the_ball_speeds = stats_box_i.find_all("p",{"class":play_the_ball_class})
                    match_data[f"Home {stat_box_label}"] = float(play_the_ball_speeds[0].text.strip("s"))
                    match_data[f"Away {stat_box_label}"] = float(play_the_ball_speeds[1].text.strip("s"))
                
                if stat_box_label == "Kick Defusal %":
                    kick_defusal = stats_box_i.find_all("p",{"class":"donut-chart-stat__value"})
                    match_data[f"Home {stat_box_label}"] = int(kick_defusal[0].text.strip("%"))
                    match_data[f"Away {stat_box_label}"] = int(kick_defusal[1].text.strip("%"))
                
                if stat_box_label == "Possession %":
                    match_data[f"Home {stat_box_label}"] = int(stats_box_i.find("p",{"class":home_possession_class}).text.strip("%"))
                    match_data[f"Away {stat_box_label}"] = int(stats_box_i.find("p",{"class":away_possession_class}).text.strip("%"))

        stat_box_label = stats_box_i.find("figcaption").text        
        if stat_box_label in attributes:
            if stat_box_label == "Average Set Distance":
                match_data[f"Home {stat_box_label}"] = float(stats_box_i.find("dd",{"class":home_stats_class}).text.strip())
                match_data[f"Away {stat_box_label}"] = float(stats_box_i.find("dd",{"class":away_stats_class}).text.strip())
            elif stat_box_label == "Time In Possession":
                match_data[f"Home {stat_box_label}"] = stats_box_i.find("dd",{"class":home_stats_class}).text.strip()
                match_data[f"Away {stat_box_label}"] = stats_box_i.find("dd",{"class":away_stats_class}).text.strip()
            else:
                match_data[f"Home {stat_box_label}"] = int(stats_box_i.find("dd",{"class":home_stats_class}).text.strip(","))
                match_data[f"Away {stat_box_label}"] = int(stats_box_i.find("dd",{"class":away_stats_class}).text.strip(","))

    return match_data
