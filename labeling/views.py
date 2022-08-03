from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView

from labeling.models import RequestPermission, InitialImage, ClassificationImage, ClassificationInspectImage


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

        if user_pk is not url_pk:
            messages.error(request, "접근할 수 없는 정보입니다.", extra_tags='danger')
            return redirect(reverse("labeling:mainpage"))
        return super(MyInfo, self).dispatch(request)  # 해당 유저가 맞으면 기존에 있던 부모 dispatch를 사용

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
    paginate_by = 5
    template_name = 'classification_list.html'

    def get_queryset(self):
        queryset = InitialImage.objects.filter(label_user=self.request.user, classificationimage__isnull=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ClassificationList, self).get_context_data(**kwargs)

        block_size = 5  # 하단의 페이지 목록 수

        start_index = int(
            (context['page_obj'].number - 1) / block_size) * block_size  # page_obj.number 1~5 => start_index 0
        end_index = min(start_index + block_size,
                        len(context['paginator'].page_range))  # block_size만큼씩 커지되 page_range를 넘진 않게 설정

        context['page_range'] = context['paginator'].page_range[start_index:end_index]

        context['waiting_images'] = InitialImage.objects.filter(label_user__isnull=True,
                                                                classificationimage__isnull=True)
        return context


class ClassificationLoadImage(View):
    def post(self, request, *args, **kwargs):
        queryset = InitialImage.objects.filter(label_user__isnull=True, classificationimage__isnull=True)
        n = InitialImage.objects.filter(label_user=self.request.user, classificationimage__isnull=True)
        bulk = []

        if n.count() == 10:
            messages.error(request, '보유 가능 이미지는 최대 10장으로 제한됩니다. 작업 후 다시 추가 해주세요.', extra_tags='danger')
        elif n.count() + 2 > 10:
            plus_data = 2 - 10 + n.count()
            for image in queryset[:plus_data]:
                image.label_user = self.request.user
                bulk.append(image)
            InitialImage.objects.bulk_update(bulk, ['label_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        else:
            for image in queryset[:2]:
                image.label_user = self.request.user
                bulk.append(image)
            InitialImage.objects.bulk_update(bulk, ['label_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        return redirect(reverse('labeling:classification_list'))


# def classification_detail(request):
#     return render(request, 'classification_detail.html')


class ClassificationDetail(DetailView):
    model = InitialImage
    template_name = 'classification_detail.html'

    def get_success_url(self):
        return reverse('labeling:classification_list')

    def get_context_data(self, **kwargs):
        context = super(ClassificationDetail, self).get_context_data(**kwargs)
        context['pre_images'] = InitialImage.objects.filter(label_user=self.request.user, pk__gte=self.object.pk)[:10]
        try:
            context['the_prev'] = InitialImage.objects.filter(label_user=self.request.user,
                                                              classificationimage__isnull=True,
                                                              pk__lt=self.object.pk).order_by('-pk').first().pk
        except:
            context['the_prev'] = InitialImage.objects.filter(label_user=self.request.user,
                                                              classificationimage__isnull=True,
                                                              pk__gt=self.object.pk).order_by('-pk').first().pk
        try:
            context['the_next'] = InitialImage.objects.filter(label_user=self.request.user,
                                                              classificationimage__isnull=True,
                                                              pk__gt=self.object.pk).order_by('pk').first().pk
        except:
            context['the_next'] = InitialImage.objects.filter(label_user=self.request.user,
                                                              classificationimage__isnull=True,
                                                              pk__lt=self.object.pk).order_by('pk').first().pk
        return context

    def post(self, request, *args, **kwargs):
        classification_image = ClassificationImage()
        classification_image.image = self.get_object()
        classification_image.detail_or_not = request.POST.get('classification')
        classification_image.save()

        if not InitialImage.objects.filter(label_user=self.request.user, pk__gt=self.get_object().pk):
            return redirect('labeling:classification_list')
        else:
            return redirect('labeling:classification_detail', InitialImage.objects.filter(label_user=self.request.user,
                                                                                          pk__gt=self.get_object().pk).first().pk)


def delete_object_function(request, pk):
    obj = InitialImage.objects.get(id=pk)
    obj.delete()
    return redirect(reverse('labeling:classification_list'))


# def classification_inspect_list(request):
#     return render(request, 'classification_inspect_list.html')


class ClassificationInspectList(ListView):
    paginate_by = 10
    template_name = 'classification_inspect_list.html'

    def get_queryset(self):
        queryset = ClassificationImage.objects.filter(image__inspect_user=self.request.user,
                                                      classificationinspectimage__isnull=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ClassificationInspectList, self).get_context_data(**kwargs)

        block_size = 5  # 하단의 페이지 목록 수

        start_index = int(
            (context['page_obj'].number - 1) / block_size) * block_size  # page_obj.number 1~5 => start_index 0
        end_index = min(start_index + block_size,
                        len(context['paginator'].page_range))  # block_size만큼씩 커지되 page_range를 넘진 않게 설정

        context['page_range'] = context['paginator'].page_range[start_index:end_index]

        context['waiting_images'] = InitialImage.objects.filter(label_user__isnull=False, inspect_user__isnull=True,
                                                                classificationimage__isnull=False,
                                                                classificationimage__classificationinspectimage__isnull=True)

        return context


class ClassificationInspectLoadImage(View):
    def post(self, request, *args, **kwargs):
        queryset = InitialImage.objects.filter(label_user__isnull=False, inspect_user__isnull=True,
                                               classificationimage__isnull=False,
                                               classificationimage__classificationinspectimage__isnull=True)
        n = ClassificationImage.objects.filter(image__inspect_user=self.request.user,
                                               classificationinspectimage__isnull=True)
        bulk = []
        if n.count() == 10:
            messages.error(request, '보유 가능 이미지는 최대 10장으로 제한됩니다. 작업 후 다시 추가 해주세요.', extra_tags='danger')
        elif n.count() + 2 > 10:
            plus_data = 2 - 10 + n.count()
            for image in queryset[:plus_data]:
                image.inspect_user = self.request.user
                bulk.append(image)
            InitialImage.objects.bulk_update(bulk, ['inspect_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        else:
            for image in queryset[:2]:
                image.inspect_user = self.request.user
                bulk.append(image)
            InitialImage.objects.bulk_update(bulk, ['inspect_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        return redirect(reverse('labeling:classification_inspect_list'))


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


# 체크 박스 값 받아서 분류 라벨링 삭제하기(검수 거부 데이터)
def just_test(request):
    if 'non-pass' in request.POST:
        selected = request.POST.getlist('cb')
        for sel in selected:
            obj = ClassificationImage.objects.filter(id=sel).first()
            obj.delete()
    elif 'pass' in request.POST:
        selected = request.POST.getlist('cb')
        for sel in selected:
            obj = ClassificationImage.objects.filter(id=sel).first()
            new_inspect = ClassificationInspectImage()
            new_inspect.image = obj
            new_inspect.save()
    return redirect(reverse('labeling:classification_inspect_list'))
