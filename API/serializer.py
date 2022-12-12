from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.relations import StringRelatedField

from gtree_db.models import SEX_CHOISES, Photo, Person, Picture
import base64


class Bytes_to_Str_Field(serializers.Field):
    def to_representation(self, value):
        return base64.b64encode(value).decode()

    def to_internal_value(self, data:str):
        return data.encode('utf-8')

class PhotoSerializer(serializers.ModelSerializer):
    photo_file = Bytes_to_Str_Field()
    class Meta:
        model = Photo
        fields = ('the_photo', 'photo_file', 'comments', )

        def create(self, validated_data):
            return Photo.objects.create(**validated_data)


class Int_to_Person(serializers.IntegerField):
    def to_internal_value(self, data:int):
        return Person.objects.get(pk= data)


class Int_to_Photo(serializers.Field):
    def to_representation(self, value: Photo) -> int:
        name = value.the_photo
        name = name[name.rfind('/'):]
        photo_dict = self.context['photo_dict']
        id = photo_dict[name]
        return id

    def to_internal_value(self, data: int):
        return Photo.objects.get(pk=data)

class Int_to_Photo_class(serializers.Serializer):
    photo = Int_to_Photo()


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        mother = Int_to_Person(required=False)
        father = Int_to_Person(required=False)
        who_married = Int_to_Person(required=False)
        pers_photo = Int_to_Photo_class(many=True, required=False)
        mainPhoto = Bytes_to_Str_Field(required=False)
        model = Person
        fields = ('last_name', 'previous_last_name', 'first_name',
                  'middle_name', 'birth_date', 'death_date',
                  'sex', 'comment', 'mother', 'father', 'who_married'
                  'mainPhoto', 'mainPhotofile','pers_photo',)

    def create(self, validated_data):
        from API.utils import _recovery_picture_from_bynaryfield
        pers_photo_data = validated_data.pop('pers_photo')
        if validated_data('mainPhotofile'):
            _ = _recovery_picture_from_bynaryfield(
                b_string= validated_data('mainPhotofile'),
                file_path= 'img' + validated_data('mainPhoto')[validated_data('mainPhoto').rfind('/'):]
            )
        person = Person.objects.create(**validated_data)

        for p_photo in pers_photo_data:
            person.pers_photo.update(Photo.objects.get(pk=p_photo))
        return person

    def to_representation(self, instance:Person):
        if self.context['mother']:
            instance.mother = None
        if self.context['father']:
            instance.father = None
        if self.context['who_married']:
            instance.who_married = None

        representation = super().to_representation(self, instance)
        if self.context['mother']:
            representation['mother'] = self.context['mother']
        if self.context['father']:
            representation['father'] = self.context['father']
        if self.context['mother']:
            representation['who_married'] = self.context['who_married']
        return representation


"""
class PostlikeSerializer(serializers.Serializer):
    posts_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    likes = serializers.CharField(max_length=1)

    def create(self, validated_data):
        return Users_likes.objects.create(**validated_data)



class RegistrationSerializer(serializers.ModelSerializer):
   # Сериализация регистрации пользователя и создания нового. 

    # Убедитесь, что пароль содержит не менее 8 символов, не более 128,
    # и так же что он не может быть прочитан клиентской стороной
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    # Клиентская сторона не должна иметь возможность отправлять токен вместе с
    # запросом на регистрацию. Сделаем его доступным только на чтение.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        # Перечислить все поля, которые могут быть включены в запрос
        # или ответ, включая поля, явно указанные выше.
        fields = ['email', 'username', 'password', 'token']

    def create(self, validated_data):
        # Использовать метод create_user, который мы
        # написали ранее, для создания нового пользователя.
        return User.objects.create_user(**validated_data)



class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # В методе validate мы убеждаемся, что текущий экземпляр
        # LoginSerializer значение valid. В случае входа пользователя в систему
        # это означает подтверждение того, что присутствуют адрес электронной
        # почты и то, что эта комбинация соответствует одному из пользователей.
        email = data.get('email', None)
        password = data.get('password', None)

        # Вызвать исключение, если не предоставлена почта.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
                                                )
        # Вызвать исключение, если не предоставлен пароль.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
                                                )
        # Метод authenticate предоставляется Django и выполняет проверку, что
        # предоставленные почта и пароль соответствуют какому-то пользователю в
        # нашей базе данных. Мы передаем email как username, так как в модели
        # пользователя USERNAME_FIELD = email.
        user = authenticate(username=email, password=password)

        # Если пользователь с данными почтой/паролем не найден, то authenticate
        # вернет None. Возбудить исключение в таком случае.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )
        # Django предоставляет флаг is_active для модели User. Его цель
        # сообщить, был ли пользователь деактивирован или заблокирован.
        # Проверить стоит, вызвать исключение в случае True.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
                                                )
        # Метод validate должен возвращать словать проверенных данных. Это
        # данные, которые передются в т.ч. в методы create и update.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
                }




class UserSerializer(serializers.ModelSerializer):
    # Ощуществляет сериализацию и десериализацию объектов User.

    # Пароль должен содержать от 8 до 128 символов. Это стандартное правило. Мы
    # могли бы переопределить это по-своему, но это создаст лишнюю работу для
    # нас, не добавляя реальных преимуществ, потому оставим все как есть.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token',)

        # Параметр read_only_fields является альтернативой явному указанию поля
        # с помощью read_only = True, как мы это делали для пароля выше.
        # Причина, по которой мы хотим использовать здесь 'read_only_fields'
        # состоит в том, что нам не нужно ничего указывать о поле. В поле
        # пароля требуются свойства min_length и max_length,
        # но это не относится к полю токена.
        read_only_fields = ('token',)

    def update(self, instance, validated_data):
       # Выполняет обновление User.

        # В отличие от других полей, пароли не следует обрабатывать с помощью
        # setattr. Django предоставляет функцию, которая обрабатывает пароли
        # хешированием и 'солением'. Это означает, что нам нужно удалить поле
        # пароля из словаря 'validated_data' перед его использованием далее.
        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            # Для ключей, оставшихся в validated_data мы устанавливаем значения
            # в текущий экземпляр User по одному.
            setattr(instance, key, value)

        if password is not None:
            # 'set_password()' решает все вопросы, связанные с безопасностью
            # при обновлении пароля, потому нам не нужно беспокоиться об этом.
            instance.set_password(password)

        # После того, как все было обновлено, мы должны сохранить наш экземпляр
        # User. Стоит отметить, что set_password() не сохраняет модель.
        instance.save()

        return instance
        """
