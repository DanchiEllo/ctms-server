from typing import List, Optional, Annotated

from fastapi import FastAPI, Response, Request, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

import models_db
from database import SessionLocal

app = FastAPI()

fake_crossroads = []


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class Mask(BaseModel):
    x: int
    y: int
    width: int
    height: int

class TrafficLight(BaseModel):
    id: int
    uri: str

class Area(BaseModel):
    id: int
    coordinates: List[List[int]]
    mask: Mask
    traffic_light: TrafficLight

class Camera(BaseModel):
    id: int
    channels: int
    width: int
    height: int
    uri: HttpUrl
    areas: List[Area]


class Crossroad(BaseModel):
    cameras: List[Camera]
    traffic_lights: List[TrafficLight]
    intersecting_streets: List[str]
    coordinates: str
    move_time: Optional[float]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "BAD_REQUEST"},
    )


@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=400,
        content={"detail": "BAD_REQUEST"},
    )


@app.post("/crossroad")
async def add_crossroad(response: Response, crossroad: Crossroad, db: Session = Depends(get_db)):
    response.status_code = 201
    new_crossroad = models_db.Crossroads(
        intersecting_streets=crossroad.intersecting_streets,
        coordinates=crossroad.coordinates,
        move_time=crossroad.move_time
    )
    db.add(new_crossroad)
    db.flush()

    for camera in crossroad.cameras:
        new_camera = models_db.Camera(
            channels=camera.channels,
            width=camera.width,
            height=camera.height,
            uri=camera.uri,
            crossroad_id=new_crossroad.id
        )
        db.add(new_camera)
        db.flush()
        for area in camera.areas:
            new_area = models_db.Area(
                coordinates=area.coordinates,
                mask_id=None,
                camera_id=new_camera.id,
                traffic_light_id=None
            )
            db.add(new_area)
            db.flush()

            new_mask = models_db.Mask(
                x=area.mask.x,
                y=area.mask.y,
                width=area.mask.width,
                height=area.mask.height,
                area=new_area
            )
            db.add(new_mask)
            db.flush()

            new_area.mask_id = new_mask.id
            if area.traffic_light:
                new_traffic_light = models_db.TrafficLight(
                    uri=area.traffic_light.uri,
                    crossroad_id=new_crossroad.id
                )
                db.add(new_traffic_light)
                db.flush()

                new_area.traffic_light_id = new_traffic_light.id

            db.commit()
            db.refresh(new_area)

    for traffic_light in crossroad.traffic_lights:
        new_traffic_light = models_db.TrafficLight(
            uri=traffic_light.uri,
            crossroad_id=new_crossroad.id
        )
        db.add(new_traffic_light)

    db.commit()

    return {"id": new_crossroad.id}
