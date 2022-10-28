import datetime
import os
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

import requests
import xlwt
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView

from accountapp.decorators import is_login, is_staff
from classification.models import InitialImage, ClassificationImage, ClassificationInspectImage
from labeling.views import zero_denom_check

has_staff_permission = [is_login, is_staff]


@method_decorator(is_login, name='dispatch')
class ClassificationList(ListView):
    paginate_by = 20
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


class ClassificationDetail(DetailView):
    model = InitialImage
    template_name = 'classification_detail.html'

    # url 주소에 적힌 이미지 pk가 자신이 접근할 수 있는 이미지인지 확인
    def dispatch(self, request, *args, **kwargs):
        image_user_pk = request.user.pk
        url_pk = InitialImage.objects.filter(pk=self.kwargs['pk'], label_user__isnull=False,
                                             classificationimage__isnull=True).first()

        if url_pk is None or image_user_pk is not url_pk.label_user.pk:
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
        classification_image.image_type = request.POST.get('classification')
        classification_image.save()

        # 분류작업할 사진이 있다면 다음 사진으로 이동
        if InitialImage.objects.filter(label_user=self.request.user, classificationimage__isnull=True,
                                       pk__gt=self.get_object().pk):
            return redirect('classification:classification_detail',
                            InitialImage.objects.filter(label_user=self.request.user, classificationimage__isnull=True,
                                                        pk__gt=self.get_object().pk).first().pk)
        else:
            return redirect('classification:classification_list')


@method_decorator(has_staff_permission, name='dispatch')
class ClassificationInspectList(ListView):
    paginate_by = 20
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
                                                                classificationimage__classificationinspectimage__isnull=
                                                                True)
        return context


@method_decorator(is_login, name='dispatch')
class ClassificationStatusBoard(ListView):
    model = InitialImage
    template_name = 'classification_status_board.html'

    def get_context_data(self, **kwargs):
        context = super(ClassificationStatusBoard, self).get_context_data(**kwargs)
        context['classified_images'] = ClassificationImage.objects.all()
        context['classified_percent'] = int(
            zero_denom_check(context['classified_images'].count(), self.object_list.count()))
        context['inspected_images'] = ClassificationInspectImage.objects.all()
        context['inspected_percent'] = int(
            zero_denom_check(context['inspected_images'].count(), self.object_list.count()))

        context['user_images'] = self.object_list.filter(label_user=self.request.user)
        context['user_classified_images'] = ClassificationImage.objects.filter(image__label_user=self.request.user)
        context['user_classified_percent'] = int(
            zero_denom_check(context['user_classified_images'].count(), context['user_images'].count()))
        context['user_inspected_images'] = ClassificationInspectImage.objects.filter(
            image__image__label_user=self.request.user)
        context['user_inspected_percent'] = int(
            zero_denom_check(context['user_inspected_images'].count(), context['user_images'].count()))

        context['inspected_detail_cut'] = context['inspected_images'].filter(image__image_type=0)
        context['inspected_model_cut'] = context['inspected_images'].filter(image__image_type=1)
        context['inspected_trash_cut'] = context['inspected_images'].filter(image__image_type=2)

        return context


class ClassificationLoadImage(View):
    def post(self, request, *args, **kwargs):
        queryset = InitialImage.objects.filter(label_user__isnull=True, classificationimage__isnull=True)
        n = InitialImage.objects.filter(label_user=self.request.user, classificationimage__isnull=True)
        bulk = []

        if n.count() >= 100:
            messages.error(request, f'보유 이미지 수가 {n.count()}장입니다. 100장 미만일 때 다시 요청해주세요.', extra_tags='danger')
        elif n.count() + 20 > 100:
            plus_data = 20 - 100 + n.count()
            for image in queryset[:plus_data]:
                image.label_user = self.request.user
                bulk.append(image)
            InitialImage.objects.bulk_update(bulk, ['label_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        else:
            for image in queryset[:20]:
                image.label_user = self.request.user
                bulk.append(image)
            InitialImage.objects.bulk_update(bulk, ['label_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        return redirect(reverse('classification:classification_list'))


class ClassificationInspectLoadImage(View):
    def post(self, request, *args, **kwargs):
        queryset = InitialImage.objects.filter(label_user__isnull=False, inspect_user__isnull=True,
                                               classificationimage__isnull=False,
                                               classificationimage__classificationinspectimage__isnull=True)
        n = ClassificationImage.objects.filter(image__inspect_user=self.request.user,
                                               classificationinspectimage__isnull=True)
        bulk = []
        if n.count() == 100:
            messages.error(request, f'보유 이미지 수가 {n.count()}장입니다. 100장 미만일 때 다시 요청해주세요.', extra_tags='danger')
        elif n.count() + 20 > 100:
            plus_data = 20 - 100 + n.count()
            for image in queryset[:plus_data]:
                image.inspect_user = self.request.user
                bulk.append(image)
            InitialImage.objects.bulk_update(bulk, ['inspect_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        else:
            for image in queryset[:20]:
                image.inspect_user = self.request.user
                bulk.append(image)
            InitialImage.objects.bulk_update(bulk, ['inspect_user'])  # bulk에 있는 데이터 모두 한번에 업데이트
            if len(bulk) > 0:
                messages.success(request, f'{len(bulk)}장의 사진이 추가되었습니다.')
            else:
                messages.success(request, '추가할 수 있는 데이터가 없습니다.', extra_tags='danger')
        return redirect(reverse('classification:classification_inspect_list'))


# 이미지 api 요청하여 사진 가져오기
@is_login
@is_staff
def image_api(request):
    url = "http://118.67.133.29/naver/all-images"  # 네이버 쇼핑 크롤링 주소
    # url = "http://118.67.133.29/instagram/all-images"  # 인스타그램 크롤링 주소
    bulk1 = []
    image_list = requests.get(url).json()
    images = image_list['data']
    last_num = InitialImage.objects.last().id
    end_num = last_num + 10000

    for image in images[last_num:end_num]:
        image_url = image['url']
        bulk1.append(InitialImage(image=image_url))
    InitialImage.objects.bulk_create(bulk1)

    return redirect(reverse('classification:classification_list'))


def delete_object_function(request, pk):
    obj = InitialImage.objects.get(id=pk)
    obj.delete()
    return redirect(reverse('classification:classification_list'))


# 분류 검수 페이지 검수 pass or non-pass 결정하는 함수
def pass_or_not(request):
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


# 분류된 이미지 zip 파일 다운로드
def classification_dataset(request):
    dataset = ClassificationInspectImage.objects.filter(image__image_type=0)
    f = BytesIO()  # 버퍼 할당
    zip_f = ZipFile(f, 'w')  # 해당 버퍼에 zip할 파일들 쓰기

    for photo in dataset:
        url = urlopen(str(photo.image.image.image))  # 사진 url
        filename = os.path.join(str(photo.image.image.image).split('/')[-1])
        # if photo.image.image_type == 0:  # 상세컷
        # elif photo.image.image_type == 1:  # 모델컷
        #     filename = os.path.join('model_cut', str(photo.image.image.image).split('/')[-1])
        # else:
        #     filename = os.path.join('trash_cut', str(photo.image.image.image).split('/')[-1])
        zip_f.writestr(filename, url.read())
    zip_f.close()
    response = HttpResponse(f.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + str(datetime.date.today()) + '.zip'  # 다운받게 될 zip 파일 이름 설정
    return response


def excel_export(request):
    response = HttpResponse(content_type="application/vnd.ms-excel")
    # 다운로드 받을 때 생성될 파일명 설정
    response["Content-Disposition"] = 'attachment; filename=classification_' + str(datetime.date.today()) + '.xls'

    # 인코딩 설정
    wb = xlwt.Workbook(encoding='utf-8')
    # 생성될 시트명 설정
    ws = wb.add_sheet('타입분류')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['image', 'type']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = ClassificationInspectImage.objects.all().values_list('image__image__image', 'image__image_type')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

# # 학습 모델 로드
# model = tf.keras.models.load_model("my_model.h5")
#
#
# def my_view(request):
#     X = []
#     image = 'https://cdn.pixabay.com/photo/2019/06/17/14/44/garbage-4280112_960_720.png'
#     response = requests.get(image)
#     img = Image.open(BytesIO(response.content))
#     img = img.resize((128, 128))
#     img = np.array(img)
#     X.append(img)
#     X = np.array(X)
#     predictions = np.argmax(model.predict(X))
#
#     return HttpResponse(
#         predictions
#     )


# 학습된 분류 모델로 iamge를 불러올 때 분류까지 자동으로 해주는 로직
# @is_login
# @is_staff
# def image_api(request):
#     url = "http://118.67.133.29/naver/all-images"
#     bulk1 = []
#     bulk2 = []
#     image_list = requests.get(url).json()
#     images = image_list['data']
#     last_num = InitialImage.objects.count()
#     end_num = last_num + 10
#     X = []
#     Y = []
#
#     for image in images[last_num:end_num]:
#         image_url = image['url']
#         bulk1.append(InitialImage(image=image_url))
#     InitialImage.objects.bulk_create(bulk1)
#     for image in images[last_num:end_num]:
#         image_url = image['url']
#         response = requests.get(image_url)
#         img = Image.open(BytesIO(response.content))
#         img = img.resize((128, 128))
#         img = np.array(img)
#         X.append(img)
#     X = np.array(X)
#     predictions = model.predict(X)
#     for prediction in predictions:
#         bulk2.append(ClassificationImage(image=InitialImage.objects.filter(image=images[last_num]['url']).first(),
#                                          image_type=np.argmax(prediction)))
#         Y.append(np.argmax(prediction))
#         last_num += 1
#     ClassificationImage.objects.bulk_create(bulk2)
#
#     # return HttpResponse(
#     #     Y
#     # )
#
#     return redirect(reverse('classification:classification_list'))
