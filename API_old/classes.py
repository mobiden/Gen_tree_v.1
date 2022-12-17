

from rest_framework.renderers import JSONRenderer


class UserJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None, status = 'ok') -> JSONRenderer:
        # Если представление выдает ошибку (например, пользователь не может
        # быть аутентифицирован), data будет содержать ключ error. Мы хотим,
        # чтобы стандартный JSONRenderer обрабатывал такие ошибки, поэтому
        # такой случай необходимо проверить.
        errors = data.get('errors', None)

        # Если мы получим ключ token как часть ответа, это будет байтовый
        # объект. Байтовые объекты плохо сериализуются, поэтому нам нужно
        # декодировать их перед рендерингом объекта User.
        token = data.get('token', None)

        if errors is not None:
            # Позволим стандартному JSONRenderer обрабатывать ошибку.
            return super(UserJSONRenderer, self).render(data)

        if token is not None and isinstance(token, bytes):
            # Как говорится выше, декодирует token если он имеет тип bytes.
            data['token'] = token.encode('utf-8').decode('utf-8')

        # Наконец, мы можем отобразить наши данные в простанстве имен 'user'.
        # return json.dumps({'status': status, 'data': data})
        return {'status': status, 'data': data}



class API_var():
    def __init__(self):
        self.wrong_photo_records: list = []
        self.wrong_persons_record: list = []
        self.sent_photos: list = []
        self.sent_persons: set = set()
        self.persons_set: set = set()
