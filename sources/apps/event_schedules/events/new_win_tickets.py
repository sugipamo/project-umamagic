from apps.db_netkeiba_tickets.models import HorseRacingTicketParser
SCHEDULE_STR = "0,"

def main():
    HorseRacingTicketParser.new_win_tickets()
