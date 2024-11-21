from bs4 import BeautifulSoup
from selenium import webdriver
import time

def get_match_data(extension: str,attributes: list[str]) -> dict:
    # Setup the driver and get the match page source
    url = f"https://www.nrl.com{extension}"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(10)

    # Allow a maximum of 3 page requests before throwing an error
    for i in range(3):
        # Attempt to access page
        try:
            driver.get(url)
        except:
            driver.quit()
            continue

        page_source = driver.page_source
        driver.quit()
        
        time.sleep(1)
    
        # Parse the webpage source into a BeautifulSoup object
        soup = BeautifulSoup(page_source, "html.parser")

        # Get the team stats tile
        team_stats_box = soup.find_all("div",class_="u-spacing-pb-24 u-spacing-pt-16 u-width-100")

        # The bulk of the data will be under tiles utilising these classes
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
        
        # Initialise a dictionary object for match data to be held
        match_data = {}

        # Loop through the 
        for stats_box_i in team_stats_box:
            # Most data will be held in tiles utilising a h3 tag or a figcaption tag
            stat_box_label = stats_box_i.find("h3")

            if stat_box_label != None:
                stat_box_label = stat_box_label.text

                # if statements matching the tag label to an attribute    
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
                        match_data[f"Home {stat_box_label}"] = float(play_the_ball_speeds[0].text.strip().replace("s",""))
                        match_data[f"Away {stat_box_label}"] = float(play_the_ball_speeds[1].text.strip().replace("s",""))
                    
                    if stat_box_label == "Kick Defusal %":
                        kick_defusal = stats_box_i.find_all("p",{"class":"donut-chart-stat__value"})
                        match_data[f"Home {stat_box_label}"] = int(kick_defusal[0].text.strip().replace("%",""))
                        match_data[f"Away {stat_box_label}"] = int(kick_defusal[1].text.strip().replace("%",""))
                    
                    if stat_box_label == "Possession %":
                        match_data[f"Home {stat_box_label}"] = int(stats_box_i.find("p",{"class":home_possession_class}).text.strip().replace("%",""))
                        match_data[f"Away {stat_box_label}"] = int(stats_box_i.find("p",{"class":away_possession_class}).text.strip().replace("%",""))

            stat_box_label = stats_box_i.find("figcaption").text        
            if stat_box_label in attributes:
                if stat_box_label == "Average Set Distance":
                    match_data[f"Home {stat_box_label}"] = float(stats_box_i.find("dd",{"class":home_stats_class}).text.strip())
                    match_data[f"Away {stat_box_label}"] = float(stats_box_i.find("dd",{"class":away_stats_class}).text.strip())
                elif stat_box_label == "Time In Possession":
                    home_time = stats_box_i.find("dd",{"class":home_stats_class}).text.strip().split(":")
                    match_data[f"Home {stat_box_label}"] = int(home_time[0]) + (int(home_time[1]) / 60)
                    
                    away_time = stats_box_i.find("dd",{"class":away_stats_class}).text.strip().split(":")
                    match_data[f"Away {stat_box_label}"] = int(away_time[0]) + (int(away_time[1]) / 60)
                else:
                    match_data[f"Home {stat_box_label}"] = int(stats_box_i.find("dd",{"class":home_stats_class}).text.strip().replace(",",""))
                    match_data[f"Away {stat_box_label}"] = int(stats_box_i.find("dd",{"class":away_stats_class}).text.strip().replace(",",""))

        # Match data was read successfully, return match data
        return match_data
    
    # Page timed out 3 times
    return None
