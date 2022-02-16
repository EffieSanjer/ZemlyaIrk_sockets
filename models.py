import binascii
import os
import hashlib
import redis
import yaml

from sqlalchemy import create_engine, Integer, String, \
    Column, Date, ForeignKey, Numeric, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, relationship
from datetime import datetime
from exceptions import *
from uuid import uuid4
import configparser

with open('settings') as conf:
    # config = configparser.ConfigParser()
    config = yaml.safe_load(conf)
# config.read("settings.ini")
red = redis.Redis(host='127.0.0.1', port=7890)

Base = declarative_base()
session = Session(bind=create_engine(config['engine_sqlite']))
# engine = create_engine("sqlite:///data_base.db")
salt = config['salt']

def object_to_dict(obj):
    return {x.name: round(getattr(obj, x.name), 2)
    if (isinstance(x.type, Numeric)) and (getattr(obj, x.name) != None) and
       (x.name != 'latitude' and x.name != 'longitude')
    else getattr(obj, x.name) for x in obj.__table__.columns}

def object_exists(p):
    if p is None:
        raise NotFoundError

def is_login(func):
    def checking(json):
        # print(red.get(json['token']))
        try:
            return func(json, red.get(json['token']).decode())
        except:
            raise UnauthorizedError
    return checking

#################################################

class People(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    phone1 = Column(String(11), nullable=False)
    phone2 = Column(String(11), nullable=True)
    email = Column(String(100), nullable=True)
    is_client = Column(Boolean, nullable=False)
    position = Column(String(100), nullable=True)
    role_id = Column(Integer, nullable=True)
    comment = Column(String(250), nullable=True)
    photo = Column(String(200), nullable=True)
    self_registration = Column(Boolean, nullable=True)
    password = Column(String(200), nullable=False)
    token = Column(String(250), nullable=False)
    emp_id = Column(Integer, nullable=True)
    date_delete = Column(Date(), nullable=True)
    user_objects = relationship("Objects", back_populates="seller")
    client_searches = relationship("Searches", back_populates="client")
    favourite = relationship("Objects", secondary="favourites")

    __table_args__ = (
        Index('token_idx', 'token'),
        Index('delete_person_idx', 'date_delete')
    )

    def sign_in(json):
        salted = hashlib.sha256(json['data']['password'].encode() + salt.encode()).hexdigest()
        p = session.query(People).filter(People.email == json['data']['email'],
                                         People.password == salted,
                                         People.date_delete == None).first()
        object_exists(p)
        json['token'] = p.token
        red.set(p.token, p.id, ex=60)
        del json['data']['password']
        del json['data']['email']
        json['data']['full_name'] = p.full_name
        return json

    def add_client(json):
        p = People()
        salted = hashlib.sha256(json['data']['password'].encode() + salt.encode()).hexdigest()
        json['data']['password'] = salted
        p = People(**json['data'])

        p.is_client = True
        p.self_registration = True
        p.token = binascii.hexlify(os.urandom(20)).decode()  # RANDOM

        try:
            session.add(p)
            session.commit()
            json['data'] = {}
            red.set(p.token, p.id, ex=60)
            json['token'] = p.token
            json['data']['full_name'] = p.full_name
        except:
            session.rollback()
            raise InternalServerError
        return json

    @is_login
    def edit_client(json, id):
        # p = session.query(People).filter(People.token == json['token']).first()
        p = session.query(People).get(id)
        # p = People(**json['data'])

        object_exists(p)
        p.full_name = json['data']['full_name']
        p.phone1 = json['data']['phone1']
        p.phone2 = json['data']['phone2']
        p.email = json['data']['email']
        p.password = json['data']['password']

        try:
            session.add(p)
            session.commit()
            json['data'] = {}
        except:
            session.rollback()
            raise InternalServerError
        return json

    @is_login
    def delete_client(json, id):
        try:
            # p = session.query(People).filter(People.token == json['token']).first()
            p = session.query(People).get(id)
            if p is None:
                raise DeletedError
            p.date_delete = datetime.today()
            session.add(p)
            session.commit()
            del json['token']
        except DeletedError as e:
            session.rollback()
            json['status'] = e.status
            json['message'] = e.message
        except:
            session.rollback()
            raise InternalServerError
        return json

    @is_login
    def get_client(json, id):
        try:
            # p = session.query(People).filter(People.token == json['token']).first()
            p = session.query(People).get(id)
            object_exists(p)
            json['data'] = object_to_dict(p)
        except:
            session.rollback()
            raise InternalServerError
        return json

    @is_login
    def get_client_objects(json, id):
        try:
            # p = session.query(People).filter(People.token == json['token']).first()
            p = session.query(People).get(id)
            object_exists(p)
            clients_objects = list(filter(lambda x: x.date_delete == None, p.user_objects))
            # fav = p.favourite
            # s = p.client_searches
            objects = []

            for o in clients_objects:
                obj = object_to_dict(o)
                objects.append(obj)

            json['data']['objects'] = objects
        except:
            session.rollback()
            raise InternalServerError
        return json

    @is_login
    def get_client_favourites(json, id):
        try:
            # p = session.query(People).filter(People.token == json['token']).first()
            p = session.query(People).get(id)
            object_exists(p)
            c_fav = p.favourite
            objects = []

            for o in c_fav:
                obj = object_to_dict(o)
                objects.append(obj)

            json['data']['favourites'] = objects
        except:
            session.rollback()
            raise InternalServerError
        return json

    def sign_out(json):
        del json['token']
        json['data'] = {}
        return json


class Localities(Base):
    __tablename__ = 'localities'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    show_name = Column(String(100), nullable=False)
    type = Column(Integer, nullable=False)
    distance = Column(Numeric, nullable=True)
    description = Column(String(250), nullable=True)
    latitude = Column(Numeric, nullable=False)
    longitude = Column(Numeric, nullable=False)
    photos = Column(String(250), nullable=True)
    date_delete = Column(String(100), nullable=True)

    loc_objects = relationship("Objects", foreign_keys=[id], primaryjoin="Objects.locality_id == Localities.id",
                               back_populates="locality")
    # parent_loc_objects = relationship("Objects", back_populates="parent", lazy='select')


class Objects(Base):
    __tablename__ = 'objects'
    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    seller_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    locality_id = Column(Integer, ForeignKey('localities.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('localities.id'), nullable=False)
    distance = Column(Numeric, nullable=True, default=0)
    address = Column(String(200), nullable=False)
    area = Column(Numeric, nullable=False)
    object_area = Column(Numeric, nullable=True)
    other_objects = Column(String(250), nullable=True)
    description = Column(String(250), nullable=True)
    date_update = Column(String(100), nullable=True, default=datetime.today())
    cadast_num = Column(String(20), nullable=True)
    rating = Column(Integer, nullable=True)
    status = Column(Integer, nullable=True)
    posession = Column(String(250), nullable=True)
    purpose = Column(String(250), nullable=True)
    source = Column(String(100), nullable=True)
    link = Column(String(200), nullable=True)
    resp_emp = Column(Integer, nullable=True)
    cost = Column(Numeric, nullable=False)
    comission = Column(Numeric, nullable=False)
    price_conditions = Column(String(250), nullable=True)
    good_price = Column(Boolean, nullable=True, default=False)
    bargain = Column(Boolean, nullable=True, default=False)
    invest_attract = Column(Boolean, nullable=True, default=False)
    latitude = Column(Numeric, nullable=False)
    longitude = Column(Numeric, nullable=False)
    date_delete = Column(String(100), nullable=True)

    seller = relationship("People", back_populates="user_objects")
    locality = relationship("Localities", foreign_keys=[locality_id],
                            primaryjoin="Objects.locality_id == Localities.id")
    parent = relationship("Localities", foreign_keys=[parent_id], primaryjoin="Objects.parent_id == Localities.id")
    # parent = relationship("Localities", foreign_keys='parent_id', back_populates="parent_loc_objects",  lazy='select')


class Searches(Base):
    __tablename__ = 'searches'
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    query = Column(String(300), nullable=False)
    client_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    date = Column(String(100), nullable=False, default=datetime.today())
    count = Column(Integer, nullable=False, default=0)

    client = relationship("People", back_populates="client_searches")


class Favourites(Base):
    __tablename__ = 'favourites'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('people.id'), nullable=False)
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    date_add = Column(String(100), nullable=False, default=datetime.today())

    # client_fav = relationship("People", back_populates="favourite")
    # client_fav = relationship("People", back_populates="favourite")

# Base.metadata.create_all(engine)
