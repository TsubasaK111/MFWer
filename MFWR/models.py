from sqlalchemy import ( Table, Column, ForeignKey, Integer, String,
                         DateTime, func )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

Base = declarative_base()


# Table for many to many relationship between Category and MFW
association_table = Table('association', Base.metadata,
    Column('MFW_id', Integer, ForeignKey('MFW.id')),
    Column('Category_id', Integer, ForeignKey('Category.id'))
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
    __tablename__ = 'Category'
    Name          = Column( String(20), nullable = False )
    id            = Column( Integer, primary_key = True )
    creator_id    = Column( Integer, ForeignKey('user.id'), nullable = False )
    creation_date = Column( DateTime, default=func.now() )
    user          = relationship("User")

    # Many to many relationship with Puppy
    MFWs = relationship(
        "MFW",
        secondary = association_table,
        backref="categories"
    )

class MFW(Base):
    __tablename__ = 'MFW'
    name          = Column( String(20), nullable = False )
    description   = Column( String(100) )
    image_url     = Column( String(200) )
    reference_url = Column( String(200) )
    id            = Column( Integer, primary_key = True )
    creator_id    = Column( Integer, ForeignKey('user.id'), nullable = False )
    creation_date = Column( DateTime, default=func.now() )
    user          = relationship("User")
    element       = relationship( "Element", backref="MFW" )

    @property
    def serialize(self):
        #Returns object data in easily serializeable format.
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'creator_id': self.creator_id,
            'image_url': self.image_url,
            'reference_url': self.reference_url
        }

class Element(Base):
    __tablename__ = 'element'
    letter        = Column( String(1), nullable = False )
    description   = Column( String(250) )
    order         = Column( Integer )
    id            = Column( Integer, primary_key = True )
    MFW_id        = Column( Integer, ForeignKey('MFW.id') )
    creation_date = Column( DateTime, default=func.now() )

    @property
    def serialize(self):
        #Returns object data in easily serializeable format.
        return { 'letter': self.letter,
                 'id': self.id,
                 'description': self.description,
                 'MFW_id': self.MFW_id
                }


engine = create_engine('sqlite:///MFWR.db')


Base.metadata.create_all(engine)


DatabaseSession = sessionmaker(bind = engine)


session = DatabaseSession()
