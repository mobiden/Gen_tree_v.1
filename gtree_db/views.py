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
    return render(request, "family_tree.html", context={
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

def get_lines(grandparents, parents, main_person, marr_person, children_of_person):
    if marr_person:
        pass
    else:
        pass

@login_required
def fam_tree_schema (request, pk):
    try:
        main_person = Person.objects.get(pk = pk)
        marr_person = None
        if main_person.who_married:
            marr_person = check_person(main_person.who_married)

        children_of_person = check_person(Person.objects.filter(Q(mother=main_person)|
                                                                Q(father=main_person)))

        main_father = check_person(main_person.father)
        main_mother = check_person(main_person.mother)
        if main_person.who_married:
            marr_father = check_person(marr_person.father)
            marr_mother = check_person(marr_person.mother)
            parents = [None, main_father, None, main_mother, None, marr_father, None, marr_mother]
        else:
            parents = [None, main_father, None, main_mother,]

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
        else:
            grandparents = [f_grandmother_main, f_grandfather_main, m_grandfather_main,
                        m_grandmother_main,
                        ]


        cur_fam = [None, None, main_person, None, None, marr_person, None, None]
        lines = [grandparents,
                 parents,
                 cur_fam,
                 children_of_person,
                 ]
    except Person.DoesNotExist:
        raise Http404

    return render(request, "fam_tree_schema.html", context={
        'lines':lines,
    })



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
        children = Person.objects.filter(Q(father=cur_person)|Q(mother=cur_person))
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
                        Q(middle_name__icontains=search_per[i]))
            return myquery.values('last_name', 'first_name', 'middle_name', 'id')

    template_name = 'Person/persons_list.html'



class Photo_list(LoginRequiredMixin, ListView):


    def get_queryset(self):
           # if self.request.user.is_superuser:
            myquery = Photo.objects.all()
            pk = self.request.GET.get('pk')
            if pk is not None:
                myquery = myquery.filter(to_pers_photo__id=pk)

            return myquery.values('photo', 'comments', 'id')

    template_name = 'Photo/photo_list.html'

