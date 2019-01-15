from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    """required for JSON response"""
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'picture': self.picture,
        }


class MusicCategory(Base):
    __tablename__ = 'music_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(String(250))

    """required for JSON response"""
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


class Song(Base):
    __tablename__ = 'song'

    id = Column(Integer, primary_key=True)
    band = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    lyrics = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey('music_category.id'))
    music_category = relationship(MusicCategory)
    __table_args__ = (UniqueConstraint('band', 'name', name='_band_song_uc'),)

    """required for JSON response"""
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'band': self.band,
            'name': self.name,
            'lyrics': self.lyrics,
        }

engine = create_engine('sqlite:///lyricscatalog.db')


Base.metadata.create_all(engine)
