from CrossroadHandler import CrossroadHandler
from database import SessionLocal
from sqlalchemy import desc
import models_db as md

if __name__ == "__main__":
    session = SessionLocal()

    last_crossroad = session.query(md.Crossroads).order_by(desc(md.Crossroads.id)).first()

    if last_crossroad:
        CrossroadHandler(last_crossroad)
    else:
        print('Перекрестков в базе данных не найдено.')