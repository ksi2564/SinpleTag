from django.contrib import messages
from django.shortcuts import redirect
# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView

from accountapp.decorators import is_login
from classification.models import InitialImage, ClassificationImage, ClassificationInspectImage


@method_decorator(is_login, name='dispatch')
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

        if n.count() >= 10:
            messages.error(request, '보유 이미지 수가 너무 많습니다. 보유하신 이미지가 10장 이하일 때 다시 추가 해주세요.', extra_tags='danger')
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
        return redirect(reverse('classification:classification_list'))


class ClassificationDetail(DetailView):
    model = InitialImage
    template_name = 'classification_detail.html'

    def dispatch(self, request, *args, **kwargs):
        image_pk = request.user.pk
        url_pk = InitialImage.objects.filter(pk=self.kwargs['pk'], label_user__isnull=False,
                                             classificationimage__isnull=True).first()

        if url_pk is None or image_pk is not url_pk.label_user.pk:
            messages.error(request, "접근할 수 없는 정보입니다.", extra_tags='danger')
            return redirect(reverse("classification:classification_list"))
        return super(ClassificationDetail, self).dispatch(request)  # 해당 유저가 맞으면 기존에 있던 부모 dispatch를 사용

    def get_context_data(self, **kwargs):
        context = super(ClassificationDetail, self).get_context_data(**kwargs)
        context['pre_images'] = InitialImage.objects.filter(label_user=self.request.user,
                                                            classificationimage__isnull=True, pk__gte=self.object.pk)[
                                :10]
        context['the_prev'] = InitialImage.objects.filter(label_user=self.request.user,
                                                          classificationimage__isnull=True,
                                                          pk__lt=self.object.pk).order_by('-pk').first()
        context['the_next'] = InitialImage.objects.filter(label_user=self.request.user,
                                                          classificationimage__isnull=True,
                                                          pk__gt=self.object.pk).first()
        if context['the_prev']:
            context['the_prev'] = context['the_prev'].pk
        else:
            context['the_prev'] = self.object.pk
        if context['the_next']:
            context['the_next'] = context['the_next'].pk
        else:
            context['the_next'] = self.object.pk

        return context

    def post(self, request, *args, **kwargs):
        classification_image = ClassificationImage()
        classification_image.image = self.get_object()
        classification_image.detail_or_not = request.POST.get('classification')
        classification_image.save()

        if not InitialImage.objects.filter(label_user=self.request.user, classificationimage__isnull=True,
                                           pk__gt=self.get_object().pk):
            return redirect('classification:classification_list')
        else:
            return redirect('classification:classification_detail',
                            InitialImage.objects.filter(label_user=self.request.user,
                                                        pk__gt=self.get_object().pk).first().pk)


def delete_object_function(request, pk):
    obj = InitialImage.objects.get(id=pk)
    obj.delete()
    return redirect(reverse('classification:classification_list'))


@method_decorator(is_login, name='dispatch')
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
        return redirect(reverse('classification:classification_inspect_list'))


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
    return redirect(reverse('classification:classification_inspect_list'))