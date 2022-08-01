from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView

from labeling.forms import InitialImageForm
from labeling.models import RequestPermission, InitialImage


def main_page(request):
    return render(request, 'main_page2.html')


def login(request):
    return render(request, 'login.html')


# def my_info(request):
#     return render(request, 'my_info.html')


class MyInfo(DetailView):
    model = User
    template_name = 'my_info.html'

    def dispatch(self, request, *args, **kwargs):
        user_pk = request.user.pk
        url_pk = self.kwargs['pk']

        if user_pk is url_pk:
            return super(MyInfo, self).dispatch(request)
        messages.error(request, "접근할 수 없는 정보입니다.", extra_tags='danger')
        return redirect(reverse("labeling:mainpage"))

    def post(self, request, *args, **kwargs):
        new_request = RequestPermission()
        new_request.user = self.request.user
        new_request.name = self.request.user.socialaccount_set.all()[0].extra_data['name']
        new_request.save()

        messages.success(request, "전문가 권한 요청을 하였습니다.")
        return redirect(self.request.path_info)


# def classification_list(request):
#     return render(request, 'classification_list.html')


class ClassificationList(ListView):
    model = InitialImage
    paginate_by = 25
    template_name = 'classification_list.html'

    def get_queryset(self):
        queryset = InitialImage.objects.filter(label_user=self.request.user)
        return queryset


# def classification_detail(request):
#     return render(request, 'classification_detail.html')


class ClassificationDetail(DetailView):
    model = InitialImage
    template_name = 'classification_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ClassificationDetail, self).get_context_data(**kwargs)
        context['pre_images'] = InitialImage.objects.filter(label_user=self.request.user, pk__gte=self.object.pk)[:10]
        try:
            context['the_prev'] = InitialImage.objects.filter(label_user=self.request.user,
                                                              pk__lt=self.object.pk).order_by('-pk').first().pk
        except:
            context['the_prev'] = InitialImage.objects.filter(label_user=self.request.user,
                                                              pk__gt=self.object.pk).order_by('-pk').first().pk
        try:
            context['the_next'] = InitialImage.objects.filter(label_user=self.request.user,
                                                              pk__gt=self.object.pk).order_by('pk').first().pk
        except:
            context['the_next'] = InitialImage.objects.filter(label_user=self.request.user,
                                                              pk__lt=self.object.pk).order_by('pk').first().pk
        return context


class ClassificationUpdate(View):
    def post(self, *args, **kwargs):
        queryset = InitialImage.objects.filter(label_user__isnull=True)
        queryset.update(label_user=self.request.user)
        return redirect(reverse('labeling:classification_list'))


# def permission(request):
#     return render(request, 'permission.html')


def label_list(request):
    return render(request, 'label_list.html')


def label_detail(request):
    return render(request, 'label_detail.html')


def inspect_list(request):
    return render(request, 'inspect_list.html')


def inspect_detail(request):
    return render(request, 'inspect_detail.html')


# def data_upload(request):
#     return render(request, 'data_upload.html')


def status_board(request):
    return render(request, 'status_board.html')
