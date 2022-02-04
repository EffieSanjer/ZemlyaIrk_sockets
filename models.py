# from sqlalchemy import create_engine
# engine = create_engine(
#     "postgresql+psycopg2://postgres:password@localhost/postgres",
#     echo=True, pool_size=6
# )
# engine.connect()
import binascii
import os
import hashlib

from sqlalchemy import create_engine, Integer, String, \
    Column, Date, ForeignKey, Numeric, Index, Boolean, inspect, exc
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from exceptions import *
from uuid import uuid4


from sqlalchemy.orm import Session, sessionmaker, relationship

# engine = create_engine("postgresql+psycopg2://postgres:pass@localhost/postgres")
engine = create_engine("sqlite:///data_base.db")

Base = declarative_base()
session = Session(bind=engine)
salt = uuid4().hex

def object_to_dict(obj):
    return {x.name: getattr(obj, x.name)
    for x in obj.__table__.columns}

def object_exists(p):
    if p is None:
       raise NotFoundError

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
        del json['data']['password']
        del json['data']['email']
        json['data']['full_name'] = p.full_name
        return json

    def add_client(json):
        p = People()
        # p.__dict__.update(json['data'])
        p = People(**json['data'])

        #dict(p)
        # p.full_name = json['data']['full_name']
        # p.phone1 = json['data']['phone1']
        # p.phone2 = json['data']['phone2']
        # p.email = json['data']['email']
        p.is_client = True
        p.self_registration = True
        # p.password = json['data']['password']
        p.token = binascii.hexlify(os.urandom(20)).decode()  # RANDOM

        try:
            session.add(p)
            session.commit()
            json['token'] = p.token
            json['data']['id'] = p.id
            json['status'] = '200'
            json['message'] = ''
        except:
            session.rollback()
            json['status'] = '500'
            json['message'] = 'Ошибка сервера'
        return json

    def edit_client(json):
        p = session.query(People).filter(People.token == json['token']).first()
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
            json['status'] = '200'
            json['message'] = 'Client (id: ' + str(p.id) + ') is edited!'
        except:
            session.rollback()
            json['status'] = '500'
            json['message'] = 'Ошибка сервера!'
        return json

    def delete_client(json):
        try:
            p = session.query(People).filter(People.token == json['token']).first()
            if p is None:
                raise DeletedError
            p.date_delete = datetime.today()
            session.add(p)
            session.commit()
            json['status'] = '200'
            json['message'] = 'Client ' + str(p.id) + ' is deleted'
        except DeletedError as e:
            session.rollback()
            json['status'] = e.status
            json['message'] = e.message
        # except AttributeError:
        #     print('AAAAAAAA')
        return json

    def get_client(json):
        try:
            p = session.query(People).filter(People.token == json['token']).first()

            object_exists(p)
            json['status'] = '200'
            json['data'] = object_to_dict(p)
        except:
            json['status'] = '500'
            json['message'] = 'Ошибка сервера!'

        # json['data']['full_name'] = p.full_name
        # json['data']['phone1'] = p.phone1
        # json['data']['phone2'] = p.phone2
        # json['data']['email'] = p.email
        # json['data']['password'] = p.password

        return json

    def get_client_objects(json):
        try:
            p = session.query(People).filter(People.token == json['token']).first() # client P

            object_exists(p)
            clients_objects = list(filter(lambda x: x.date_delete == None, p.user_objects))

            # clients_objects = p.user_objects

            objects = []
            for o in clients_objects:  # iterate objects
                # obj = vars(o)
                obj = object_to_dict(o)
                # for key in obj.keys():
                #     if key.startswith('_'):
                #         obj.pop(key)
                #         break
                objects.append(obj)  # add to list

            #json['data'] = p
            json['data']['objects'] = objects
            json['status'] = '200'
        except:
            json['status'] = '500'
            json['message'] = 'Ошибка сервера!'
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

    loc_objects = relationship("Objects", foreign_keys=[id], primaryjoin="Objects.locality_id == Localities.id", back_populates="locality")
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
    locality = relationship("Localities", foreign_keys=[locality_id], primaryjoin="Objects.locality_id == Localities.id")
    parent = relationship("Localities", foreign_keys=[parent_id], primaryjoin="Objects.parent_id == Localities.id")
    # parent = relationship("Localities", foreign_keys='parent_id', back_populates="parent_loc_objects",  lazy='select')


Base.metadata.create_all(engine)
print(engine)
