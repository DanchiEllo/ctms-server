from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

from database import Base, engine


class Crossroads(Base):
    __tablename__ = 'crossroads'

    id = Column(Integer, primary_key=True, index=True)
    coordinates = Column(String(50))
    move_time = Column(Float, nullable=True)

    cameras = relationship("Camera", back_populates="crossroad")
    traffic_lights = relationship("TrafficLight", back_populates="crossroad")
    intersecting_streets = Column(JSON)


class Camera(Base):
    __tablename__ = 'cameras'

    id = Column(Integer, primary_key=True, index=True)
    channels = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    uri = Column(String(255))
    crossroad_id = Column(Integer, ForeignKey('crossroads.id'))
    crossroad = relationship("Crossroads", back_populates="cameras")
    areas = relationship("Area", back_populates="camera")


class TrafficLight(Base):
    __tablename__ = 'traffic_lights'

    id = Column(Integer, primary_key=True, index=True)
    uri = Column(String(255))
    crossroad_id = Column(Integer, ForeignKey('crossroads.id'))
    crossroad = relationship("Crossroads", back_populates="traffic_lights")
    traffic_light_area = relationship("Area", uselist=False, back_populates="traffic_light")


class Area(Base):
    __tablename__ = 'areas'

    id = Column(Integer, primary_key=True, index=True)
    coordinates = Column(JSON)
    mask_id = Column(Integer, ForeignKey('masks.id'))
    camera_id = Column(Integer, ForeignKey('cameras.id'))
    camera = relationship("Camera", back_populates="areas")
    mask = relationship("Mask", uselist=False, back_populates="area")
    traffic_light_id = Column(Integer, ForeignKey('traffic_lights.id'))
    traffic_light = relationship("TrafficLight", back_populates="traffic_light_area")


class Mask(Base):
    __tablename__ = 'masks'

    id = Column(Integer, primary_key=True, index=True)
    x = Column(Integer)
    y = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    area = relationship("Area", uselist=False, back_populates="mask")


Base.metadata.create_all(engine)
