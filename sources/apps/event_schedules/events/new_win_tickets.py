from apps.db_netkeiba_tickets.models import HorseRacingTicketParser
SCHEDULE_STR = "3600,"

def main():
    HorseRacingTicketParser.new_win_tickets()
