from apps.db_netkeiba_tips.models import HorseRacingTipParserForPageYosoCp
SCHEDULE_STR = "0,"

def main():
    HorseRacingTipParserForPageYosoCp.new_tips()
