from apps.web_netkeiba_pagesources.models import Page
SCHEDULE_STR = "3600,"

def main():
    Page.extract_raceids()
