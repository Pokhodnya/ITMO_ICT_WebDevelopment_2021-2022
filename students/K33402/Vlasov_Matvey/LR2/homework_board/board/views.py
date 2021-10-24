from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Length
from django.shortcuts import render
from django.urls import reverse

from django.views.generic import TemplateView, DetailView, ListView, UpdateView

from board.forms import SubmissionForm
from board.models import ClassDiscipline, Teacher, Student, Discipline, Submission


class HomeView(TemplateView):
    template_name = 'board/home.html'


class ProfileDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = self.request.user
        teacher = Teacher.objects.all().filter(pk=user.pk).first()
        student = Student.objects.all().filter(pk=user.pk).first()
        context = {'teacher': teacher, 'student': student}
        return render(request, 'board/profile.html', context)


class DisciplineListView(LoginRequiredMixin, ListView):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = self.request.user
        teacher = Teacher.objects.all().filter(pk=user.pk).first()
        student = Student.objects.all().filter(pk=user.pk).first()
        context = {'class_disciplines': None}
        if teacher is not None:
            context['class_disciplines'] = ClassDiscipline.objects.filter(teacher=teacher)
        elif student is not None:
            class_disciplines = ClassDiscipline.objects.filter(class_school=student.class_school)\
                .order_by('discipline')
            tasks_graded = []
            tasks_total = []
            average_grade = []

            for obj in class_disciplines.all():
                tasks_graded.append(Submission.objects.filter(
                    student__user=user, assignment__discipline=obj.discipline, grade__isnull=False))
                tasks_total.append(Submission.objects.filter(
                    student__user=user, assignment__discipline=obj.discipline))

            for obj in tasks_graded:
                grades = list(map(lambda x: x.grade, obj.all()))
                if len(grades) == 0:
                    average_grade.append(None)
                    continue
                average_grade.append(sum(grades) / len(grades))

            context['class_disciplines'] = class_disciplines
            context['tasks_graded'] = list(map(lambda x: len(x), tasks_graded))
            context['tasks_total'] = list(map(lambda x: len(x), tasks_total))
            context['average_grade'] = average_grade

        return render(request, 'board/discipline_list.html', context)


class DisciplineDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        discipline = Discipline.objects.get(pk=kwargs['pk'])
        tasks = Submission.objects.filter(student=self.request.user.pk, assignment__discipline=discipline)\
            .order_by('grade', Length('solution'), 'deadline', '-last_submission')
        context = {'discipline': discipline, 'tasks': tasks}
        return render(request, 'board/discipline_detail.html', context)


class SubmissionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = '/login/'

    model = Submission
    form_class = SubmissionForm
    success_message = "Assignment successfully submitted"

    def get_success_url(self):
        return reverse('submission', kwargs={'pk': self.kwargs['pk']})


class AssignmentListView(LoginRequiredMixin, ListView):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        tasks = Submission.objects.filter(student=self.request.user.pk)\
            .order_by('grade', 0**0**Length('solution'), 'deadline', '-last_submission')
        context = {'tasks': tasks}
        return render(request, 'board/assignment_list.html', context)

