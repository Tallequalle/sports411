import time, random, os, zipfile, io, tempfile, sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from driverium import Driverium
from fake_useragent import UserAgent
from apscheduler.schedulers.background import BackgroundScheduler

USER_AGENT = UserAgent(browsers=["Chrome"], platforms=["desktop"])

SPORTS = ["SOCCER", "BASKETBALL"]

def initialize_driver() -> webdriver.Chrome:
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument("--no-sandbox")
    driver_options.add_argument("--headless=new")
    driver_options.add_argument("--disable-blink-features=AutomationControlled") 
    driver_options.add_experimental_option("useAutomationExtension", False)
    driver_options.add_argument(f"--user-agent={USER_AGENT.random}")
    driver_options.add_argument("--blink-settings=imagesEnabled=false")
    driver_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    driver_options.add_argument("--use-gl=desktop")
    driver_options.add_argument("--no-default-browser-check")
    driver_options.add_argument("--no-first-run")
    driver_options.add_argument("--lang=uk-UA")
    driver_options.add_argument("--log-level=3")

    driver_options.add_argument("--disable-background-networking")
    driver_options.add_argument("--disable-background-timer-throttling")
    driver_options.add_argument("--disable-software-rasterizer")
    driver_options.add_argument("--disable-backgrounding-occluded-windows")
    driver_options.add_argument("--disable-client-side-phishing-detection")
    driver_options.add_argument("--disable-hang-monitor")
    driver_options.add_argument("--disable-dev-shm-usage")
    driver_options.add_argument("--disable-popup-blocking")
    driver_options.add_argument("--disable-webgl")
    driver_options.add_argument("--disable-webrtc")
    driver_options.add_argument("--disable-logging")
    driver_options.add_argument("--disable-gpu")

    with open(f"{os.path.abspath("data")}/background.js", "r", encoding="utf-8") as file:
        js_content = file.read()
    
    js_content = js_content.replace("IP", "179.60.183.245").replace("PORT", "50100").replace("USERNAME", "Selredpioneercom").replace("PASSWORD", "R4g8RtB")
    
    in_memory_zip = io.BytesIO()
    
    with zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("background.js", js_content)
        
        with open(f"{os.path.abspath("data")}/manifest.json", "r", encoding="utf-8") as manifest_file:
            manifest_content = manifest_file.read()
            
        zip_file.writestr("manifest.json", manifest_content)

    in_memory_zip.seek(0)
    
    extension = in_memory_zip.getvalue()

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
        temp_file.write(extension)
        temp_file_path = temp_file.name
    
    driver_options.add_extension(temp_file_path)

    service = Service(Driverium().get_driver())

    driver = webdriver.Chrome(service=service, options=driver_options)
    
    os.unlink(temp_file_path)

    driver.set_page_load_timeout(80)
    driver.set_script_timeout(80)

    driver.maximize_window()

    return driver

def main():
    connection = sqlite3.connect("sport.db")
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS games (id TEXT, status TEXT, visitor TEXT, home TEXT, draw TEXT, derivates TEXT, visitor_money TEXT, visitor_money_red BOOLEAN, home_money TEXT, home_money_red BOOLEAN, draw_money TEXT, draw_money_red BOOLEAN, visitor_spread TEXT, visitor_spread_red BOLEAN, home_spread TEXT, home_spread_red BOOLEAN, draw_spread TEXT, draw_spread_red BOOLEAN, visitor_total TEXT, visitor_total_red BOOLEAN, home_total TEXT, home_total_red BOOLEAN, draw_total TEXT, draw_total_red BOOLEAN)")

    cursor.close()
    connection.close()

    driver = initialize_driver()

    driver.get("https://be.sports411.ag/en/sports/")

    time.sleep(random.uniform(8, 16))

    if driver.find_elements(By.CLASS_NAME, "input-group"):
        driver.find_element(By.ID, "account").send_keys("6492")

        time.sleep(random.uniform(1.6, 4))

        driver.find_element(By.ID, "password").send_keys("13T5o7kJ")

        time.sleep(random.uniform(1.6, 4))

        driver.find_element(By.CLASS_NAME, "login-enter").click()

        time.sleep(random.uniform(1.6, 4))

    WebDriverWait(driver, 16).until(expected_conditions.presence_of_element_located((By.ID, "c-cont-entry")))

    scheduler = BackgroundScheduler()

    scheduler.add_job(parse, "interval", seconds=5, args=(driver,))

    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        driver.close()
        driver.quit()
        scheduler.shutdown()

def parse(driver:webdriver.Chrome):
    data = {}

    current = [game.find_element(By.TAG_NAME, "a").get_attribute("cat") for game in driver.find_element(By.ID, "c-cont-entry").find_elements(By.TAG_NAME, "li")]

    for sport in SPORTS:
        if sport in current:
            driver.find_element(By.ID, "c-cont-entry").find_element(By.XPATH, f'.//a[@cat="{sport}"]').click()

            time.sleep(1.6)

            for game in driver.find_elements(By.CLASS_NAME, "live-game"):
                game_id = game.get_attribute("id")

                status = game.find_element(By.CLASS_NAME, "live-status").get_attribute("innerText").strip()

                visitor = game.find_element(By.CLASS_NAME, "visitor").get_attribute("innerText").strip()
                home = game.find_element(By.CLASS_NAME, "home").get_attribute("innerText").strip()
                draw = game.find_element(By.CLASS_NAME, "draw").get_attribute("innerText").strip() if game.find_elements(By.CLASS_NAME, "draw") else None

                if game.find_elements(By.CLASS_NAME, "derivates-badge"):
                    derivates = game.find_element(By.CLASS_NAME, "derivates-badge").get_attribute("innerText").strip()
                else:
                    derivates = None

                visitor_money = game.find_element(By.CLASS_NAME, "mline-1").get_attribute("innerText").strip()
                visitor_money_red = True if game.find_element(By.CLASS_NAME, "mline-1").find_elements(By.CLASS_NAME, "changed-odd") else False
                home_money = game.find_element(By.CLASS_NAME, "mline-2").get_attribute("innerText").strip()
                home_money_red = True if game.find_element(By.CLASS_NAME, "mline-2").find_elements(By.CLASS_NAME, "changed-odd") else False
                draw_money = game.find_element(By.CLASS_NAME, "mline-X").get_attribute("innerText").strip() if draw else None
                draw_money_red = (True if game.find_element(By.CLASS_NAME, "mline-X").find_elements(By.CLASS_NAME, "changed-odd") else False) if draw else None

                if len(game.find_elements(By.CLASS_NAME, "hdp")) == 3:
                    visitor_spread, home_spread, draw_spread = game.find_elements(By.CLASS_NAME, "hdp")

                    draw_spread_red = True if draw_spread.find_elements(By.CLASS_NAME, "changed-odd") else False
                    draw_spread = draw_spread.get_attribute("innerText").strip().replace("\n", " ")
                else:
                    visitor_spread, home_spread = game.find_elements(By.CLASS_NAME, "hdp")
                    draw_spread = draw_spread_red = None
                visitor_spread_red = True if visitor_spread.find_elements(By.CLASS_NAME, "changed-odd") else False
                visitor_spread = visitor_spread.get_attribute("innerText").strip().replace("\n", " ")
                home_spread_red = True if home_spread.find_elements(By.CLASS_NAME, "changed-odd") else False
                home_spread = home_spread.get_attribute("innerText").strip().replace("\n", " ")

                if len(game.find_elements(By.CLASS_NAME, "ou")) == 3:
                    visitor_total, home_total, draw_total = game.find_elements(By.CLASS_NAME, "ou")

                    draw_total_red = True if draw_total.find_elements(By.CLASS_NAME, "changed-odd") else False
                    draw_total = draw_total.get_attribute("innerText").strip().replace("\n", " ")
                else:
                    visitor_total, home_total = game.find_elements(By.CLASS_NAME, "ou")
                    draw_total = draw_total_red = None
                visitor_total_red = True if visitor_total.find_elements(By.CLASS_NAME, "changed-odd") else False
                visitor_total = visitor_total.get_attribute("innerText").strip().replace("\n", " ")
                home_total_red = True if home_total.find_elements(By.CLASS_NAME, "changed-odd") else False
                home_total = home_total.get_attribute("innerText").strip().replace("\n", " ")

                data[game_id] = {"status":status, "visitor":visitor, "home":home, "draw":draw, "derivates":derivates, "visitor_money":visitor_money, "visitor_money_red":visitor_money_red, "home_money":home_money, "home_money_red":home_money_red, "draw_money":draw_money, "draw_money_red":draw_money_red, "visitor_spread":visitor_spread, "visitor_spread_red":visitor_spread_red, "home_spread":home_spread, "home_spread_red":home_spread_red, "draw_spread":draw_spread, "draw_spread_red":draw_spread_red, "visitor_total":visitor_total, "visitor_total_red":visitor_total_red, "home_total":home_total, "home_total_red":home_total_red, "draw_total":draw_total, "draw_total_red":draw_total_red}
        
    connection = sqlite3.connect("sport.db")
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM games")

    current = [item[0] for item in cursor.fetchall()]

    for key, value in data.items():
        if key in current:
            cursor.execute("UPDATE games SET status = ?, visitor = ?, home = ?, draw = ?, derivates = ?, visitor_money = ?, visitor_money_red = ?, home_money = ?, home_money_red = ?, draw_money = ?, draw_money_red = ?, visitor_spread = ?, visitor_spread_red = ?, home_spread = ?, home_spread_red = ?, draw_spread = ?, draw_spread_red = ?, visitor_total = ?, visitor_total_red = ?, home_total = ?, home_total_red = ?, draw_total = ?, draw_total_red = ? WHERE id = ?", (value["status"], value["visitor"], value["home"], value["draw"], value["derivates"], value["visitor_money"], value["visitor_money_red"], value["home_money"], value["home_money_red"], value["draw_money"], value["draw_money_red"], value["visitor_spread"], value["visitor_spread_red"], value["home_spread"], value["home_spread_red"], value["draw_spread"], value["draw_spread_red"], value["visitor_total"], value["visitor_total_red"], value["home_total"], value["home_total_red"], value["draw_total"], value["draw_total_red"], key))
        else:
            cursor.execute("INSERT INTO games (id, status, visitor, home, draw, derivates, visitor_money, visitor_money_red, home_money, home_money_red, draw_money, draw_money_red, visitor_spread, visitor_spread_red, home_spread, home_spread_red, draw_spread, draw_spread_red, visitor_total, visitor_total_red, home_total, home_total_red, draw_total, draw_total_red) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (key, value["status"], value["visitor"], value["home"], value["draw"], value["derivates"], value["visitor_money"], value["visitor_money_red"], value["home_money"], value["home_money_red"], value["draw_money"], value["draw_money_red"], value["visitor_spread"], value["visitor_spread_red"], value["home_spread"], value["home_spread_red"], value["draw_spread"], value["draw_spread_red"], value["visitor_total"], value["visitor_total_red"], value["home_total"], value["home_total_red"], value["draw_total"], value["draw_total_red"]))
    
    connection.commit()

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()