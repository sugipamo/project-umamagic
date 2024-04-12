import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
from resources import data_manager

def main(driver, url):
    driver.get(url)
    data_manager.save("google.html", driver.page_source)
    data_manager.delete("google.html")