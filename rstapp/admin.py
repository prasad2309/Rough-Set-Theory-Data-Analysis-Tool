from django.contrib import admin
from .models import stability_index
from .models import dates
from .models import threshold
from .models import last_outputs

# Register your models here.
admin.site.register(stability_index)
admin.site.register(dates)
admin.site.register(threshold)
admin.site.register(last_outputs)
