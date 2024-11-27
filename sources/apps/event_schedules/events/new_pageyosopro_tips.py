from apps.db_netkeiba_tips.models import HorseRacingTipParserForPageYosoPro
SCHEDULE_STR = "0,"

def main():
    HorseRacingTipParserForPageYosoPro.new_tips()
