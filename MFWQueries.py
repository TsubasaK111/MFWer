from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, MFW, element

engine = create_engine('sqlite:///MFWmenu.db')

Base.metadata.bind = engine
DatabaseSession = sessionmaker(bind = engine)
session = DatabaseSession()

dishes = session.query(element).all()
for dish in dishes:
    print 'working,...'
    print dish.name
    print "\n"
    print "\n"

MFWs = session.query(MFW).all()
for MFW in MFWs:
    print MFW.name
