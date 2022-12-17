
import requests
from django.core.serializers import json
from django.http import HttpResponse
from rest_framework.request import Request

from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
import logging

from rest_framework.views import APIView as AV
from rest_framework.generics import RetrieveUpdateAPIView, get_object_or_404
# from .models import User, Users_likes, Posts
from Gen_tree.settings import RAW_CONFIG, MEDIA_ROOT
from gtree_db.models import Photo, Person

from .serializer import PhotoSerializer, PersonSerializer
from .classes import UserJSONRenderer, API_var
from .utils import json_response, error_json_response, _recovery_picture_from_bynaryfield, get_json_data, \
    person_sending, check_person_in_sent, send_request





def send_dataset(request):
    api_var = API_var()
    # sending photo
    photos_sending(api_var)
    #sending persons
    api_var.persons_set = set(Person.objects.all())
    while len(api_var.persons_set) > 0:
        person = api_var.persons_set.pop()
        _ = sending_person(person, api_var)

    return api_var.wrong_persons_record


def photos_sending(api_var:API_var):
    for photo in Photo.objects.all():
        data = PhotoSerializer(photo).data
        data['token'] = RAW_CONFIG['API']['token']
        json = UserJSONRenderer().render(data)

        response = send_request(json=json, ext='photos/')
        if response.status_code != 200:
            raise Exception
        json = response.json()
        if json['status']:
            print(f'got json {json["status"]} for {photo.the_photo}')
            if json['status'] == 'error':
                api_var.wrong_photo_records.append(photo)
            else:
                photo_dict = {json['data']['photo']: json['data']['id']}
                api_var.sent_photos.append(photo_dict)

    print(api_var.wrong_photo_records)

def sending_person(person: Person, api_var: API_var, check_married:bool = True):
    cur_context = {'photos': api_var.sent_photos, 'mother':  None,
                   'father': None, 'who_married': None}
    if not person.mother and not person.father:
        pass
    else:
        if person.mother:
            temp_person = check_person_in_sent(person.mother, api_var=api_var)
            if not temp_person:
               temp_person = sending_person(person.mother, api_var=api_var)
            cur_context.update({'mother': int(temp_person['id'])})
        if person.father:
            temp_person = check_person_in_sent(person.father, api_var=api_var)
            if not temp_person:
                temp_person = sending_person(person.father, api_var=api_var)
            cur_context.update({'father': int(temp_person['id'])})
    if person.who_married and check_married:
        temp_person = check_person_in_sent(person.who_married, api_var)
        if not temp_person:
            temp_person = sending_person(person.who_married, api_var=api_var, check_married=False)
        cur_context.update({'who_married': int(temp_person['id'])})

    json = (person_sending(person, context=cur_context)).json()
    if json['status']:
        print(f'got json {json["status"]} for {str(person)}')
    if json['status'] == 'error':
        api_var.wrong_persons_record.append(person)
    else:
        sent_person = {'id': json['data']['id'], 'person': person}
        api_var.sent_persons.add(sent_person)
        if person in api_var.persons_set:
            api_var.persons_set.remove(person)
    return sent_person


    # sending persons



class PhotoView(AV):
    def get(self, request):
        return HttpResponse('without get', status=status.HTTP_400_BAD_REQUEST)

    #       photos = Photo.objects.all()
    #       serializer = PhotoSerializer(photos, many=True)
    #       return Response({"photos": serializer.data})

    def post(self, request: Request):
        json_data = get_json_data(request=request, token=RAW_CONFIG['API']['token'])

        temp_the_photo = json_data['the_photo']
        temp_photo_file = json_data['photo_file'].encode('utf-8')
        my_the_photo = 'img' + temp_the_photo[temp_the_photo.rfind('/'):]
        temp_comments = json_data['comments']
        logging.debug(msg=my_the_photo)

        ans_0save1cant_save2already_exist = _recovery_picture_from_bynaryfield(b_string=temp_photo_file,
                                               file_path= str(MEDIA_ROOT) + '/' + my_the_photo,
                                                        )
        if ans_0save1cant_save2already_exist == 2 and Photo.objects.filter(the_photo__exact=my_the_photo).first():
            old_photo = Photo.objects.filter(the_photo__exact=my_the_photo).first()
            with open('logs.txt', 'r') as l:
                l.write(f'id: {old_photo.id}, photo: {old_photo.the_photo} \n')
            data = {"id": old_photo.id,
                    "photo": old_photo.the_photo,
                    }

        else:
            try:
                new_photo = Photo(the_photo=my_the_photo, photo_file=temp_photo_file, comments=temp_comments)
                new_photo.save()
            except Exception as exce:
                logging.error("Exception", exc_info=True)
                return error_json_response(http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                       message=f'ошибка сериализации, {exce.args}', )

            data = {"id": new_photo.id,
                "photo": temp_the_photo,
                }
        return json_response(data=data, json_status='ok')

class PersonView(AV):
        def get(self, request):
            return HttpResponse('without get', status=status.HTTP_400_BAD_REQUEST)
##
        def post(self, request: Request):
            json_data = get_json_data(request=request, token=RAW_CONFIG['API']['token'])
            _ = json_data.pop('token', None)
            temp_the_photo = json_data['mainPhoto']
            json_data['mainPhoto'] = None
            temp_photo_file = json_data['mainPhotofile'].encode('utf-8')
            my_the_photo = 'img' + temp_the_photo[temp_the_photo.rfind('/'):]
            logging.debug(msg=my_the_photo)
            file_path = str(MEDIA_ROOT) + '/' + my_the_photo
            path_or_exist_or_error = _recovery_picture_from_bynaryfield(
                b_string=temp_photo_file,
                file_path=file_path,
            )

            # json_data['path_to_file'] = file_path
            json_data['mainPhoto'] = file_path


            serializer = PersonSerializer(data=json_data)
            try:
                serializer.is_valid(raise_exception=True)
                serializer.validated_data
            except Exception as exce:
                logging.error("Exception", exc_info=True)
                return error_json_response(http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                           message=f'ошибка сериализации, {exce.args}', )

            curPerson = serializer.save()

            logging.debug(msg=f'{str(curPerson)} внесен')

            data = {"id": curPerson.id,
                    "person": str(curPerson),
                    }
            return json_response(data=data, json_status='ok')


"""
class PostCreation(AV):
    permission_classes = (IsAuthenticated,)
    def post (self, request):
        new_post = request.data.get('new_post')
        new_post['author_id'] = self.request.user.id

        serializer = PostSerializer (data=new_post)

        if serializer.is_valid(raise_exception=True):
            post_saved = serializer.save()
        return Response(
                        {'success': f"Post '{post_saved.theme}' created successfully"},
                        status=status.HTTP_201_CREATED
                        )





class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # метод GET
        # Здесь нечего валидировать или сохранять. Мы просто хотим, чтобы
        # сериализатор обрабатывал преобразования объекта User во что-то, что
        # можно привести к json и вернуть клиенту.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        # метод PATCH: в теле отправлять все с изменениями
        serializer_data = request.data.get('user', {})

        # Паттерн сериализации, валидирования и сохранения - то, о чем говорили
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)




class PostLike(AV):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        new_like = request.data.get('new_like')
        posts_id = new_like['posts_id']
        posts_author_id = Posts.objects.get(pk=posts_id).author_id
        if self.request.user.id == posts_author_id:
            return Response({'errors': "Author can't like hisown posts"},
                            status=status.HTTP_403_FORBIDDEN)
        new_like['user_id'] = self.request.user.id

        if Users_likes.objects.filter(posts_id__exact=posts_id,
                                      user__exact=self.request.user):
            return Response({'errors': "You've already like it"})
        serializer = PostlikeSerializer (data=new_like)

        if serializer.is_valid(raise_exception=True):
            try:
                _ = serializer.save()
            except Exception:
                msg = "Can't save data"
                raise exceptions.ValidationError(detail=msg)

            return Response(
              {'success': 'like was registrated'},
              status=status.HTTP_201_CREATED
        )


"""