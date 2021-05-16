from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class GameManager(models.Manager):
    def search(self, words):
        q = Q()
        for w in words:
                   q |= Q(title__icontains=w) | Q(description__icontains=w)
        return self.filter(q)


class Game(models.Model):
    title = models.CharField(max_length=100,
                             default='An interesting game title',
                             verbose_name=u'title')
    description = models.CharField(max_length=255,
                                   default='An interesting game description',
                                   verbose_name=u'description')
    img = models.ImageField(verbose_name=u'image', upload_to='www/games',
                            blank=True, default='www/games/new.jpg')

    objects = GameManager()

    def __str__(self):
        return self.title


class CartItem(models.Model):
    ref = models.ForeignKey('Item', null=True, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', null=True, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name=u'amount', default=1, null=True)

    def __str__(self):
        return "%s %s * %s" % (self.ref.game.title, self.ref.version, self.amount)


class Item(models.Model):
    version = models.CharField(max_length=100, default='1.0', verbose_name=u'version')
    price = models.FloatField(default=9.9, verbose_name=u'Price ($)')
    game = models.ForeignKey('Game', on_delete=models.CASCADE)

    def __str__(self):
        return self.game.title + ' ' + self.version


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cart = models.OneToOneField('Cart', null=True, on_delete=models.CASCADE)


class Cart(models.Model):
    user_token = models.CharField(max_length=100, default='')

    @property
    def items(self):
        return self.cartitem_set.all()

    @property
    def total(self):
        return sum(x.ref.price * x.amount for x in self.items)

    def __str__(self):
        return 'Cart ' + self.user_token[:6] + '..'


class Order(models.Model):
    PAYMENT_STATUSES = (
        (1, 'Pending'),
        (2, 'Completed'),
        (3, 'Cancelled')
    )
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    status = models.SmallIntegerField(verbose_name='Status',
                                      choices=PAYMENT_STATUSES,
                                      default=1)
    total = models.FloatField(verbose_name='total',
                              default=0)
    items = models.CharField(max_length=1000,
                             default='',
                             verbose_name='Items')

    def __str__(self):
        return 'Order for ' + self.user.username


class NewItem(models.Model):
    ''' Butch upload of new games or license keys (items) in JSON format '''

    NEW_ITEM_HELP = '''JSON format for games:<br>
    [{"title":"game_title","description":"game_description"},...]<br>
    JSON format for items:<br>
    [{"game":"game_title","version":"game_version","price":key_price},...]<br><br>
    If there\'s no such game in database license key will not be added'''

    asd = models.FileField(verbose_name='item in JSON', upload_to='www/new_items')
    item_type = models.SmallIntegerField(verbose_name='item type',
                                         choices=((1, 'Games'),
                                                  (2, 'License keys')),
                                         default=1, help_text=NEW_ITEM_HELP)
    added = models.BooleanField(verbose_name='already in database',
                                default=False, editable=False)

    def add_to_db(self):
        if self.added: return
        items = json.load(self.asd)
        if self.item_type == 1: # if games
            for i in items:
                Game.objects.create(title=i['title'], description=i['description'])
        else: # if keys
            for i in items:
                if Game.objects.filter(title=i['game']).exists():
                    g = Game.objects.get(title=i['game'])
                    Item.objects.create(game=g, version=i['version'], price=i['price'])
        self.added = True
        self.save()
