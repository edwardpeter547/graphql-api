from fastapi import FastAPI
from graphene import Schema
from starlette_graphene3 import GraphQLApp, make_playground_handler
from app.gql.queries import Query
from app.gql.mutations import Mutations
from app.db.database import prepare_database, Session
from app.db.models import Employer, Job


schema = Schema(query=Query, mutation=Mutations)

app = FastAPI(debug=True)

@app.on_event("startup")
def start_up():
    prepare_database()

app.mount("/", GraphQLApp(schema=schema, on_get=make_playground_handler()))
