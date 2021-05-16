# Generated by Django 2.2.12 on 2020-05-30 09:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_token', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=100, verbose_name='title')),
                ('description', models.CharField(default='', max_length=255, verbose_name='description')),
                ('img', models.ImageField(blank=True, default='www/games/new.jpg', upload_to='www/games', verbose_name='description')),
            ],
        ),
        migrations.CreateModel(
            name='NewItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asd', models.FileField(upload_to='www/new_items', verbose_name='item in JSON')),
                ('item_type', models.SmallIntegerField(choices=[(1, 'Games'), (2, 'License keys')], default=1, help_text='JSON format for games:<br>[{"title":"game_title","description":"game_description"},...]<br>for items:<br>[{"game":"game_title","version":"game_version","price":key_price},...]<br>if there\'s no such game in database license key will not be added', verbose_name='item type')),
                ('added', models.BooleanField(default=False, editable=False, verbose_name='already in database')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Cart')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(1, 'Pending'), (2, 'Completed'), (3, 'Cancelled')], default=1, verbose_name='Status')),
                ('total', models.FloatField(default=0, verbose_name='total')),
                ('items', models.CharField(default='', max_length=1000, verbose_name='Items')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(default='', max_length=100, verbose_name='version')),
                ('price', models.FloatField(default=0, verbose_name='price')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Game')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=1, null=True, verbose_name='amount')),
                ('cart', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Cart')),
                ('ref', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Item')),
            ],
        ),
    ]