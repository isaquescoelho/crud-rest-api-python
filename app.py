from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from flask import Flask, request, jsonify
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from itertools import count
from typing import Optional


server = Flask(__name__)
spec = FlaskPydanticSpec('Flask', title='People Database')
spec.register(server)
database = TinyDB('database.json')
score = count()


class Person(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(score))
    name: str
    age: int


class People(BaseModel):
    people: list[Person]
    count: int


@server.get('/people') # endpoint
@spec.validate(resp=Response(HTTP_200=People))
def get_people():
    """Return all people in the Database"""
    return jsonify(
        People(
            people = database.all(),
            count = len(database.all())
        ).dict()
    )


@server.post('/people')
@spec.validate(body=Request(Person), resp=Response(HTTP_201=Person))
def insert_people():
    """Insert People into the Database"""
    body = request.context.body.dict()
    database.insert(body)
    return body


@server.put('/people/<int:id>')
@spec.validate(
    body=Request(Person),
    resp=Response(HTTP_200=Person)
)
def change_person(id):
    """Change the database person's id"""
    Person = Query()
    body = request.context.body.dict()
    database.update(body, Person.id == id)
    return jsonify(body)


@server.delete('/people/<int:id>')
@spec.validate(resp=Response('HTTP_204'))
def delete_person(id):
    """Delete a person from the database by id"""
    Person = Query()
    database.remove(Person.id == id)
    return jsonify({})

server.run()
