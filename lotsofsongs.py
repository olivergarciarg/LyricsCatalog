from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbmodel import User, Base, MusicCategory, Song

engine = create_engine('sqlite:///lyricscatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Add 1 user
user1 = User(name="Oliver", email="oojjgg@gmail.com", picture="")
session.add(user1)
session.commit()


category1 = MusicCategory(name="Rock", description="broad genre of popular music that originated as 'rock and roll' in the United States in the early 1950s, and developed into a range of different styles in the 1960s")
session.add(category1)
session.commit()

song1 = Song(name="Chop Suey", band = "System of a down", lyrics="Wake up \
    Grab a brush and put a little (makeup)\
    Grab a brush and put a little\
    Hide the scars to fade away the (shakeup)\
    Hide the scars to fade away the\
    Why'd you leave the keys upon the table?\
    Here you go create another fable\
    You wanted to\
    Grab a brush and put a little makeup\
    You wanted to\
    Hide the scars to fade away the shakeup\
    You wanted to\
    Why'd you leave the keys upon the table?\
    You wanted to"
    , user=user1, music_category=category1)
session.add(song1)
session.commit()

category2 = MusicCategory(name="Pop Rock", description="rock music with a greater emphasis on professional songwriting and recording craft, and less emphasis on attitude")
session.add(category2)
session.commit()

song2 = Song(name="So Alive", band = "Goo Goo Dolls", lyrics="Feeling like a hero, but I can't fly\
    No, you never crash if you don't try\
    Took it to the edge, now I know why\
    Never gonna live if you're too scared to die\
    Gonna disconnect from the hardwire\
    Time to raise a flag for the ceasefire\
    Staring down the hole inside me\
    Looking in the mirror\
    Making peace with the enemy..."
    , user=user1, music_category=category2)
session.add(song2)
session.commit()

category3 = MusicCategory(name="Punk rock", description="rock music genre that developed in the mid-1970s in the United States, United Kingdom, and Australia. Rooted in 1960s garage rock and other forms of what is now known as 'proto-punk' music")
session.add(category3)
session.commit()

song3 = Song(name="London Calling", band = "The Clash", lyrics="London calling to the faraway towns\
    Now war is declared and battle come down\
    London calling to the underworld\
    Come out of the cupboard, you boys and girls\
    London calling now don't look to us\
    Phony Beatlemania has bitten the dust\
    London calling see we ain't got no swing\
    'Cept for the ring of that truncheon thing"
    , user=user1, music_category=category3)
session.add(song3)
session.commit()

category4 = MusicCategory(name="Blues", description="music genre and musical form originated by African Americans in the Deep South of the United States around the end of the 19th century")
session.add(category4)
session.commit()

song4 = Song(name="Mannish Boy", band = "Muddy Waters",  lyrics="Oh, yeah\
    Oh, yeah\
    Everything gonna be alright this mornin'\
    Now, when I was a young boy\
    At the age of five\
    My mother said I was gonna be\
    The greatest man alive\
    But now I'm a man\
    I'm age twenty-one\
    I want you to believe me, honey\
    We having lots of fun"\
    , user=user1, music_category=category4)
session.add(song4)
session.commit()


print ("added menu items!")