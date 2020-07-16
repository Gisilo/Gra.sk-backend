
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import django_filters
from django.contrib.auth.models import User
from .models import Grabit

class GrabitFilter(django_filters.FilterSet):
    # Do case-insensitive lookups on 'name'
    id = django_filters.LookupChoiceFilter(lookup_choices=[('exact', 'Equals'),])
    owner = django_filters.LookupChoiceFilter(lookup_choices=[('exact', 'Equals'),])

    class Meta:
        model = Grabit
        fields = ['id', 'owner']

# Graphene will automatically map the Grabit model's fields onto the GrabitNode.
# This is configured in the GrabitNode's Meta class (as you can see below)
class GrabitNode(DjangoObjectType):

    id = graphene.ID(source='pk', required=True)

    class Meta:
        model = Grabit
        filterset_class=GrabitFilter
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    grabit = graphene.relay.Node.Field(GrabitNode)
    all_grabits = DjangoFilterConnectionField(GrabitNode)

class CreateGrabit(graphene.relay.ClientIDMutation):
    msg = graphene.String()
    grabit = graphene.Field(GrabitNode)

    class Input:
        id = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()
        creation_date = graphene.DateTime()
        update_date = graphene.DateTime()
        graph = graphene.String()
        owner = graphene.String(required=True)


    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):

        id = input.get("id")
        owner = input.get("owner")
        graph = input.get("graph")
        try:
            print(f"prima user {graph}", flush=True)
            user_owner = User.objects.get(pk=int(owner))
            new_grabit, created = cls.add_grabit(id=id, owner=user_owner, graph=graph)
            print(f"sssssssssssssss {graph}", flush=True)
            msg = f"Created new grabit {id}" if created else f"Updated grabit {id}"
            return CreateGrabit(msg=msg, grabit=new_grabit)
        except Exception as e: 
            print(f"Error when creating or updating grabit {id}. {e}", flush=True)
            return CreateGrabit(msg=f"Can't create or update grabit {id}")

    @classmethod
    def add_grabit(self, id, owner, graph=None):
        if graph is None:
            return self.create_grabit(id, owner)
        else:
            return self.update_grabit(id, owner, graph)

    @classmethod
    def create_grabit(self, id, owner):
        return Grabit.objects.update_or_create(id=id, owner=owner)

    @classmethod
    def update_grabit(self, id, owner, graph):
        return Grabit.objects.update_or_create(id=id, owner=owner, defaults={'graph': graph})


class DeleteGrabit(graphene.relay.ClientIDMutation):
    msg = graphene.Field(type=graphene.String)
    grabit = graphene.Field(GrabitNode)

    class Input:
        name = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        obj = Grabit.objects.get(name=input["name"])
        try:
            obj.delete()
            msg = "Successful delete project {}".format(input["name"])
        except:
            msg = "Can't delete project {}".format(input["name"])
        print(msg)
        return DeleteGrabit(msg=msg, grabit=obj)


class Mutation(graphene.AbstractType):
    create_grabit = CreateGrabit.Field()
    delete_grabit = DeleteGrabit.Field()
