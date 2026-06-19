from contextlib import contextmanager
from pathlib import Path
import sqlite3

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
    with connect() as db:
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
