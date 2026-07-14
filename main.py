from contextlib import contextmanager
from pathlib import Path
import sqlite3
import time

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


DB_PATH = Path(__file__).with_name("measurements.db")
app = FastAPI()


class Measurement(BaseModel):
    timestamp: str
    measurement: float


@contextmanager
def connect():
    db = sqlite3.connect(DB_PATH)
    try:
        yield db
        db.commit()
    finally:
        db.close()


def init_db():
    with connect() as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS measurements "
            "(timestamp TEXT PRIMARY KEY, measurement REAL)"
        )


@app.on_event("startup")
def startup():
    init_db()


@app.post("/measurements")
def create_measurement(data: Measurement):
    timestamp = int(time.time())
    # makes sure the data was taken within an hour of being received by the server
    # the timestamp sent by the sensors is in standard time, but this can be adjusted
    if abs(timestamp - data.timestamp) > 3600:
        raise HTTPException(status_code=400, detail="Timestamp does not match")
        return

    with connect() as db:
        # TODO: verify error handling works
        #
        # row = db.execute(
        #     "SELECT timestamp FROM measurements WHERE timestamp = ?",
        #     (timestamp,),
        # ).fetchone()
        #
        # if row is not None:
        #     return

        db.execute(
            "INSERT OR REPLACE INTO measurements VALUES (?, ?)",
            (data.timestamp, data.measurement),
        )
    return data


@app.get("/measurements/{timestamp}")
def get_measurement(timestamp: str):
    with connect() as db:
        row = db.execute(
            "SELECT timestamp, measurement FROM measurements WHERE timestamp = ?",
            (timestamp,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Measurement not found")

    return {"timestamp": row[0], "measurement": row[1]}


@app.get("/measurements")
def get_measurements(start: str = Query(...), end: str = Query(...)):
    with connect() as db:
        rows = db.execute(
            "SELECT timestamp, measurement FROM measurements "
            "WHERE timestamp >= ? AND timestamp <= ? "
            "ORDER BY timestamp",
            (start, end),
        ).fetchall()

    return [{"timestamp": row[0], "measurement": row[1]} for row in rows]
