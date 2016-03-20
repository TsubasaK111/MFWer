from sqlalchemy import ( Table, Column, ForeignKey, Integer, String,
                         DateTime, func )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

import pdb, logging

Base = declarative_base()


# Table for many to many relationship between Category and MFW
association_table = Table('association', Base.metadata,
    Column('MFW_id', Integer, ForeignKey('MFW.id')),
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
    name          = Column( String(40), nullable = False )
    description   = Column( String(100) )
    id            = Column( Integer, primary_key = True )
    creator_id    = Column( Integer, ForeignKey('user.id'), nullable = False )
    creation_date = Column( DateTime, default=func.now() )
    user          = relationship("User")

    # Many to many relationship with Puppy
    MFWs = relationship(
        "MFW",
        secondary = association_table,
        backref="categorys"
    )

    @property
    def serialize(self):
        #Returns object data in easily serializeable format.
        return {
            'name': self.name,
            'id': self.id,
            'creation_date': self.creation_date
        }


class MFW(Base):
    __tablename__ = 'MFW'
    name          = Column( String(20), nullable = False )
    description   = Column( String(100) )
    image_url     = Column( String(200) )
    reference_url = Column( String(200) )
    id            = Column( Integer, primary_key = True )
    creator_id    = Column( Integer, ForeignKey('user.id'), nullable = False )
    creation_date = Column( DateTime, default=func.now() )
    category_id   = Column( Integer, ForeignKey('category.id') )
    user          = relationship("User")
    element       = relationship( "Element", backref="MFW" )

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
    MFW_id        = Column( Integer, ForeignKey('MFW.id') )
    creation_date = Column( DateTime, default=func.now() )

    @property
    def serialize(self):
        #Returns object data in easily serializeable format.
        return { 'letter': self.letter,
                 'id': self.id,
                 'description': self.description,
                 'MFW_id': self.MFW_id,
                 'order': self.order,
                 'creation_date': self.creation_date
                }


engine = create_engine('sqlite:///MFWR.db')


Base.metadata.create_all(engine)


DatabaseSession = sessionmaker(bind = engine)


session = DatabaseSession()


# def before_flush(session, flush_context, instances):
#     """populate the "current_occupancy" column, prevent puppy overflows."""
#     logging.info( "\nnew flush! Session.new is: ", session.new )
#     for each in session.new:
#         logging.info( "__tablename__ is: ", each.__tablename__ )
#         if each.__tablename__ == "MFW":
#             logging.info( "each. is: ", each.shelter_id )
#             remaining_capacity, current_occupancy = remaining_capacity_counter(
#                                                             session,
#                                                             each.shelter_id)
#             if remaining_capacity - 1 < 0:
#                 puppies_on_hold.append(each)
#                 logging.warning( "shelter full! ", each, " will not be inserted." )
#                 logging.warning( "puppies_on_hold contains: ", puppies_on_hold )
#                 session.expunge(each)
#                 pdb.set_trace()
#             else:
#                 occupancy_update_result = session.execute("""
#                         UPDATE shelter
#                         SET current_occupancy = :current_occupancy
#                         WHERE id = :shelter_id
#                     """,
#                     {"current_occupancy": current_occupancy,
#                     "shelter_id": each.shelter_id}
#                     )
#                 logging.info( each.name, " has been put into: ", occupancy_update_result )
#
#
# event.listen(session, 'before_flush', before_flush)
