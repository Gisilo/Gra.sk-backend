from django.test import TestCase
from grabit.models import Grabit
import json
from django.test import TestCase
from django.test import Client

# Inherit from this in your test cases
class GraphQLTestCase(TestCase):

    def setUp(self):
        Grabit.objects.create(name_project="pro_prova_1")
        Grabit.objects.create(name_project="pro_prova_2")
        self._client = Client()

    def query(self, query: str, op_name: str = None, input: dict = None):
        '''
        Args:
            query (string) - GraphQL query to run
            op_name (string) - If the query is a mutation or named query, you must
                               supply the op_name.  For annon queries ("{ ... }"),
                               should be None (default).
            input (dict) - If provided, the $input variable in GraphQL will be set
                           to this value

        Returns:
            dict, response from graphql endpoint.  The response has the "data" key.
                  It will have the "error" key if any error happened.
        '''
        body = {'query': query}
        if op_name:
            body['operation_name'] = op_name
        if input:
            body['variables'] = {'input': input}

        resp = self._client.post('/graphql', json.dumps(body),
                                 content_type='application/json')
        jresp = json.loads(resp.content.decode())
        return jresp

    def assertResponseNoErrors(self, resp: dict, expected: dict):
        '''
        Assert that the resp (as retuened from query) has the data from
        expected
        '''
        self.assertNotIn('errors', resp, 'Response had errors')
        self.assertEqual(resp['data'], expected, 'Response has correct data')

    def test_query_grabit(self):
        resp = self.query(
            # The mutation's graphql code
            '''
            query GrabitIDAndName{
              allGrabits{
                edges{
                  node{
                    nameProject
                  }
                }
                
              }
            }
            ''',
            # The operation name (from the 1st line of the mutation)
            op_name='GrabitIDAndName'
        )
        exp = {
            "allGrabits": {
              "edges": [
                {
                  "node": {
                    "nameProject": "pro_prova_1"
                  }
                },
                {
                  "node": {
                    "nameProject": "pro_prova_2"
                  }
                }
              ]
            }
        }
        self.assertResponseNoErrors(resp, exp)

    def test_create_grabit(self):
        resp = self.query(
            # The mutation's graphql code
            '''
            mutation CreateGrabitByName{
              createGrabit(
                input: {
                  nameProject: "pro_create_mutation1"
                }
              ){grabit{
                nameProject
              }
              }
            }
            ''',
            # The operation name (from the 1st line of the mutation)
            op_name='CreateGrabitByName'
        )
        exp = {
            "createGrabit": {
              "grabit": {
                "nameProject": "pro_create_mutation1"
              }
            }
        }
        self.assertResponseNoErrors(resp, exp)

    def test_delete_grabit(self):
        resp = self.query(
            # The mutation's graphql code
            '''
            mutation DeleteGrabitByName{
                    deleteGrabit(
                        input: {
                            nameProject: "pro_prova_1"
                    }){
                        msg
                    }
                }
            ''',
            # The operation name (from the 1st line of the mutation)
            op_name='DeleteGrabitByName'
        )
        exp = {
            "deleteGrabit": {
                "msg": "Successful delete project pro_prova_1"
            }
        }
        self.assertResponseNoErrors(resp, exp)






