
#from django.contrib import admin
from django.urls import path
from django.conf import settings
from gestor import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    path('logout/', views.signout, name='logout'),
    path('login/', views.init_sesion, name='login'),
    path('ingreso/', views.ingreso, name='ingreso'),
    path('analisis/', views.analisis, name='analisis'),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)