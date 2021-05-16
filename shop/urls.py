from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('del_from_cart/', views.del_from_cart, name='del_from_cart'),
    path('change_amount/', views.change_amount, name='change_amount'),
    path('payment/', views.payment, name='payment'),
    path('pay/', views.pay, name='pay'),
    path('profile/', views.profile, name='profile'),
    path('games/', views.games, name='games'),
    path('signup/', views.signup, name='signup'),
    path('search/', views.search, name='search'),
    path('login/', views.login_, name='login_'),
    path('logout/', views.logout_, name='logout_'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),
    path('apidoc/', views.apidoc, name='apidoc'),
    path('api/games/', views.dump_games, name='dump_games'),
    path('api/lic_keys/', views.dump_lic_keys, name='dump_lic_keys'),
]
