from django.shortcuts import render
from django.views import View

from django.apps import apps
from django.urls import reverse

class IndexView(View):
    def get(self, request, *args, **kwargs):

        context = {}

        # 全てのアプリのapps.pyを呼び出す。
        apps_configs    = apps.get_app_configs()

        links   = []
        for apps_config in apps_configs:
            # name="index"があることを前提として実行しているので、念の為にtry文で実行する。
            try:
                dic = {}

                # TIPS: ここで reverse_lazy() だと、try文が終わった後に例外(存在しないURL名)が発動してしまう。
                dic["url"]      = reverse(f"{apps_config.name}:index")
                dic["name"]     = apps_config.verbose_name

                links.append(dic)
            except:
                continue

        context["links"]    = links

        return render(request, "home/index.html", context)

index   = IndexView.as_view()
