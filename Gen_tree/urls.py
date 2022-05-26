# Gen_tree URL Configuration
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
# from upload_app.views import home_page
from django.views.generic import RedirectView

import gtree_db.view as gtv
from Gen_tree import settings

urlpatterns = [

    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view()),
    path('tree/', include('gtree_db.urls')),
    path('', gtv.main_page),
    path('favicon.ico', RedirectView.as_view(url='/media/work/favicon.ico')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)