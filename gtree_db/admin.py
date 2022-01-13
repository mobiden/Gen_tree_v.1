from django.contrib import admin
from .models import Person, Photo, Picture, Arch_Photo

admin.site.register(Person)
admin.site.register(Photo)
admin.site.register(Arch_Photo)
admin.site.register(Picture)