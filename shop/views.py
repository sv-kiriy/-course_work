from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import hashlib
import random
import json
import logging
from reportlab.pdfgen import canvas
from time import time, ctime

from shop.models import *

logger = logging.getLogger('django.views')

@csrf_exempt
def login_(request):
    auth_error = None
    if request.method == 'POST':
        _login = request.POST.get('username', '')
        _pass = request.POST.get('password', '')
        user = authenticate(username=_login, password=_pass)
        if user is not None:
            login(request, user)
            logger.info("%s User %s logged in" % (ctime(time()), _login))
            return HttpResponseRedirect('/')
        else:
            logger.info("%s User %s failed to log in" % (ctime(time()), _login))
            auth_error = True
    return render(request, 'login.html', {'auth_error': auth_error})


def logout_(request):
    logger.info("%s User %s logged out" % (ctime(time()), request.user, ))
    logout(request)
    return HttpResponseRedirect('/')

@csrf_exempt
def signup(request):
    if request.method == 'POST':
#        name         = request.POST.get("name")
#        second_name  = request.POST.get("second_name")
#        email        = request.POST.get("email")
#        country      = request.POST.get("country")
#        mobile_phone = request.POST.get("mobile_phone")
        username     = request.POST.get("username")
        password     = request.POST.get("password")
        password_2   = request.POST.get("password_2")

        user_exists = User.objects.filter(username=username).exists()
        e_user_exists = True if user_exists else False
        e_passw = True if password != password_2 else False
        if e_user_exists or e_passw:
            context = {
 #               "name"          : name,
 #               "second_name"   : second_name,
 #               "email"         : email,
 #               "country"       : country,
 #               "mobile_phone"  : mobile_phone,
                "username"      : username,
                "e_user_exists" : e_user_exists,
                "e_passw"       : e_passw,
            }
            return render(request, 'signup.html', context)

        user = User.objects.create_user(username, '', password)
        user.save()
        user_token = request.session['user_token']
        user_cart, _ = Cart.objects.get_or_create(user_token=user_token)
        profile = Profile.objects.create(cart=user_cart,
#                                         first_name=name,
#                                         second_name=second_name,
#                                         country=country,
#                                         mobile_phone=mobile_phone,
                                         user=user)
        profile.save()
        logger.info("%s Registered new user %s" % (ctime(time()), username))
        return login_(request)

    return render(request, 'signup.html', {})

@login_required
@csrf_exempt
def payment(request):
    user_cart = request.user.profile.cart
    items = user_cart.items
    return render(request, 'payment.html', {'items': items,
                                            'total': user_cart.total})


def apidoc(request):
    return render(request, 'apidoc.html')


@csrf_exempt
def download_pdf(request):
    order_id = request.POST['order_id']
    order = Order.objects.get(pk=order_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="order_%s.pdf"' % order_id
    p = canvas.Canvas(response)
    p.setFont("Courier", 12)
    items = json.loads(order.items)
    l = 40
    x, y = 100, 700
    p.drawString(x, y, "Order #%s for user %s" % (order.id, order.user.username))
    p.drawString(x, y - 100, 'Item'.ljust(l) + 'Price')
    y -= 130
    for i in items:
        p.drawString(x, y, i['item'].ljust(l) + str(i['price']))
        y -= 30
    p.drawString(x, y, 'Total:'.ljust(l) + str(order.total))
    p.showPage()
    p.save()
    return response
    

@csrf_exempt
@login_required
def pay(request):
    user_cart = request.user.profile.cart
    items = json.dumps([
                {'item' : str(i),
                 'price': i.amount * i.ref.price } for i in user_cart.items])
    order = Order.objects.create(user=request.user, total=user_cart.total, items=items)
    user_cart.cartitem_set.clear()
    order.status = 2
    order.save()
    logger.info("%s User %s payed the order %s" % (ctime(time()), request.user, order.id))
    return HttpResponse('''<center>ok, order marked as payed, <a href="/">go home</a>
                        <br>
                        <form method=POST action=/download_pdf/>
                        <input type=hidden name=order_id value=%s>
                        <input type=submit value="download PDF">
                        </form></center>''' % order.id)


def index(request):
    if 'user_token' not in request.session:
        request.session['user_token'] = hashlib.md5(str(random.random()).encode()).hexdigest()
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        user_cart = user.profile.cart
    else:
        user_token = request.session['user_token']
        user_cart, _ = Cart.objects.get_or_create(user_token=user_token)
    game_id = request.GET.get('game_id', '')
    game_title = ''
    if game_id:
        game = Game.objects.get(pk=game_id)
        game_title = game.title
        items = game.item_set.all()
    else:
        items = Item.objects.all()
    paginator = Paginator(items, 10)
    page = request.GET.get('page', 1)
    items = paginator.page(page)
    return render(request, 'index.html', { 'items':items,
                                           'cart_items': [i.ref for i in user_cart.items],
                                           'game_title':game_title })


def dump_lic_keys(request):
    def keys_to_json(keys):
        return [{'game_version': k.version,
                 'game_id': k.game.id,
                 'price': k.price} for k in keys]
    game_id = request.GET.get('game_id', '')
    if game_id:
        game = Game.objects.get(pk=game_id)
        items = game.item_set.all()
    else:
        items = Item.objects.all()
    return JsonResponse({'lic_keys': keys_to_json(items)})


def dump_games(request):
    def games_to_json(games):
        return [{'game_title': g.title,
                 'game_description': g.description,
                 'game_id': g.id} for g in games]
    game_id = request.GET.get('game_id', '')
    if game_id:
        games = [Game.objects.get(pk=game_id)]
    else:
        games = Game.objects.all()
    return JsonResponse({'games': games_to_json(games)})


@csrf_exempt
def del_from_cart(request):
    item_id = request.POST['item_id']
    item = CartItem.objects.get(pk=item_id)
    item.delete()
    return HttpResponseRedirect('/cart/')


@csrf_exempt
def change_amount(request):
    item_id = request.POST['item_id']
    delta = int(request.POST['delta'])
    item = CartItem.objects.get(pk=item_id)
    item.amount += delta
    item.save()
    return HttpResponseRedirect('/cart/')


@csrf_exempt
def add_to_cart(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        user_cart = user.profile.cart
    else:
        user_token = request.session['user_token']
        user_cart, _ = Cart.objects.get_or_create(user_token=user_token)
    item_id = request.POST['item_id']
    item = Item.objects.get(pk=item_id)
    c_item, _ = CartItem.objects.get_or_create(ref=item, cart=user_cart)
    c_item.amount = 1
    c_item.save()
    return HttpResponseRedirect('/')

def cart(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        user_cart = user.profile.cart
    else:
        user_token = request.session['user_token']
        user_cart, _ = Cart.objects.get_or_create(user_token=user_token)
    items = user_cart.items
    paginator = Paginator(items, 10)
    page = request.GET.get('page', 1)
    items = paginator.page(page)
    return render(request, 'cart.html', {'items':items})


@csrf_exempt
def search(request):
    words = request.POST['search']
    items = Game.objects.search(words.split())
    paginator = Paginator(items, 10)
    page = request.GET.get('page', 1)
    items = paginator.page(page)

    return render(request, 'games.html', {'items':items, 'search':words})


def games(request):
    items = Game.objects.all()
    paginator = Paginator(items, 10)
    page = request.GET.get('page', 1)
    items = paginator.page(page)

    return render(request, 'games.html', {'items':items})


@login_required
def profile(request):

    return render(request, 'index.html', {})
