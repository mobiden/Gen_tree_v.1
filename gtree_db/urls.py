from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import path
import gtree_db.views as gtv

urlpatterns = [
    path('', gtv.main_page, name='main_page'),
    path('family_tree/', gtv.family_tree, name='family_tree'),
    path('family_tree/<pk>/', gtv.fam_tree_schema, name='fam_tree_schema'),
    path('person/create/', gtv.Create_person.as_view(), name='create_person'),
    path('person/list/', gtv.List_of_persons.as_view(), name='persons_list'),
    path('person/get/<pk>/', gtv.detailed_person, name='detailed_person'),
    path('person/delete/<pk>/', gtv.Delete_person.as_view(), name='delete_person'),
    path('person/change/<pk>', gtv.Change_person.as_view(), name='change_person'),

    path('photo/add/', gtv.Add_photo.as_view(), name='add_photo'),
    path('photo/list/', gtv.Photo_list.as_view(), name='photo_list'),
    path('photo/list/<pk>/', gtv.Photo_list.as_view(), name='photo_list_id'),
    path('photo/detail/<pk>/', gtv.photo_detailed, name='photo_detailed'),
]