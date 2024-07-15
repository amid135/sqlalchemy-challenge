# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date_dt = datetime.strptime(last_date, '%Y-%m-%d')
    query_date = last_date_dt - timedelta(days=365)

    # Query for precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Find the most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    most_active_station = active_stations[0][0]

    # Calculate the date 1 year ago from the last data point
    last_date = session.query(func.max(Measurement.date)).\
        filter(Measurement.station == most_active_station).scalar()
    last_date_dt = datetime.strptime(last_date, '%Y-%m-%d')
    query_date = last_date_dt - timedelta(days=365)

    # Query the temperature observations (TOBS) for the most active station for the last year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= query_date).all()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(results))

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start date."""
    # Query for TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Convert list of tuples into normal list
    temp_stats = list(np.ravel(results))

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given date range."""
    # Query for TMIN, TAVG, and TMAX for dates between start and end date inclusive
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Convert list of tuples into normal list
    temp_stats = list(np.ravel(results))

    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
