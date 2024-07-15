from apps.web_netkeiba_pagesources.models import Pages
SCHEDULE_STR = "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,360,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2600,"

def main():
    models = Pages.PageClasses
    models = [m for m in models if not m.need_login]
    models.sort(key=lambda m: m.objects.all().count())
    models[0].new_page()
