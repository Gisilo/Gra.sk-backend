from __future__ import unicode_literals


from django.db import models
from jsonfield import JSONField


# Create your models here.


class Grabit(models.Model):

    DBMS = (('MySQL', 'MySQL'), ('SQLite', 'SQLite'), ('Neo4j', 'Neo4j'))

    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name_project = models.CharField(unique=True, max_length=200)
    name_db = models.CharField(max_length=200, null=True)
    dbms = models.CharField(max_length=6, choices=DBMS, null=True)
    description = models.TextField(blank=True, null=True)
    port = models.IntegerField(null=True, blank=True)
    #folder = models.FilePathField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    graph = JSONField(default=list)

    #p = Project(name_project='Manager', name_db='ManagerDB', dbms='SQLite', description='Database del manager del sistema', port=8000, folder='C:\\Users\\Utente\\Desktop\\django\\serverdb\\manager', graph=None)


    def __str__(self):
        return self.name_project

