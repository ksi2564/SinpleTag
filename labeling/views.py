import datetime
import json

import xlwt
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView

from accountapp.decorators import is_login, is_staff
from category.models import TopCategory, Item, HeelHeight, Sole, Material, Printing, Detail, Color
from classification.models import ClassificationInspectImage
from labeling.models import LabelImage, InspectImage, OutsourcingLabeling

has_staff_permission = [is_login, is_staff]


def main_page(request):
    return render(request, 'main_page.html')


@method_decorator(is_login, name='dispatch')
class LabelingList(ListView):
    paginate_by = 20
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
        image_user_pk = request.user.pk
        url_pk = ClassificationInspectImage.objects.filter(pk=self.kwargs['pk'],
                                                           labelimage__isnull=True).first()

        if url_pk is None or image_user_pk is not url_pk.labeling_user.pk:
            messages.error(request, "접근할 수 없는 정보입니다.", extra_tags='danger')
            return redirect(reverse("labeling:label_list"))
        return super(LabelingDetail, self).dispatch(request)  # 해당 유저가 맞으면 기존에 있던 부모 dispatch를 사용

    def get_context_data(self, **kwargs):
        context = super(LabelingDetail, self).get_context_data(**kwargs)
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

        context['topcategory'] = TopCategory.objects.all()
        context['item'] = Item.objects.all()
        context['heel_height'] = HeelHeight.objects.all()
        context['sole'] = Sole.objects.all()
        context['material'] = Material.objects.all()
        context['printing'] = Printing.objects.all()
        context['detail'] = Detail.objects.all()
        context['color'] = Color.objects.all()

        return context

    def post(self, request, *args, **kwargs):
        new_labeled_image = LabelImage()
        new_labeled_image.image = self.get_object()
        # if request.POST.get('top-category'):
        #     new_labeled_image.top_category = TopCategory.objects.get(pk=request.POST.get('top-category'))
        if request.POST.get('item'):
            new_labeled_image.item = Item.objects.get(pk=request.POST.get('item'))
        # if request.POST.get('heel-height'):
        #     new_labeled_image.heel_height = HeelHeight.objects.get(pk=request.POST.get('heel-height'))
        new_labeled_image.save()  # 단일 속성 저장 후 다중 속성 설정해서 저장함.

        sole = request.POST.getlist('sole')
        material = request.POST.getlist('material')
        # printing = request.POST.getlist('printing')
        # detail = request.POST.getlist('detail')
        # color = request.POST.getlist('color')
        for s in sole:
            new_labeled_image.sole.add(Sole.objects.get(pk=s))
        for m in material:
            new_labeled_image.material.add(Material.objects.get(pk=m))
        # for p in printing:
        #     new_labeled_image.printing.add(Printing.objects.get(pk=p))
        # for d in detail:
        #     new_labeled_image.detail.add(Detail.objects.get(pk=d))
        # for c in color:
        #     new_labeled_image.color.add(Color.objects.get(pk=c))

        if ClassificationInspectImage.objects.filter(labeling_user=self.request.user, labelimage__isnull=True,
                                                     pk__gt=self.get_object().pk):
            return redirect('labeling:label_detail',
                            ClassificationInspectImage.objects.filter(labeling_user=self.request.user,
                                                                      labelimage__isnull=True,
                                                                      pk__gt=self.get_object().pk).first().pk)
        else:
            return redirect('labeling:label_list')


@method_decorator(has_staff_permission, name='dispatch')
class LabelingInspectList(ListView):
    paginate_by = 20
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
        url_pk = LabelImage.objects.filter(pk=self.kwargs['pk'], inspectimage__isnull=True).first()

        if url_pk is None or image_pk is not url_pk.image.label_inspect_user.pk:
            messages.error(request, "접근할 수 없는 정보입니다.", extra_tags='danger')
            return redirect(reverse("labeling:inspect_list"))
        return super(LabelingInspectDetail, self).dispatch(request)  # 해당 유저가 맞으면 기존에 있던 부모 dispatch를 사용

    def get_context_data(self, **kwargs):
        context = super(LabelingInspectDetail, self).get_context_data(**kwargs)
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

        context['topcategory'] = TopCategory.objects.all()
        context['item'] = Item.objects.all()
        context['heel_height'] = HeelHeight.objects.all()
        context['sole'] = Sole.objects.all()
        context['material'] = Material.objects.all()
        context['printing'] = Printing.objects.all()
        context['detail'] = Detail.objects.all()
        context['color'] = Color.objects.all()

        return context

    def post(self, request, *args, **kwargs):
        new_inspected_image = InspectImage()
        new_inspected_image.image = self.get_object()
        # new_inspected_image.top_category = TopCategory.objects.get(pk=request.POST.get('top-category'))
        new_inspected_image.item = Item.objects.get(pk=request.POST.get('item'))
        # new_inspected_image.heel_height = HeelHeight.objects.get(pk=request.POST.get('heel-height'))
        new_inspected_image.save()

        sole = request.POST.getlist('sole')
        material = request.POST.getlist('material')
        # printing = request.POST.getlist('printing')
        # detail = request.POST.getlist('detail')
        # color = request.POST.getlist('color')
        for s in sole:
            new_inspected_image.sole.add(Sole.objects.get(pk=s))
        for m in material:
            new_inspected_image.material.add(Material.objects.get(pk=m))
        # for p in printing:
        #     new_inspected_image.printing.add(Printing.objects.get(pk=p))
        # for d in detail:
        #     new_inspected_image.detail.add(Detail.objects.get(pk=d))
        # for c in color:
        #     new_inspected_image.color.add(Color.objects.get(pk=c))

        if not LabelImage.objects.filter(image__label_inspect_user=self.request.user, inspectimage__isnull=True,
                                         pk__gt=self.get_object().pk):
            return redirect('labeling:inspect_list')
        else:
            return redirect('labeling:inspect_detail',
                            LabelImage.objects.filter(image__label_inspect_user=self.request.user,
                                                      inspectimage__isnull=True,
                                                      pk__gt=self.get_object().pk).first().pk)


class LabelingInspectDetail(DetailView):
    model = LabelImage
    template_name = 'inspect_detail.html'

    def dispatch(self, request, *args, **kwargs):
        image_pk = request.user.pk
        url_pk = LabelImage.objects.filter(pk=self.kwargs['pk'], inspectimage__isnull=True).first()

        if url_pk is None or image_pk is not url_pk.image.label_inspect_user.pk:
            messages.error(request, "접근할 수 없는 정보입니다.", extra_tags='danger')
            return redirect(reverse("labeling:inspect_list"))
        return super(LabelingInspectDetail, self).dispatch(request)  # 해당 유저가 맞으면 기존에 있던 부모 dispatch를 사용

    def get_context_data(self, **kwargs):
        context = super(LabelingInspectDetail, self).get_context_data(**kwargs)
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

        context['topcategory'] = TopCategory.objects.all()
        context['item'] = Item.objects.all()
        context['heel_height'] = HeelHeight.objects.all()
        context['sole'] = Sole.objects.all()
        context['material'] = Material.objects.all()
        context['printing'] = Printing.objects.all()
        context['detail'] = Detail.objects.all()
        context['color'] = Color.objects.all()

        return context

    def post(self, request, *args, **kwargs):
        new_inspected_image = InspectImage()
        new_inspected_image.image = self.get_object()
        # new_inspected_image.top_category = TopCategory.objects.get(pk=request.POST.get('top-category'))
        new_inspected_image.item = Item.objects.get(pk=request.POST.get('item'))
        # new_inspected_image.heel_height = HeelHeight.objects.get(pk=request.POST.get('heel-height'))
        new_inspected_image.save()

        sole = request.POST.getlist('sole')
        material = request.POST.getlist('material')
        # printing = request.POST.getlist('printing')
        # detail = request.POST.getlist('detail')
        # color = request.POST.getlist('color')
        for s in sole:
            new_inspected_image.sole.add(Sole.objects.get(pk=s))
        for m in material:
            new_inspected_image.material.add(Material.objects.get(pk=m))
        # for p in printing:
        #     new_inspected_image.printing.add(Printing.objects.get(pk=p))
        # for d in detail:
        #     new_inspected_image.detail.add(Detail.objects.get(pk=d))
        # for c in color:
        #     new_inspected_image.color.add(Color.objects.get(pk=c))

        if not LabelImage.objects.filter(image__label_inspect_user=self.request.user, inspectimage__isnull=True,
                                         pk__gt=self.get_object().pk):
            return redirect('labeling:inspect_list')
        else:
            return redirect('labeling:inspect_detail',
                            LabelImage.objects.filter(image__label_inspect_user=self.request.user,
                                                      inspectimage__isnull=True,
                                                      pk__gt=self.get_object().pk).first().pk)


@method_decorator(has_staff_permission, name='dispatch')
class LabelingOutsourcingList(ListView):
    model = OutsourcingLabeling
    paginate_by = 100
    template_name = 'outsourcing_list.html'

    def get_context_data(self, **kwargs):
        context = super(LabelingOutsourcingList, self).get_context_data(**kwargs)
        block_size = 5  # 하단의 페이지 목록 수

        start_index = int(
            (context['page_obj'].number - 1) / block_size) * block_size  # page_obj.number 1~5 => start_index 0
        end_index = min(start_index + block_size,
                        len(context['paginator'].page_range))  # block_size만큼씩 커지되 page_range를 넘진 않게 설정

        context['page_range'] = context['paginator'].page_range[start_index:end_index]

        return context


@method_decorator(has_staff_permission, name='dispatch')
class LabelingOutsourcingDetail(DetailView):
    model = OutsourcingLabeling
    template_name = 'outsourcing_detail.html'

    def get_context_data(self, **kwargs):
        context = super(LabelingOutsourcingDetail, self).get_context_data(**kwargs)
        # 미리보기 bar
        context['pre_images'] = OutsourcingLabeling.objects.filter(pk__gte=self.object.pk)[:10]
        context['the_prev'] = OutsourcingLabeling.objects.filter(pk__lt=self.object.pk).order_by('-pk').first()
        context['the_next'] = OutsourcingLabeling.objects.filter(pk__gt=self.object.pk).first()

        context['the_prev'] = context['the_prev'].pk if context['the_prev'] else self.object.pk
        context['the_next'] = context['the_next'].pk if context['the_next'] else self.object.pk

        context['item'] = Item.objects.all()
        context['sole'] = Sole.objects.all()
        context['material'] = Material.objects.all()

        return context

    # def post(self, request, *args, **kwargs):
    #     new_inspected_image = InspectImage()
    #     new_inspected_image.image = self.get_object()
    #     new_inspected_image.item = Item.objects.get(pk=request.POST.get('item'))
    #     new_inspected_image.save()
    #
    #     sole = request.POST.getlist('sole')
    #     material = request.POST.getlist('material')
    #
    #     for s in sole:
    #         new_inspected_image.sole.add(Sole.objects.get(pk=s))
    #     for m in material:
    #         new_inspected_image.material.add(Material.objects.get(pk=m))
    #
    #     if not LabelImage.objects.filter(image__label_inspect_user=self.request.user, inspectimage__isnull=True,
    #                                      pk__gt=self.get_object().pk):
    #         return redirect('labeling:inspect_list')
    #     else:
    #         return redirect('labeling:inspect_detail',
    #                         LabelImage.objects.filter(image__label_inspect_user=self.request.user,
    #                                                   inspectimage__isnull=True,
    #                                                   pk__gt=self.get_object().pk).first().pk)


# 대시보드에서 백분율 계산 시 분모가 0일 때 예외처리 함수
def zero_denom_check(numer, denom):
    if denom != 0:
        return numer / denom * 100
    else:
        return 0


@method_decorator(is_login, name='dispatch')
class LabelingStatusBoard(ListView):
    queryset = ClassificationInspectImage.objects.filter(image__image_type=0)
    template_name = 'labeling_status_board.html'

    def get_context_data(self, **kwargs):
        context = super(LabelingStatusBoard, self).get_context_data(**kwargs)
        context['labeled_images'] = LabelImage.objects.all()
        context['labeled_percent'] = int(zero_denom_check(context['labeled_images'].count(), self.object_list.count()))
        context['inspected_images'] = InspectImage.objects.all()
        context['inspected_percent'] = int(
            zero_denom_check(context['inspected_images'].count(), self.object_list.count()))
        context['user_images'] = self.object_list.filter(labeling_user=self.request.user)

        context['user_labeled_images'] = LabelImage.objects.filter(image__labeling_user=self.request.user)
        context['user_labeled_percent'] = int(
            zero_denom_check(context['user_labeled_images'].count(), context['user_images'].count()))

        context['user_inspected_images'] = InspectImage.objects.filter(image__image__labeling_user=self.request.user)
        context['user_inspected_percent'] = int(
            zero_denom_check(context['user_inspected_images'].count(), context['user_images'].count()))

        # 대시보드 통계 자료에 사용되는 context
        inspect_images = InspectImage.objects.all()
        # categories = {}
        # for category in TopCategory.objects.all():
        #     categories[category.name] = inspect_images.filter(top_category=category).count()
        # context['top_categories'] = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        categories = {}
        for category in Item.objects.all():
            categories[category.name] = inspect_images.filter(item=category).count()
        context['item'] = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        # categories = {}
        # for category in HeelHeight.objects.all():
        #     categories[category.name] = inspect_images.filter(heel_height=category).count()
        # context['heels'] = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        categories = {}
        for category in Sole.objects.all():
            categories[category.name] = inspect_images.filter(sole=category).count()
        context['soles'] = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        categories = {}
        for category in Material.objects.all():
            categories[category.name] = inspect_images.filter(material=category).count()
        context['materials'] = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        # categories = {}
        # for category in Printing.objects.all():
        #     categories[category.name] = inspect_images.filter(printing=category).count()
        # context['printings'] = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        # categories = {}
        # for category in Detail.objects.all():
        #     categories[category.name] = inspect_images.filter(detail=category).count()
        # context['details'] = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        # categories = {}
        # for category in Color.objects.all():
        #     categories[category.name] = inspect_images.filter(color=category).count()
        # context['color'] = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        return context


class LabelingLoadImage(View):
    def post(self, request, *args, **kwargs):
        queryset = ClassificationInspectImage.objects.filter(labeling_user__isnull=True, image__image_type=0,
                                                             labelimage__isnull=True)
        n = ClassificationInspectImage.objects.filter(labeling_user=self.request.user, labelimage__isnull=True)
        bulk = []

        if n.count() >= 100:
            messages.error(request, f'보유 이미지 수가 {n.count()}장입니다. 100장 미만일 때 다시 요청해주세요.', extra_tags='danger')
        elif n.count() + 20 > 100:
            plus_data = 20 - 100 + n.count()
            for image in queryset[:plus_data]:
                image.labeling_user = self.request.user
                bulk.append(image)
            ClassificationInspectImage.objects.bulk_update(bulk, ['labeling_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        else:
            for image in queryset[:20]:
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

        if n.count() >= 100:
            messages.error(request, f'보유 이미지 수가 {n.count()}장입니다. 100장 미만일 때 다시 요청해주세요.', extra_tags='danger')
        elif n.count() + 20 > 100:
            plus_data = 20 - 100 + n.count()
            for image in queryset[:plus_data]:
                image.image.label_inspect_user = self.request.user
                bulk.append(image.image)
            ClassificationInspectImage.objects.bulk_update(bulk, ['label_inspect_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        else:
            for image in queryset[:20]:
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


def excel_export(request):
    response = HttpResponse(content_type="application/vnd.ms-excel")
    # 다운로드 받을 때 생성될 파일명 설정
    response["Content-Disposition"] = 'attachment; filename=labeling_' + str(datetime.date.today()) + '.xls'

    # 인코딩 설정
    wb = xlwt.Workbook(encoding='utf-8')
    # 생성될 시트명 설정
    ws = wb.add_sheet('신발 카테고리')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # columns = ['이미지', '카테고리', '아이템', '굽 높이', '밑창 모양', '소재감', '프린트', '디테일', '색상']
    columns = ['이미지', '아이템', '밑창 모양', '소재감']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = InspectImage.objects.all()
    attr = []

    # 1행씩 들어갈 값 attr에 append
    for row in rows:
        attr.append(row.image.image.image.image.image.name)
        # attr.append(row.top_category.name)
        attr.append(row.item.name)
        # attr.append(row.heel_height.name)
        attr.append([', '.join([x.name for x in row.sole.all()])])
        attr.append([', '.join([x.name for x in row.material.all()])])
        # attr.append([', '.join([x.name for x in row.printing.all()])])
        # attr.append([', '.join([x.name for x in row.detail.all()])])
        # attr.append([', '.join([x.name for x in row.color.all()])])
        row_num += 1
        for col_num in range(len(attr)):
            ws.write(row_num, col_num, attr[col_num], font_style)
        attr = []

    wb.save(response)

    return response


def outsourcing_json_deserializer(request):
    sole, material = [], []
    json_data = open("static/outsourcing.json")
    data_list = json.load(json_data)
    json_data.close()
    bulk = []

    try:
        for data in data_list:
            image = 'http://' + request.get_host() + '/media/outsourcing/' + data['img_name'] + '.jpg'
            item = data["shoes_type"]
            material = data["material"]
            sole = data["sole"]
            bulk.append(OutsourcingLabeling(image=image, item=Item.objects.get(name=item)))
        created_labeling = OutsourcingLabeling.objects.bulk_create(bulk)
        # ManyToMany field add attr
        for attr in created_labeling:
            for s in sole:
                attr.sole.add(Sole.objects.get(name=s))
            for m in material:
                attr.material.add(Material.objects.get(name=m))
    except KeyError:
        pass

    return redirect(reverse('labeling:outsourcing_list'))
