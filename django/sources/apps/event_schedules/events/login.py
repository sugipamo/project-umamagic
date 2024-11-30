from apps.web_controller.models import LoginForScraping 
SCHEDULE_STR = "1,"

def main():
    models = LoginForScraping.objects.all()
    models = [m for m in models if not m.loggined]
    if not models:
        return
    models[0].login()
