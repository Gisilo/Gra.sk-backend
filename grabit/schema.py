
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import django_filters
from django.contrib.auth.models import User
from .models import Grabit
from django.db.models import Q


# Graphene will automatically map the Grabit model's fields onto the GrabitNode.
# This is configured in the GrabitNode's Meta class (as you can see below)
class GrabitNode(DjangoObjectType):

    id = graphene.ID(source='pk', required=True)

    class Meta:
        model = Grabit
        filter_fields = ['id', 'owner']
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):

    get_grabits_by_id_and_owner = graphene.List(GrabitNode, id=graphene.String(), owner=graphene.String())
    get_grabits_of_owner = graphene.List(GrabitNode, owner=graphene.String())
    all_grabits = DjangoFilterConnectionField(GrabitNode)


    def resolve_get_grabits_by_id_and_owner(self, info, id, owner):
        user_owner = User.objects.get(pk=int(owner))
        filter = (Q(id__exact = id) & Q(owner__exact = user_owner))
        return Grabit.objects.filter(filter)

    def resolve_get_grabits_of_owner(self, info, owner):
        user_owner = User.objects.get(pk=int(owner))
        filter = Q(owner__exact=user_owner)
        return Grabit.objects.filter(filter)


class CreateGrabit(graphene.relay.ClientIDMutation):
    msg = graphene.String()
    grabit = graphene.Field(GrabitNode)

    class Input:
        id = graphene.String()
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
        description = input.get("description")
        name = input.get("name")

        try:
            print(f"prima user {graph}", flush=True)
            user_owner = User.objects.get(pk=int(owner))
            new_grabit, created = cls.add_grabit(id=id, name=name,
                                                 owner=user_owner, graph=graph, description=description)

            msg = f"Created new grabit {id}" if created else f"Updated grabit {id}"
            return CreateGrabit(msg=msg, grabit=new_grabit)
        except Exception as e: 
            print(f"Error when creating or updating grabit {id}. {e}", flush=True)
            return CreateGrabit(msg=f"Can't create or update grabit {id}")

    @classmethod
    def add_grabit(self, owner, name, id=None, description=None, graph=None):
        if not id:
            return self.create_grabit(name, owner, description, graph)
        else:
            return self.update_grabit(id, owner, graph, description)

        '''
        if graph is None:
            return self.create_grabit(id, owner, description)
        else:
            return self.update_grabit(id, owner, graph, description)
        '''

    @classmethod
    def create_grabit(self, name, owner, description, graph):
        new_values = {'name': name, 'owner': owner, 'description': description, 'graph': graph}
        obj = Grabit(**new_values)
        obj.save()
        return obj, True

    @classmethod
    def update_grabit(self, id, owner, graph, description):
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
