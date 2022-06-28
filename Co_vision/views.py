import cv2, os
import numpy as np
from PIL import Image
from django.db.models import Count, Q

from Gen_tree.settings import BASE_DIR, MEDIA_ROOT
from gtree_db.models import Person, Photo

# Для детектирования лиц используем каскады Хаара
cascadePath = "Co_vision/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

# Для распознавания используем локальные бинарные шаблоны
recognizer = cv2.face.LBPHFaceRecognizer_create(1,8,8,8,123)
#recognizer = cv2.createLBPHFaceRecognizer(1,8,8,8,123)

def get_images():
    # Ищем все фотографии и записываем их в image_paths
    mainPhotos = Person.objects.exclude(
        Q(mainPhoto__icontains='Without') &
        Q(mainPhoto__icontains='photo') &
        Q(mainPhoto__icontains='.jpg')
                                            ).values('id', 'mainPhoto')
    the_photos = Photo.objects.annotate(
                    num_people=Count('to_pers_photo')).filter(
                            num_people__exact= 1).values(
                                    'the_photo', 'to_pers_photo__id')


    images = []
    labels = []

    for mainImage in mainPhotos:
        # Переводим изображение в черно-белый формат и приводим его к формату массива

        path = os.path.join(MEDIA_ROOT, mainImage['mainPhoto'])
       # path = str(BASE_DIR) + str("/media/") + mainImage['mainPhoto']
        gray = (Image.open(path)).convert('L')
        image = np.array(gray, 'uint8')
        # извлекаем номер человека, изображенного на фото
        subject_number = int(mainImage['id'])

        # Определяем области где есть лица
        faces = faceCascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 1:
            # Если лицо нашлось добавляем его в список images, а соответствующий ему номер в список labels
            for (x, y, w, h) in faces:
                images.append(image[y: y + h, x: x + w])
                labels.append(subject_number)
                # В окне показываем изображение
 #               cv2.imshow("", image[y: y + h, x: x + w])
 #               cv2.waitKey(100)

    for t_photo in the_photos:
        # Переводим изображение в черно-белый формат и приводим его к формату массива
        path = os.path.join(MEDIA_ROOT, t_photo['the_photo'])
        #path = str(BASE_DIR) + str("/media/") + t_photo['the_photo']
        gray = (Image.open(path)).convert('L')
        image = np.array(gray, 'uint8')
        # извлекаем номер человека, изображенного на фото
        subject_number = int(t_photo['to_pers_photo__id'])
        if len(faces) == 1:
            # Определяем области где есть лица
            faces = faceCascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            # Если лицо нашлось добавляем его в список images, а соответствующий ему номер в список labels
            for (x, y, w, h) in faces:
                images.append(image[y: y + h, x: x + w])
                labels.append(subject_number)
                # В окне показываем изображение
 #               cv2.imshow("", image[y: y + h, x: x + w])
 #               cv2.waitKey(100)

    return images, labels

def traininig_new_model(trained_model_path):
    # Получаем лица и соответствующие им номера
    images, labels = get_images()
    cv2.destroyAllWindows()
    # Обучаем программу распознавать лица
    recognizer.train(images, np.array(labels))
    recognizer.write(trained_model_path)


def check_photo(check_photo_path):
    # путь к уже натренированной модели
    trained_model_path = os.path.join(BASE_DIR, "Co_vision\\training_model.yml")

 #   if not os.path.exists(trained_model_path):
    traininig_new_model(trained_model_path)
 #   else:
 #       recognizer.read(trained_model_path)


    # Создаем список фотографий для распознавания
    image_paths = [check_photo_path]
    for image_path in image_paths:
        # Ищем лица на фотографиях
        gray = Image.open(image_path).convert('L')
        image = np.array(gray, 'uint8')
        faces = faceCascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        answer = {}
        for (x, y, w, h) in faces:
        # Если лица найдены, пытаемся распознать их
        # Функция  recognizer.predict в случае успешного распознавания возвращает номер
        # и параметр confidence, этот параметр указывает на уверенность алгоритма,
        # что это именно тот человек, чем он меньше, тем больше уверенность
            number_predicted, conf = recognizer.predict(image[y: y + h, x: x + w])
            if conf < 50 and number_predicted not in answer.keys():
                answer[number_predicted] = conf

 #           cv2.imshow("Recognizing Face", image[y: y + h, x: x + w])
 #           cv2.waitKey(1000)
    return answer.items()