from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from .models import User,House
import base64
from PIL import Image
from datetime import datetime
from .encode import encode_face
from .authen import authe_image, findCosineDistance
import os
import numpy as np
import cv2
import secrets
import string
import io


class MainHome(View):
    def get(self, request):
        return render(request, 'opendoor/home.html')

    def post(self, request):
        pass


class Login(View):
    def get(self, request):
        return render(request, 'opendoor/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            house = House.objects.get(housekey=user.housekey)
            status = "Đang mở"
            if house.status==0:
                status="Đang đóng"
            context = {'status': status, 'housekey': user.housekey}
            if password == user.password:
                return render(request, 'opendoor/userhome.html', context=context)
            else:
                return render(request, 'opendoor/login.html')
        except User.DoesNotExist:
            return render(request, 'opendoor/login.html')


class SignUp(View):
    def get(self, request):
        return render(request, 'opendoor/signup.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        housekey = request.POST.get('housekey')
        image_data = request.FILES['image'].read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        decoded_image = base64.b64decode(encoded_image)
        nparr = np.frombuffer(decoded_image, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        c = datetime.now()
        if not os.path.exists('imagedataset'):
            os.makedirs('imagedataset')
        img_name = "avatar_" + str(c.year) + str(c.month) + str(c.day) + str(c.hour) + str(c.minute) + str(
            c.second) + str(c.microsecond) + ".jpg";
        image_path = os.path.join('imagedataset', img_name)
        with open(image_path, 'wb') as file:
            file.write(decoded_image)
        embb = encode_face(img)
        emb = {'embedding_vector': embb}
        house = House.objects.filter(housekey=housekey)
        if house.exists() == False:
            newhouse = House(housekey=housekey, status=False)
            newhouse.save()
        us = User(username=username, password=password, housekey=housekey, link_image=image_path,
                  embedding_vector=emb)
        us.save()
        return HttpResponse('Sign up successful!')


class HomeUser(View):
    def get(self, request):
        return render(request,'opendoor')

    def post(self, request):
        pass

@csrf_exempt
def RequestCameraProcesser(request):
    if request.method=='POST':
        image_data = request.FILES.get('image')
        data = request.POST
        hk = data['housekey']
        time = datetime.now()
        timenow = str(time.strftime("%Y-%m-%d %H:%M"))
        if image_data:
            print(image_data)
            nparr = np.frombuffer(image_data.read(), np.uint8)
            print(nparr.shape)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            _, img_encoded = cv2.imencode('.png', img)
            img_base64 = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
            try:
                dsU = User.objects.filter(housekey=hk)
                for u in dsU:
                    au = authe_image(img, u.embedding_vector['embedding_vector'])
                    if au:
                        house  = House.objects.get(housekey = hk)
                        house.status=1
                        house.save()
                        # channel_layer = get_channel_layer()
                        # async_to_sync(channel_layer.group_send)(
                        #     hk,
                        #     {
                        #         'type': 'send.notification',
                        #         'message': "THÔNG BÁO: Có người nhà về lúc " + timenow,
                        #         'img': img_base64,
                        #     }
                        # )
                        return JsonResponse({"message": "Xác thực thành công","au":au})
                else:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        hk,
                        {
                            'type': 'send.notification',
                            'message': "THÔNG BÁO: Có người lạ đến lúc " + timenow,
                            'img': img_base64,
                        }
                    )
                    return JsonResponse({"message": "Xác thực không thành công","au":au})
            except:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    hk,
                    {
                        'type': 'send.notification',
                        'message': "THÔNG BÁO: Có người lạ đến lúc " + timenow,
                        'img': img_base64,
                    }
                )
                return JsonResponse({"message": "Xác thực không thành công"})
            # print("okkk",encode_face(img))
            cv2.imshow('Image from POST request', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return HttpResponse("thành công post")

def generate_random_code(length):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")  # Lấy thời gian hiện tại dưới dạng chuỗi
    random_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    random_code = timestamp + random_string
    return random_code

def getHouseKey(request):
    houseKey = generate_random_code(20)
    return HttpResponse(f"YourhouseKey:{houseKey}")

def processButton(request):
    if request.method == 'POST':
        status = request.POST.get('status')
        houseKey = request.POST.get('housekey')
        house = House.objects.get(housekey=houseKey)
        house.status = int(status)
        house.save()
        status="Đang mở"
        if house.status==0:
            status ="Đang đóng"
        context = {'status': status, 'housekey': houseKey}
        return render(request, 'opendoor/userhome.html', context=context)

@csrf_exempt
def processServo(request):
    if request.method=='POST':
        data = request.POST
        housekey = data['housekey']
        houses = House.objects.filter(housekey=housekey)
        if houses.exists():
            house = House.objects.get(housekey=housekey)
            return JsonResponse({'message': house.status}, status=200)
        else:
            # Trả về response với status code 404 và dữ liệu JSON
            return HttpResponseNotFound({'message': 'House not found'})
# def processServo(request):
#     if request.method=='POST':
#         housekey = request.data.get('housekey')
#         house = House.objects.filter(housekey=housekey)
#         if house.exists():
#             data = {'status': house.status}
#             return HttpResponse(data)
#         else:
#             data1={'co cai nit':'okkk'}
#             return JsonResponse(data1)


# if __name__ == "__main__":
#     u = User.objects.get(ip_address="123")
#     u = User.objects.get(ip_address="123")
#     u = User.objects.get(ip_address="123")