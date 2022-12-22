import base64
import logging
import os
import typing
import webbrowser

from rest_framework import status
import requests
from django.core.serializers import json
from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework.response import Response

from API.classes import UserJSONRenderer


from Gen_tree.settings import RAW_CONFIG
from gtree_db.models import Person

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


def json_response(data: typing.Any = None, status:int = 200, json_status: str = "ok") -> Response:
    if data is None:
        data = {}
    return Response(
        status=status,
        data= {
            "status": json_status,
            "data": data,
                 }
                         )


def error_json_response(
    http_status: int,
    status: str = "error",
    message: typing.Optional[str] = None,
    data: typing.Optional[dict] = None,
):
    if data is None:
        data = {}
    return json_response(
        json_status= 'error',
        status=http_status,
        data={
            "status": status,
            "message": str(message),
            "data": data,
        },
    )


def _recovery_picture_from_bynaryfield(b_string: bytes, file_path: str) -> str:
    if not os.path.exists(file_path):
        try:
            with open('temp31111111', 'wb') as ph:
                enfile = base64.b64decode(b_string)
                ph.write(enfile)
                ph.close()
                os.rename('temp31111111', file_path)
            return file_path
        except:
            logging.debug(msg=f"Can't save photo: {file_path}")
            return "error"
    else:
        return 'exist'

def get_json_data(request: Request, token: typing.Optional[str] = None) -> json:
    try:
        data = request.data
        logging.info('request.data', request.data)
        json_data = data["data"]
    except:
        return error_json_response(http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   message='не удалось извлечь data', data=data)
    if token:
        try:
            if json_data['token'] != token:
                raise exceptions.AuthenticationFailed(msg='Неподходящий токен')
        except:
            return error_json_response(http_status=status.HTTP_401_UNAUTHORIZED,
                                       message='неподходящий токен', )
    return json_data

def person_sending(person: Person, context: dict) -> Response:
    from API.serializer import PersonSerializer
    serializer = PersonSerializer(person, context=context)
    data = serializer.data
    data['token'] = RAW_CONFIG['API']['token']
    json = UserJSONRenderer().render(data)
    response = send_request(json=json, ext='persons/')
    if response.status_code == 500:
        try:
            with open('temp.html', 'w', encoding='utf-8') as t:
                text = str(response.text)
                t.write(text)
                t.close()
        except Exception as e:
            print(e)
        webbrowser.open_new_tab('file://' + os.path.realpath(t.name))
    return response

def check_person_in_sent(person: Person, api_var):
    for sent_person in api_var.sent_persons:
        if sent_person['person'] == person:
            return sent_person
    return None


def send_request(json: json, ext: str) -> Response:
    api_url = RAW_CONFIG['API']['url'] + ext
    api_token = RAW_CONFIG['API']['token']


    headers = {'token': api_token, 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br',
                      'User-Agent': 'My User Agent 1.0', 'Connection': 'keep-alive',
                      'Content-Type': 'application/json',
                   }
    print('sending request', api_url)
    response = requests.post(url=api_url, json=json, headers=headers)
    return response

def create_logs(string: str):
    with open('logs.txt', 'a') as l:
        l.write(str(string) + '\n')
