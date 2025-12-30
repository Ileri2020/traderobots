from django.contrib import admin
from .models import TradingAccount, Robot, AppVisit, Profile

admin.site.register(Profile)
admin.site.register(TradingAccount)
admin.site.register(Robot)
admin.site.register(AppVisit)
