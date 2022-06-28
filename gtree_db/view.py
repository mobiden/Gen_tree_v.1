import os
from itertools import zip_longest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.db.models import Count, Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView

from PIL import Image, ImageDraw, ImageColor

from Co_vision.views import check_photo
from Gen_tree.settings import BASE_DIR, MEDIA_ROOT
from gtree_db.models import Person, Photo, Empty_person



@login_required
def main_page(request):
    return render(request, 'main.html')

@login_required
def family_tree(request):
    all_person = Person.objects.all()
    return render(request, "family_list.html", context={
        'all_person': sorted_person_list(all_person),
   })

def check_person(person):
    if person:
        return person
    else:
        null_person = Empty_person (last_name = "не известно",
                                    first_name='',
                                    middle_name='',
                                    mainPhoto = '/work/Without photo.jpg')
        return null_person

def sorted_person_list(mylist):
    return sorted(sorted(mylist, key=lambda x: x.first_name), key=lambda y: y.last_name)

def get_person_or_default (person_id, pk):
    if person_id:
        return person_id
    else:
        return pk

def persons_in_center (persons, married):
    if len(persons) > 8:
# обрезает список детей до 8, чтобы поместились в одну строку
        persons = persons[:8]
    amount = len(persons)

    first = int((8 - amount) / 2) + 1
    second = 8 - amount - first
    first_list = []
    for i in range(first):
        first_list += [None]
    second_list = []
    for i in range(second):
        second_list +=[None]
    first_list += persons
    first_list += second_list
    return first_list
#    else:
 #       if amount > 4:
 #           second = 8 - amount
 #           first_list = []
 #           second_list = []
 #           for i in range(second):
 #               second_list += [None]
 #           first_list += persons
 #           first_list += second_list
 #       else:
 #           first = int((3 - amount) / 2) + 1
 #           second = 4 - amount - first
 #           first_list = []
 #           for i in range(first):
 #               first_list += [None]
 #           second_list = []
 #           for i in range(second):
 #               second_list += [None]
 #           first_list += persons
 #           first_list += second_list

    return first_list


def arrows_create(number, path):
    max_num = int(max(set(number)))
    up_end = list(number.split('-')[0])
    down_end = list(number.split('-')[1])
    cell_size = 180
    width = max_num * cell_size
    height = 20
    line_level = height - 15
    line_width = 4 - 1
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    startpoint = -1
    endpoint = 0
    for up_line in up_end:
        up_line = int(up_line)
        x = int((up_line - 0.5) * cell_size)
        y1 = 0
        y2 = line_level
        draw.rectangle((x, y1, x + line_width, y2), fill='green')
        if startpoint < 0 or startpoint > x:
            startpoint = x
        if endpoint < x:
            endpoint = x

    for down_line in down_end:
        down_line = int(down_line)
        x = int((down_line - 0.5) * cell_size)
        y1 = height
        y2 = line_level
        draw.rectangle((x, y1, x + line_width, y2), fill='green')
        if startpoint < 0 or startpoint > x:
            startpoint = x
        if endpoint < x:
            endpoint = x
        draw.polygon([(x, y1), (x + line_width, y1), (x - 5, y1 - 5), (x + line_width + 5, y1 - 5)], fill='green')

    draw.rectangle((startpoint, line_level, endpoint + line_width, line_level + line_width), fill='green')
    try:
        image.save(os.path.abspath(path))
    except:
        print("Image can't save")

def get_arrow(number):
    line_wid = int(max(set(number)))
        # вставить создание стрелки
    if number == '100':
        # white block
        path_width = ("/media/work/transp.png", 1)
    else:
        path = str("/media/work/" + str(number) + "arrow.png")

 #       if not os.path.exists(str(BASE_DIR) + str("\\media\\work\\" + str(number) + "arrow.png")):
        arrows_create(number, (str(BASE_DIR) + str("/media/work/" + str(number) + "arrow.png")))
        path_width = (path, line_wid)

    return path_width


def get_arrows_lines(persons_line):
    if len(persons_line[0]) == 8:
        grandparents_arrows = [get_arrow('100'), get_arrow('13-2'), get_arrow('100'), get_arrow('13-2'),]
    else:
        grandparents_arrows = [get_arrow('13-2'), get_arrow('13-2'), ]

    if len(persons_line[1]) > 4:
        parents_arrows = [get_arrow('100'), get_arrow('100'), get_arrow('15-3'), get_arrow('100'), ]
#   else:
#        parents_arrows = [get_arrow('100'), get_arrow('13-2'), ]

    row1 = []
    row2 = []

    children_arrows = []
    for person_num in range(len(persons_line[2])):
        if persons_line[2][person_num] is not None:
            row1 += [person_num + 1]
        else:
            row1 += [0]

    for person_num in range(len(persons_line[3])):
        if persons_line[3][person_num] is not None:
            row2 += [person_num + 1]
        else:
            row2 += [0]

    num_arrow1 = num_arrow2 = ''
    empty_block = 0
    end_of_empty_block = False
    for i in range(len(persons_line[3])):
        if row2[i] == 0 and row1[i] == 0:
            if not end_of_empty_block:
                children_arrows += [get_arrow('100')]
                empty_block += 1
        else:
            end_of_empty_block = True
            if row1[i] != 0:
                num_arrow1 += str(i - empty_block + 1)
            if row2[i] != 0:
                num_arrow2 += str(i - empty_block + 1)
    if num_arrow2 == '':
        children_arrows = None
    else:
        whole_string = num_arrow1 + '-' + num_arrow2
        children_arrows += [get_arrow(whole_string)]
    return [grandparents_arrows, parents_arrows, children_arrows]



def num_of_children (cur_person):
    return Person.objects.filter(Q(father=cur_person) | Q(mother=cur_person))

@login_required
def fam_tree_schema (request, pk):
    pk = int(pk)
    try:
        main_person = Person.objects.get(pk=pk)
        marr_person = None
        if main_person.who_married:
            marr_person = main_person.who_married

        children_of_person = (Person.objects.filter(Q(mother=main_person)|
                                                                Q(father=main_person)))


        married = False
        if marr_person:
            married = True
        children_of_person = persons_in_center(children_of_person, married)



        main_father = check_person(main_person.father)
        main_mother = check_person(main_person.mother)
        parents = [None, None, main_father, None, None, None, main_mother, None]


        f_grandmother_main = check_person(main_father.mother)
        f_grandfather_main = check_person(main_father.father)
        m_grandfather_main = check_person(main_mother.father)
        m_grandmother_main = check_person(main_mother.mother)

        if main_person.who_married:
#            f_grandfather_marr = check_person(marr_father.father)
#            f_grandmother_marr = check_person(marr_father.mother)
#            m_grandfather_marr = check_person(marr_mother.father)
#            m_grandmother_marr = check_person(marr_mother.mother)
            grandparents = [None, f_grandmother_main, None, f_grandfather_main,
                            None, m_grandfather_main, None, m_grandmother_main,
#                            f_grandfather_marr, f_grandmother_marr,
#                            m_grandfather_marr, m_grandmother_marr,
                            ]


        else:
            grandparents = [None, f_grandmother_main, None, f_grandfather_main,
                            None, m_grandfather_main, None, m_grandmother_main,
                        ]



        cur_fam = [None, None, None, None, main_person, None, marr_person, None]

    except Person.DoesNotExist:
        # change raise
        raise Http404

    lines = [grandparents, parents, cur_fam, children_of_person, ]
    arrow_lines = get_arrows_lines(lines)

    mix_lines = zip_longest(lines, arrow_lines)

    return render(request, "Tree/fam_tree_schema.html", context={
        'mix_lines':mix_lines, 'id':pk,
    })



def moving_by_arrows (request, pk, arrow):
    # id = request.GET.get('id')
    # num_of_arrow = request.GET.get('num_of_arrow')
    cur_person = Person.objects.get(pk=pk)
    new_pk = ""
    arrow = int(arrow)
    if arrow == 1:
        # left
        pass
    elif arrow == 2:
        # up
        if cur_person.sex == 'M':
            new_pk = get_person_or_default(cur_person.father_id, get_person_or_default(cur_person.mother_id, pk))
        else:
            new_pk = get_person_or_default(cur_person.mother_id, get_person_or_default (cur_person.father_id, pk))

    elif arrow == 3:
        # right
        new_pk = get_person_or_default(cur_person.who_married_id, pk)
    elif arrow == 4:
        # down
        if num_of_children(cur_person):
            new_pk = num_of_children(cur_person)[0].id
        else:
            new_pk = pk

    return redirect('fam_tree_schema', pk= new_pk)


class Create_person(PermissionRequiredMixin, CreateView):
        permission_required = 'Gen_tree.can_edit'
        permission_denied_message = 'доступ запрещен'
        model = Person
        fields = [
            'last_name',
            'first_name',
            'middle_name',
            'birth_date',
            'sex',
            'father',
            'mother',
            'who_married',
            'comment',
            'mainPhoto',
            'previous_last_name',
            'death_date',
        ]
        template_name = 'Person/person_form.html'


        def get_success_url(self):
            pk = self.object.id
            return reverse('detailed_person', kwargs={"pk": pk})

#        def form_valid(self, form):
#            self.object = form.save()


class Change_person(PermissionRequiredMixin, UpdateView):
    permission_required = 'Gen_tree.can_edit'
    permission_denied_message = 'доступ запрещен'
    model = Person
    fields = [
            'id',
            'last_name',
            'previous_last_name',
            'first_name',
            'middle_name',
            'birth_date',
            'death_date',
            'sex',
            'father',
            'mother',
            'who_married',
            'comment',
            'mainPhoto',
        ]
    template_name = 'Person/edit_of_person.html'

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse('detailed_person', kwargs={"pk": pk})


class Delete_person(PermissionRequiredMixin, DeleteView):
    permission_required = 'Gen_tree.can_edit'
    permission_denied_message = 'доступ запрещен'
    model = Person

    template_name = 'Person/delete_of_person.html'
    success_url = "/tree/family_tree/"

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(Delete_person, self).get_object()
        obj.empty_person = None

        return obj

@login_required
def detailed_person (request, pk):
    try:
        cur_person = Person.objects.get(pk = pk)
        children = num_of_children(cur_person)
    except Person.DoesNotExist:
        raise Http404

    return render(request, "Person/detailed_person.html", context={
        'cur_person': cur_person,
        'children':children,
    })


class Add_photo(PermissionRequiredMixin, CreateView):
    permission_required = 'Gen_tree.can_edit'
    permission_denied_message = 'доступ запрещен'
    model = Photo
    fields = [
        'the_photo',
        'comments',
    ]
    template_name = 'Photo/photo_form.html'

    def get_success_url(self):
        pk = self.object.id
        return reverse('photo_detailed', kwargs={"pk": pk})


class List_of_persons(LoginRequiredMixin, ListView):
    model = Person

    def get_queryset(self):
        if True:
        # if self.request.user.is_superuser:
            myquery = Person.objects.all()
            search_p = self.request.GET.get('search_p')
            if search_p is not None:
                search_per = search_p.split()
                for i in range(len(search_per)):
                    myquery = myquery.filter(
                        Q(last_name__icontains=search_per[i])|
                        Q(first_name__icontains=search_per[i])|
                        Q(middle_name__icontains=search_per[i])|
                        Q(previous_last_name__icontains=search_per[i]))

            return myquery.values('last_name',
                                  'first_name',
                                  'middle_name',
                                  'id')

    template_name = 'Person/persons_list.html'

@login_required
def get_Kinfolk_list(request, pk):
    kinfolks = []

    uncles_aunts = set()
    cousins = set()
    bro_sist = set()
    nephew_niece = set()

    try:
        cur_person = Person.objects.get(pk=pk)
    except Person.DoesNotExist:
        raise Http404

# братья/сестры дяди/тети
    if cur_person.father:
        bro_sist = set(num_of_children(cur_person.father))
        bro_sist.discard(cur_person)
        if cur_person.father.father:
            uncles_aunts |= set(num_of_children(cur_person.father.father))
            uncles_aunts.discard(cur_person.father)
        if cur_person.father.mother:
            uncles_aunts |= set(num_of_children(cur_person.father.mother))
            uncles_aunts.discard(cur_person.father)

    if cur_person.mother:
        bro_sist = set(num_of_children(cur_person.mother))
        bro_sist.discard(cur_person)

        if cur_person.mother.father:
            uncles_aunts |= set(num_of_children(cur_person.mother.father))
            uncles_aunts.discard(cur_person.mother)
        if cur_person.mother.mother:
            uncles_aunts |= set(num_of_children(cur_person.mother.mother))
            uncles_aunts.discard(cur_person.mother)

    if bro_sist:
        for person in bro_sist:
            if person.sex == 'F':
                kinfolks += [(person, 'сестра')]
            else:
                kinfolks += [(person, "брат")]
            if person.who_married:
                if person.who_married.sex == 'F':
                    kinfolks += [(person.who_married, 'сноха')]
                else:
                    kinfolks += [(person.who_married, 'зять')]
        nephew_niece |= set(num_of_children(person))

# племянники
    if nephew_niece:
        for person in nephew_niece:
            if person.sex == 'F':
                kinfolks += [(person, 'племянница')]
            else:
                kinfolks += [(person, "племянник")]

# дяди/тети

    if uncles_aunts:
        for person in uncles_aunts:
            if person.sex == 'F':
                kinfolks += [(person, 'тетя')]
                if person.who_married:
                    kinfolks += [(person.who_married, 'дядя-свойственник')]
            else:
                kinfolks += [(person, 'дядя')]
                if person.who_married:
                    kinfolks += [(person.who_married, 'тетя-свойственница')]
            cousins |= set(num_of_children(person))

    if cousins:
        for person in cousins:
            if person.sex == 'F':
                kinfolks += [(person, 'кузина (двоюродная сестра)')]
            else:
                kinfolks += [(person, 'кузен (двоюродный брат)')]

    b_s_inlaw = set()
    if cur_person.who_married:
        hus_wife = cur_person.who_married

 # родители жены/мужа
        if hus_wife.father:
            b_s_inlaw |= set(num_of_children(hus_wife.father))
            if hus_wife.sex == 'F':
                kinfolks += [(hus_wife.father, 'тесть')]
            else:
                kinfolks += [(hus_wife.father, 'свёкор')]
        if hus_wife.mother:
            b_s_inlaw |= set(num_of_children(hus_wife.father))
            if hus_wife.sex == 'F':
                kinfolks += [(hus_wife.mother, 'тёща')]
            else:
                kinfolks += [(hus_wife.mother, 'свекровь')]
        b_s_inlaw.discard(hus_wife)

        if b_s_inlaw:
            for person in b_s_inlaw:
                if hus_wife.sex == "F":
                    if person.sex == 'F':
                        kinfolks += [(person, 'свояченица')]
                        if person.who_married:
                            kinfolks +=[(person.who_married, 'свояк')]
                    else:
                        kinfolks += [(person, "шурин")]
                else:
                    if person.sex == "F":
                        kinfolks += [(person, 'золовка')]
                    else:
                        kinfolks += [(person, 'деверь')]

    # родственники через детей
    if num_of_children(cur_person):
        children = set(num_of_children(cur_person))
        for person in children:
            if person.who_married:
                if person.who_married.sex == 'F':
                    kinfolks += [(person.who_married, 'сноха')]
                else:
                    kinfolks += [(person.who_married, 'зять')]
                if person.who_married.father:
                    kinfolks +=[(person.who_married.father, 'сват')]
                if person.who_married.mother:
                    kinfolks += [(person.who_married.mother, 'сватья')]


    return render(request, "Person/kinfolks_list.html", context={
           'cur_person': cur_person,
           'kinfolks': sorted(sorted(kinfolks, key=lambda x: x[0].first_name), key=lambda y: y[0].last_name),
                  })



class Photo_list(LoginRequiredMixin, ListView):
    def get_queryset(self):
           # if self.request.user.is_superuser:
            myquery = Photo.objects.all()
            if 'pk' in self.kwargs:
                pk = self.kwargs['pk']
                myquery = myquery.filter(to_pers_photo__id=pk)
            return myquery

    template_name = 'Photo/photo_list.html'

@login_required
def photo_detailed(request, pk):
    photo = Photo.objects.get(id=pk)
    myquery = Person.objects.all()
    ph_persons = Person.objects.filter(pers_photo=photo)
    add_person_page = request.GET.get('add_per')
    check_people_on_photo = request.GET.get('ch_p')
    if add_person_page:
        return render(request, "Photo/detailed_photo(add_person).html", context={
            'photo': photo,
            'ph_persons': sorted_person_list(ph_persons),
            'myquery': myquery,
        })
    elif check_people_on_photo:
        old_check = check_photo(os.path.join(MEDIA_ROOT, str(photo.the_photo)))
        new_check = []
        check = True
        for id, conf in old_check:
            person = Person.objects.get(id=id)
            if person not in ph_persons:
                new_check.append((person.id,  str(person), conf))

        return render(request, "Photo/detailed_photo(add_person).html", context={
            'photo': photo,
            'ph_persons': sorted_person_list(ph_persons),
            'myquery': myquery,
            'check_photo': new_check,
            'check': check
        })
    else:
        return render(request, "Photo/detailed_photo.html", context={
            'photo': photo,
            'ph_persons': sorted_person_list(ph_persons),
                    })


def person_add_to_photo(request, pk):
    per_id = request.GET.get('per_id')
    person = Person.objects.get(id=per_id)
    photo= Photo.objects.get(id=pk)
    person.pers_photo.add(photo)
    return HttpResponseRedirect (reverse('photo_detailed', args=(photo.pk,)))


