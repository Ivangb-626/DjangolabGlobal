# Generated manually on 2026-05-03

import django.db.models.deletion
from django.db import migrations, models


def migrar_voto_unico_a_varios(apps, schema_editor):
    Votante = apps.get_model('polls', 'Votante')
    Filma = apps.get_model('polls', 'Filma')

    for votante in Votante.objects.exclude(pelicula__isnull=True):
        votante.peliculas.add(votante.pelicula_id)

    for filma in Filma.objects.all():
        filma.bozkak = filma.votantes.count()
        filma.save(update_fields=['bozkak'])


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0006_pelicula_votante_delete_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Pelicula',
            new_name='Filma',
        ),
        migrations.RenameField(
            model_name='filma',
            old_name='titulo',
            new_name='izenburua',
        ),
        migrations.AddField(
            model_name='filma',
            name='bozkak',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='filma',
            name='generoa',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='filma',
            name='sinopsia',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='filma',
            name='urtea',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='filma',
            name='zuzendaria',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='votante',
            name='peliculas',
            field=models.ManyToManyField(blank=True, related_name='votantes', to='polls.filma'),
        ),
        migrations.RunPython(migrar_voto_unico_a_varios, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='votante',
            name='pelicula',
        ),
    ]
