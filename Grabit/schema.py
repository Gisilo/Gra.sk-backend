from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Grabit


# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)
class GrabitNode(DjangoObjectType):
    class Meta:
        model = Grabit
        filter_fields = ['name_project', 'name_db', 'created_date', 'update_date']
        interfaces = (relay.Node, )


class Query(ObjectType):
    grabit = relay.Node.Field(GrabitNode)
    all_grabits = DjangoFilterConnectionField(GrabitNode)