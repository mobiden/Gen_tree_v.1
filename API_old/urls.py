from django.urls import path
from .views import send_dataset, PhotoView, PersonView

urlpatterns = [
    path('send_dataset/', send_dataset, name='send_dataset'),
    path('photos/', PhotoView.as_view(), name='api_photos_view'),
    path('persons/', PersonView.as_view(), name='api_persons_view')


#    path('user/login/', LoginUser.as_view(), name='login'),
#    path('post/creation/', PostCreation.as_view(), name="post_creation"),
                 ]