from django.db import models



class Person(models.Model):
    last_name = models.CharField('Фамилия',
                                 max_length=60,
                                 null=True,
                                 blank=True
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
                                   )
    birth_date = models.DateTimeField('Дата рождения',
                                      blank=True,
                                      null=True)

    death_date = models.DateTimeField('Дата смерти, если была',
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
                               verbose_name= 'Отец',
                               related_name= 'father_name',
                               blank=True,
                               null=True,
                               on_delete=models.PROTECT)

    mother = models.ForeignKey('self',
                               verbose_name='Мать',
                               related_name='mother_name',
                               blank=True,
                               null=True,
                               on_delete=models.PROTECT,
                               )

    who_married = models.ForeignKey('self',
                               verbose_name='Муж/Жена',
                               related_name='married_name',
                               blank=True,
                               null=True,
                               on_delete=models.PROTECT,
                               )

    comment = models.TextField('Комментарии',
                                null=True,
                                blank=True,
                                    )

    mainPhoto = models.ImageField('Главное фото',
                                    upload_to='img/',
                                    default='work/Without photo.jpg',
                                )

    pers_photo = models.ManyToManyField('Photo',
                                        verbose_name='На фото',
                                        related_name='to_pers_photo',
                                        blank=True,
                                       )

    creating_date = models.DateTimeField(blank=True,
                                         null=True,
                                         auto_now_add=True,
                                         )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['last_name', 'first_name', 'birth_date'], name='unicue_person')
        ]

    def __str__(self):

        if self.middle_name is None:
            name = self.last_name + " " + self.first_name
        else:
            name = self.last_name + " " + self.first_name + " " + self.middle_name
        return name


class Photo(models.Model):
    photo = models.ImageField('Фото',
                              upload_to='img/',
                            null=True,
                            blank=True,
                                )
    comments = models.TextField('Комментарии',
                                null=True,
                                blank=True,
                                    )
    creating_date = models.DateTimeField(blank=True,
                                         null=True,
                                         auto_now_add=True,

                                         )

class Empty_person(Person):

    class Meta:
       managed=False

    def save(self, *args, **kwargs):
        pass


class Picture (models.Model):
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
    def __str__(self):
        return self.picture_name

#    def __str__(self):
#        return self.project_name


#    class Meta:
#        constraints = [
#            models.UniqueConstraint(fields=['project', 'people'], name='one_person_in_pr')
#        ]
