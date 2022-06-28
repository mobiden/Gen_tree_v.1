from django.db import models
import base64
import os

# from Co_vision.views import traininig_new_model
#  from Gen_tree.settings import BASE_DIR


class Person(models.Model):
    last_name = models.CharField('Фамилия',
                                 max_length=60,
                                 null=True,
                                 blank=True,
                                 default='',
                                 )

    previous_last_name = models.CharField('Предыдущая фамилия, если была',
                                          max_length=60,
                                          null=True,
                                          blank=True,
                                          )

    first_name = models.CharField('Имя',
                                  max_length=45,
                                  null=True,

                                  )
    middle_name = models.CharField('Отчество',
                                   max_length=60,
                                   null=True,
                                   blank=True,
                                   default=''
                                   )
    birth_date = models.DateField('Дата рождения',
                                  blank=True,
                                  null=True)

    death_date = models.DateField('Дата смерти, если была',
                                  blank=True,
                                  null=True)

    SEX_CHOISES = [
        ('F', 'Женский'),
        ('M', 'Мужской'),
    ]
    sex = models.CharField('Пол',
                           max_length=1,
                           choices=SEX_CHOISES,
                           blank=True,
                           null=True,
                           )

    father = models.ForeignKey('self',
                               verbose_name='Отец',
                               related_name='father_name',
                               blank=True,
                               null=True,
                               on_delete=models.DO_NOTHING,
                               )

    mother = models.ForeignKey('self',
                               verbose_name='Мать',
                               related_name='mother_name',
                               blank=True,
                               null=True,
                               on_delete=models.DO_NOTHING,
                               )

    who_married = models.ForeignKey('self',
                                    verbose_name='Муж/Жена',
                                    related_name='married_name',
                                    blank=True,
                                    null=True,
                                    on_delete=models.DO_NOTHING,
                                    )

    comment = models.TextField('Комментарии',
                               null=True,
                               blank=True,
                               )

    mainPhoto = models.ImageField('Главное фото',
                                  upload_to='img/',
                                  default='work/Without photo.jpg',
                                  )
    mainPhotofile = models.BinaryField(max_length=6000000,
                                       blank=True,
                                       null=True,
                                       help_text='Максимум 5 мегабайт',
                                       editable=True,
                                       )

    pers_photo = models.ManyToManyField('Photo',
                                        verbose_name='На фото',
                                        related_name='to_pers_photo',
                                        blank=True,
                                        help_text='фото крупным планом',
                                        )

    creating_date = models.DateTimeField(blank=True,
                                         null=True,
                                         auto_now_add=True,
                                         )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['last_name', 'first_name', 'birth_date'], name='unicue_person')
        ]
        ordering = ['last_name', 'first_name', 'middle_name']

    def __str__(self):
        last_name = self.last_name
        if last_name is None:
            last_name = ''
        if self.middle_name is None:
            name = last_name + " " + self.first_name
        else:
            name = last_name + " " + self.first_name + " " + self.middle_name
        return name.strip()

    def save(self, *args, **kwargs):
        if self.mainPhoto:
            self.mainPhotofile = self.mainPhoto.file.read()

        super().save(*args, **kwargs)  # Call the "real" save() method.
        if self.who_married:
            second_half = self.who_married
            if not second_half.who_married:
                second_half.who_married = self
                second_half.save()
        # add who_married

    @classmethod
    def from_db(cls, db, field_names, values):

        instance = super().from_db(db, field_names, values)
        ph_file = instance.mainPhoto
        if not os.path.exists(ph_file.path) and instance.mainPhotofile:
            with open('temp11111111', 'wb') as ph:
                enfile = base64.b64encode(instance.mainPhotofile)
                ph.write(base64.b64decode(enfile))
                ph.close()
                os.rename('temp11111111', ph_file.path)

        return instance


class Photo(models.Model):
    the_photo = models.ImageField('Фото',
                                  upload_to='img/',
                                  null=True,
                                  blank=True,
                                  )
    photo_file = models.BinaryField(max_length=6000000,
                                    blank=True,
                                    null=True,
                                    help_text='Максимум 5 мегабайт',
                                    )

    comments = models.TextField('Комментарии',
                                null=True,
                                blank=True,
                                )
    creating_date = models.DateTimeField(blank=True,
                                         null=True,
                                         auto_now_add=True,
                                         )
    def __str__(self):
        return self.the_photo.path

    def save(self, *args, **kwargs):
        if self.the_photo:
  #          trained_model_path = os.path.join(BASE_DIR, "Co_vision\\training_model.yml")
   #         traininig_new_model(trained_model_path)
            self.photo_file = self.the_photo.file.read()
        super().save(*args, **kwargs)  # Call the "real" save() method.

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        ph_file = instance.the_photo
        if not os.path.exists(ph_file.path) and instance.photo_file:
            with open('temp21111111', 'wb') as ph:
                enfile = base64.b64encode(instance.photo_file)
                ph.write(base64.b64decode(enfile))
                ph.close()
                os.rename('temp21111111', ph_file.path)
        return instance


class Empty_person(Person):
    class Meta:
        managed = False

    def save(self, *args, **kwargs):
        pass


class Picture(models.Model):
    picture_name = models.CharField('Имя служебных картинок',
                                    max_length=20,
                                    primary_key=True,
                                    unique=True,
                                    )
    picture = models.ImageField('Служебные картинки',
                                upload_to='img/work/',
                                null=True,
                                blank=True,
                                )
    picturefile = models.BinaryField(max_length=6000000,
                                     blank=True,
                                     null=True,
                                     help_text='Максимум 5 мегабайт',
                                     )

    def __str__(self):
        return self.picture_name

    def save(self, *args, **kwargs):
        if self.picture:
            self.picturefile = self.picture.file.read()
        super().save(*args, **kwargs)  # Call the "real" save() method.

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        ph_file = instance.picture
        if not os.path.exists(ph_file.path) and instance.picturefile:
            with open('temp31111111', 'wb') as ph:
                enfile = base64.b64encode(instance.picturefile)
                ph.write(base64.b64decode(enfile))
                ph.close()
                os.rename('temp31111111', ph_file.path)

#    class Meta:
#        constraints = [
#            models.UniqueConstraint(fields=['project', 'people'], name='one_person_in_pr')
#        ]
