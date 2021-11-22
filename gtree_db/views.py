from itertools import zip_longest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView

from gtree_db.models import Person, Photo, Empty_person


@login_required
def main_page(request):
    return render(request, 'main.html')

@login_required
def family_tree(request):
    all_person = Person.objects.all().annotate(Count('id'))
    return render(request, "family_list.html", context={
        'all_person': all_person,
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
    if married:
        first = int((9 - amount) / 2)
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
    else:
        if amount > 4:
            second = 8 - amount
            first_list = []
            second_list = []
            for i in range(second):
                second_list += [None]
            first_list += persons
            first_list += second_list
        else:
            first = int((3 - amount) / 2) + 1
            second = 4 - amount - first
            first_list = []
            for i in range(first):
                first_list += [None]
            second_list = []
            for i in range(second):
                second_list += [None]
            first_list += persons
            first_list += second_list

        return first_list


def get_arrow(number):
    if number == 100:
        # white block
        path_width = ("/media/work/whiteblock.jpg", 1)
    elif number == 111:
        path_width = ("/media/work/11-1arrow.jpg", 1)
    elif number == 121:
        path_width = ("/media/work/12-1arrow.jpg", 2)
    elif number == 122:
        path_width = ("/media/work/12-2arrow.jpg", 2)
    elif number == 132:
        path_width = ("/media/work/13-2arrow.jpg", 3)
    elif number == 153:
        path_width = ("/media/work/15-3arrow.jpg", 5)
    elif number == 1524:
        path_width = ("/media/work/15-24arrow.jpg", 5)
    elif number == 15234:
        path_width = ("/media/work/15-234arrow.jpg", 5)

    else:
        # change raise
        raise Exception('Нет Стрелки').with_traceback()
    return path_width

def num_of_children (cur_person):
    return Person.objects.filter(Q(father=cur_person) | Q(mother=cur_person))

@login_required
def fam_tree_schema (request, pk):
    try:
        main_person = Person.objects.get(pk=pk)
        marr_person = None
        if main_person.who_married:
            marr_person = main_person.who_married

        children_of_person = (Person.objects.filter(Q(mother=main_person)|
                                                                Q(father=main_person)))

        num_arr_for_child = len(children_of_person)
        if num_arr_for_child == 1:
            children_arrows = [get_arrow(100), get_arrow(100), get_arrow(153)]
        elif num_arr_for_child == 2:
            children_arrows = [get_arrow(100), get_arrow(100), get_arrow(1524)]
        elif num_arr_for_child == 3:
            children_arrows = [get_arrow(100), get_arrow(100), get_arrow(15234)]
        else:
            children_arrows = None

        married = False
        if marr_person:
            married = True
        children_of_person = persons_in_center(children_of_person, married)



        main_father = check_person(main_person.father)
        main_mother = check_person(main_person.mother)
        if main_person.who_married:
            marr_father = check_person(marr_person.father)
            marr_mother = check_person(marr_person.mother)
            parents = [None, main_father, None, main_mother, None, marr_father, None, marr_mother]
            parents_arrows = [get_arrow(100), get_arrow(132), get_arrow(100), get_arrow(132)]
        else:
            parents = [None, main_father, None, main_mother,]
            parents_arrows = [get_arrow(100), get_arrow(132), ]

        f_grandmother_main = check_person(main_father.mother)
        f_grandfather_main = check_person(main_father.father)
        m_grandfather_main = check_person(main_mother.father)
        m_grandmother_main = check_person(main_mother.mother)

        if main_person.who_married:
            f_grandfather_marr = check_person(marr_father.father)
            f_grandmother_marr = check_person(marr_father.mother)
            m_grandfather_marr = check_person(marr_mother.father)
            m_grandmother_marr = check_person(marr_mother.mother)
            grandparents = [f_grandmother_main, f_grandfather_main, m_grandfather_main,
                            m_grandmother_main, f_grandfather_marr, f_grandmother_marr,
                            m_grandfather_marr, m_grandmother_marr,
                            ]
            grandparents_arrows = [get_arrow(122), get_arrow(122),
                                   get_arrow(122), get_arrow(122)]

        else:
            grandparents = [f_grandmother_main, f_grandfather_main, m_grandfather_main,
                        m_grandmother_main,
                        ]
            grandparents_arrows = [get_arrow(122), get_arrow(122),]


        cur_fam = [None, None, main_person, None, None, None, marr_person, None]

    except Person.DoesNotExist:
        # change raise
        raise Http404

    lines = [grandparents, parents, cur_fam, children_of_person, ]

    arrow_lines = [grandparents_arrows, parents_arrows, children_arrows]

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
            new_pk = get_person_or_default(cur_person.father_id, pk)
        else:
            new_pk = get_person_or_default(cur_person.mother_id, pk)

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


class Create_person(LoginRequiredMixin, CreateView):
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
        success_url = "/tree/family_tree/"

#        def form_valid(self, form):
#            self.object = form.save()


class Change_person(LoginRequiredMixin, UpdateView):
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
    success_url = "/tree/family_tree/"

class Delete_person(LoginRequiredMixin, DeleteView):
    model = Person

    template_name = 'Person/delete_of_person.html'
    success_url = "/tree/family_tree/"

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


class Add_photo(LoginRequiredMixin, CreateView):
    model = Photo
    fields = [
        'photo',
        'comments',
    ]
    template_name = 'Photo/photo_form.html'
    success_url = "/tree/family_tree/"


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

            return myquery.values('last_name', 'first_name', 'middle_name', 'id')

    template_name = 'Person/persons_list.html'



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
    ph_persons = Person.objects.filter(pers_photo=photo)
    return render(request, "Photo/detailed_photo.html", context={
        'photo': photo,
        'ph_persons': ph_persons,
    })

def person_add_to_photo(request, pk):
    pass