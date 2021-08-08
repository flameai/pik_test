from django.contrib.gis import admin
from main.models import *

# Register your models here.

admin.site.register(Zone, admin.GeoModelAdmin)