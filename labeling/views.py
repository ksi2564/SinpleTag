from django.contrib import messages
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView

from accountapp.decorators import is_login, is_staff
from category.models import TopCategory, Item, HeelHeight, Sole, Material, Printing, Detail, Color
from classification.models import ClassificationInspectImage
from labeling.models import LabelImage, InspectImage

has_staff_permission = [is_login, is_staff]


def main_page(request):
    return render(request, 'main_page.html')


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
        context['topcategory'] = TopCategory.objects.all()
        context['item'] = Item.objects.all()
        context['heel_height'] = HeelHeight.objects.all()
        context['sole'] = Sole.objects.all()
        context['material'] = Material.objects.all()
        context['printing'] = Printing.objects.all()
        context['detail'] = Detail.objects.all()
        context['color'] = Color.objects.all()
        # 미리보기 bar
        context['pre_images'] = ClassificationInspectImage.objects.filter(labeling_user=self.request.user,
                                                                          labelimage__isnull=True,
                                                                          pk__gte=self.object.pk)[:10]
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

    def post(self, request, *args, **kwargs):
        new_labeled_image = LabelImage()
        new_labeled_image.image = self.get_object()
        new_labeled_image.top_category = TopCategory.objects.get(pk=request.POST.get('top-category'))
        new_labeled_image.item = Item.objects.get(pk=request.POST.get('item'))
        new_labeled_image.heel_height = HeelHeight.objects.get(pk=request.POST.get('heel-height'))
        new_labeled_image.save()
        sole = request.POST.getlist('sole')
        material = request.POST.getlist('material')
        printing = request.POST.getlist('printing')
        detail = request.POST.getlist('detail')
        color = request.POST.getlist('color')
        for s in sole:
            new_labeled_image.sole.add(Sole.objects.get(pk=s))
        for m in material:
            new_labeled_image.material.add(Material.objects.get(pk=m))
        for p in printing:
            new_labeled_image.printing.add(Printing.objects.get(pk=p))
        for d in detail:
            new_labeled_image.detail.add(Detail.objects.get(pk=d))
        for c in color:
            new_labeled_image.color.add(Color.objects.get(pk=c))

        return redirect('labeling:label_list')


@method_decorator(has_staff_permission, name='dispatch')
class LabelingInspectList(ListView):
    paginate_by = 5
    template_name = 'inspect_list.html'

    def get_queryset(self):
        queryset = LabelImage.objects.filter(image__label_inspect_user=self.request.user, inspectimage__isnull=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LabelingInspectList, self).get_context_data(**kwargs)

        block_size = 5  # 하단의 페이지 목록 수

        start_index = int(
            (context['page_obj'].number - 1) / block_size) * block_size  # page_obj.number 1~5 => start_index 0
        end_index = min(start_index + block_size,
                        len(context['paginator'].page_range))  # block_size만큼씩 커지되 page_range를 넘진 않게 설정

        context['page_range'] = context['paginator'].page_range[start_index:end_index]
        # 라벨링 페이지에서는 제품 상세컷만 추가됨
        context['waiting_images'] = LabelImage.objects.filter(image__labeling_user__isnull=False,
                                                              image__label_inspect_user__isnull=True,
                                                              inspectimage__isnull=True)
        return context


class LabelingInspectDetail(DetailView):
    model = LabelImage
    template_name = 'inspect_detail.html'

    def dispatch(self, request, *args, **kwargs):
        image_pk = request.user.pk
        url_pk = LabelImage.objects.filter(pk=self.kwargs['pk']).first()

        if url_pk is None or image_pk is not url_pk.image.label_inspect_user.pk:
            messages.error(request, "접근할 수 없는 정보입니다.", extra_tags='danger')
            return redirect(reverse("labeling:label_list"))
        return super(LabelingInspectDetail, self).dispatch(request)  # 해당 유저가 맞으면 기존에 있던 부모 dispatch를 사용

    def get_context_data(self, **kwargs):
        context = super(LabelingInspectDetail, self).get_context_data(**kwargs)
        context['topcategory'] = TopCategory.objects.all()
        context['item'] = Item.objects.all()
        context['heel_height'] = HeelHeight.objects.all()
        context['sole'] = Sole.objects.all()
        context['material'] = Material.objects.all()
        context['printing'] = Printing.objects.all()
        context['detail'] = Detail.objects.all()
        context['color'] = Color.objects.all()
        # 미리보기 bar
        context['pre_images'] = LabelImage.objects.filter(image__label_inspect_user=self.request.user,
                                                          inspectimage__isnull=True,
                                                          pk__gte=self.object.pk)[:10]
        context['the_prev'] = LabelImage.objects.filter(image__label_inspect_user=self.request.user,
                                                        inspectimage__isnull=True,
                                                        pk__lt=self.object.pk).order_by('-pk').first()
        context['the_next'] = LabelImage.objects.filter(image__label_inspect_user=self.request.user,
                                                        inspectimage__isnull=True,
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
        new_labeled_image = InspectImage()
        new_labeled_image.image = self.get_object()
        new_labeled_image.top_category = TopCategory.objects.get(pk=request.POST.get('top-category'))
        new_labeled_image.item = Item.objects.get(pk=request.POST.get('item'))
        new_labeled_image.heel_height = HeelHeight.objects.get(pk=request.POST.get('heel-height'))
        new_labeled_image.save()
        sole = request.POST.getlist('sole')
        material = request.POST.getlist('material')
        printing = request.POST.getlist('printing')
        detail = request.POST.getlist('detail')
        color = request.POST.getlist('color')
        for s in sole:
            new_labeled_image.sole.add(Sole.objects.get(pk=s))
        for m in material:
            new_labeled_image.material.add(Material.objects.get(pk=m))
        for p in printing:
            new_labeled_image.printing.add(Printing.objects.get(pk=p))
        for d in detail:
            new_labeled_image.detail.add(Detail.objects.get(pk=d))
        for c in color:
            new_labeled_image.color.add(Color.objects.get(pk=c))

        return redirect('labeling:inspect_list')


@method_decorator(is_login, name='dispatch')
class LabelingStatusBoard(ListView):
    queryset = ClassificationInspectImage.objects.filter(image__image_type=0)
    template_name = 'labeling_status_board.html'

    def get_context_data(self, **kwargs):
        context = super(LabelingStatusBoard, self).get_context_data(**kwargs)
        context['labeled_images'] = LabelImage.objects.all()
        context['labeled_percent'] = int(context['labeled_images'].count() / self.object_list.count() * 100)
        context['inspected_images'] = InspectImage.objects.all()
        context['inspected_percent'] = int(context['inspected_images'].count() / self.object_list.count() * 100)

        context['user_images'] = self.object_list.filter(labeling_user=self.request.user)
        context['user_labeled_images'] = LabelImage.objects.filter(image__labeling_user=self.request.user)
        context['user_labeled_percent'] = int(
            context['user_labeled_images'].count() / context['user_images'].count() * 100)
        context['user_inspected_images'] = InspectImage.objects.filter(image__image__labeling_user=self.request.user)
        context['user_inspected_percent'] = int(
            context['user_inspected_images'].count() / context['user_images'].count() * 100)
        return context


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


class LabelingInspectLoadImage(View):
    def post(self, request, *args, **kwargs):
        queryset = LabelImage.objects.filter(image__labeling_user__isnull=False, image__label_inspect_user__isnull=True,
                                             inspectimage__isnull=True)
        n = LabelImage.objects.filter(image__label_inspect_user=self.request.user, inspectimage__isnull=True)
        bulk = []

        if n.count() >= 10:
            messages.error(request, '보유 이미지 수가 너무 많습니다. 보유하신 이미지가 10장 이하일 때 다시 추가 해주세요.', extra_tags='danger')
        elif n.count() + 2 > 10:
            plus_data = 2 - 10 + n.count()
            for image in queryset[:plus_data]:
                image.image.label_inspect_user = self.request.user
                bulk.append(image.image)
            ClassificationInspectImage.objects.bulk_update(bulk, ['label_inspect_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        else:
            for image in queryset[:2]:
                image.image.label_inspect_user = self.request.user
                bulk.append(image.image)
            ClassificationInspectImage.objects.bulk_update(bulk, ['label_inspect_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        return redirect(reverse('labeling:inspect_list'))


def delete_object_function(request, pk):
    obj = LabelImage.objects.get(id=pk)
    obj.image.image.image.delete()
    return redirect(reverse('labeling:inspect_list'))
