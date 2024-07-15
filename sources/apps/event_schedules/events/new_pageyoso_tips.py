from apps.db_netkeiba_tips.models import HorseRacingTipParserForPageYoso
SCHEDULE_STR = "0,"

def main():
    HorseRacingTipParserForPageYoso.new_tips()
