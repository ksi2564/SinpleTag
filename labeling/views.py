from django.contrib import messages
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView

from accountapp.decorators import is_login
from classification.models import ClassificationInspectImage


def main_page(request):
    return render(request, 'main_page2.html')


@method_decorator(is_login, name='dispatch')
class LabelingList(ListView):
    paginate_by = 5
    template_name = 'label_list.html'

    def get_queryset(self):
        queryset = ClassificationInspectImage.objects.filter(labeling_user=self.request.user, labelimage__isnull=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LabelingList, self).get_context_data(**kwargs)

        block_size = 5  # 하단의 페이지 목록 수

        start_index = int(
            (context['page_obj'].number - 1) / block_size) * block_size  # page_obj.number 1~5 => start_index 0
        end_index = min(start_index + block_size,
                        len(context['paginator'].page_range))  # block_size만큼씩 커지되 page_range를 넘진 않게 설정

        context['page_range'] = context['paginator'].page_range[start_index:end_index]
        # 라벨링 페이지에서는 제품 상세컷만 추가됨
        context['waiting_images'] = ClassificationInspectImage.objects.filter(labeling_user__isnull=True,
                                                                              image__image_type=0,
                                                                              labelimage__isnull=True)
        return context


class LabelingDetail(DetailView):
    model = ClassificationInspectImage
    template_name = 'label_detail.html'

    def dispatch(self, request, *args, **kwargs):
        image_pk = request.user.pk
        url_pk = ClassificationInspectImage.objects.filter(pk=self.kwargs['pk'],
                                                           label_inspect_user__isnull=True).first()

        if url_pk is None or image_pk is not url_pk.labeling_user.pk:
            messages.error(request, "접근할 수 없는 정보입니다.", extra_tags='danger')
            return redirect(reverse("labeling:label_list"))
        return super(LabelingDetail, self).dispatch(request)  # 해당 유저가 맞으면 기존에 있던 부모 dispatch를 사용

    def get_context_data(self, **kwargs):
        context = super(LabelingDetail, self).get_context_data(**kwargs)
        context['pre_images'] = ClassificationInspectImage.objects.filter(labeling_user=self.request.user,
                                                                          labelimage__isnull=True,
                                                                          pk__gte=self.object.pk)[
                                :10]
        context['the_prev'] = ClassificationInspectImage.objects.filter(labeling_user=self.request.user,
                                                                        labelimage__isnull=True,
                                                                        pk__lt=self.object.pk).order_by('-pk').first()
        context['the_next'] = ClassificationInspectImage.objects.filter(labeling_user=self.request.user,
                                                                        labelimage__isnull=True,
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


def label_detail(request):
    return render(request, 'label_detail.html')


def inspect_list(request):
    return render(request, 'inspect_list.html')


def inspect_detail(request):
    return render(request, 'inspect_detail.html')


def status_board(request):
    return render(request, 'status_board.html')


class LabelingLoadImage(View):
    def post(self, request, *args, **kwargs):
        queryset = ClassificationInspectImage.objects.filter(labeling_user__isnull=True, image__image_type=0,
                                                             labelimage__isnull=True)
        n = ClassificationInspectImage.objects.filter(labeling_user=self.request.user, labelimage__isnull=True)
        bulk = []

        if n.count() >= 10:
            messages.error(request, '보유 이미지 수가 너무 많습니다. 보유하신 이미지가 10장 이하일 때 다시 추가 해주세요.', extra_tags='danger')
        elif n.count() + 2 > 10:
            plus_data = 2 - 10 + n.count()
            for image in queryset[:plus_data]:
                image.labeling_user = self.request.user
                bulk.append(image)
            ClassificationInspectImage.objects.bulk_update(bulk, ['labeling_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        else:
            for image in queryset[:2]:
                image.labeling_user = self.request.user
                bulk.append(image)
            ClassificationInspectImage.objects.bulk_update(bulk, ['labeling_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        return redirect(reverse('labeling:label_list'))
