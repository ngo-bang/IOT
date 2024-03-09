from django.urls import path,include
from . import views
app_name = "opendoor"
urlpatterns = [
    path('home',views.MainHome.as_view(),name = "home"),
    path('login/',views.Login.as_view(),name= "login"),
    path('signup', views.SignUp.as_view(), name="signup"),
    path('requestcamera',views.RequestCameraProcesser,name="requestcamera"),
    path('housekey', views.getHouseKey, name='housekey'),
    path('processbutton', views.processButton, name='processbutton'),
    path('servo', views.processServo, name='servo'),
]