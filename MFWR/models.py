from sqlalchemy import ( Table, Column, ForeignKey, Integer, String,
                         DateTime, func, UniqueConstraint )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

import pdb, logging

Base = declarative_base()


# Table for many to many relationship between Category and MFW
MFWs_Categories = Table('mfws_categories', Base.metadata,
    Column('mfw_id', Integer, ForeignKey('mfw.id')),
    Column('category_id', Integer, ForeignKey('category.id'))
)


class User(Base):
    __tablename__ = 'user'
    name          = Column( String(80), nullable = False )
    email         = Column( String() )
    picture       = Column( String() )
    link          = Column( String() )
    google_plus_id= Column( String() )
    id            = Column( Integer, primary_key = True )
    creation_date = Column( DateTime, default=func.now() )


class Category(Base):
    __tablename__ = 'category'
    name          = Column( String(40), nullable = False, unique = True )
    description   = Column( String(100) )
    id            = Column( Integer, primary_key = True )
    creator_id    = Column( Integer,
                            ForeignKey('user.id'),
                            nullable = False )
    creation_date = Column( DateTime, default=func.now() )
    user          = relationship("User")

    # Many to many relationship with MFW
    mfws = relationship( "MFW",
                         secondary = MFWs_Categories,
                         back_populates="categories" )

    @property
    def serialize(self):
        #Returns object data in easily serializeable format.
        return {
            'name': self.name,
            'id': self.id,
            'creation_date': self.creation_date
        }


class MFW(Base):
    __tablename__ = 'mfw'
    name          = Column( String(20), nullable = False, unique = True )
    description   = Column( String(100) )
    image_url     = Column( String(200) )
    reference_url = Column( String(200) )
    id            = Column( Integer, primary_key = True )
    creator_id    = Column( Integer, ForeignKey('user.id'), nullable = False )
    creation_date = Column( DateTime, default=func.now() )
    user          = relationship("User")
    elements       = relationship( "Element", backref="mfw" )

    # Many to many relationship with Category
    categories = relationship( "Category",
                               secondary = MFWs_Categories,
                               back_populates="mfws" )

    @property
    def serialize(self):
        #Returns object data in easily serializeable format.
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'image_url': self.image_url,
            'reference_url': self.reference_url,
            'creation_date': self.creation_date
        }


class Element(Base):
    __tablename__ = 'element'
    letter        = Column( String(1), nullable = False )
    description   = Column( String(250) )
    order         = Column( Integer )
    id            = Column( Integer, primary_key = True )
    mfw_id        = Column( Integer, ForeignKey('mfw.id') )
    creation_date = Column( DateTime, default=func.now() )

    @property
    def serialize(self):
        #Returns object data in easily serializeable format.
        return { 'letter': self.letter,
                 'id': self.id,
                 'description': self.description,
                 'mfw_id': self.mfw_id,
                 'order': self.order,
                 'creation_date': self.creation_date
                }


engine = create_engine('sqlite:///MFWR.db')


Base.metadata.create_all(engine)


DatabaseSession = sessionmaker(bind = engine)


session = DatabaseSession()
