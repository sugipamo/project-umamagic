import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
from resources import data_manager

def main(driver, url, htmlpath):
    driver.get(url)
    data_manager.save(htmlpath, driver.page_source)