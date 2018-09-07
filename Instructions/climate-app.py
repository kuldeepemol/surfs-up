# Import modules
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def home():
    print("Server received request for 'Home' page ...")
    return (
        f"Welcome to Climate API!<br/><br/>"
        f"Available route are listed below:<br/><br/>"
        f"To find you precipitation in Hawaii use route: /api/v1.0/precipitation<br/>"
        f"To find all stations in Hawaii use route: /api/v1.0/stations<br/>"
        f"To find all temperature in Hawaii use route: /api/v1.0/tobs<br/>"
        f"To find Temperature between date use route: /api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for '/api/v1.0/precipitation' page ...")

    # Calculate the date one year from the last date in data set
    last_date, = session.query(Measurement.date).order_by(desc(Measurement.id)).first()

    year_ago_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    year_ago_date = year_ago_date.strftime('%Y-%m-%d')

    results = session.query(
                    Measurement.date,
                    Measurement.prcp.label('precipitation')
            ).filter(
                    Measurement.date >= year_ago_date,
                    Measurement.date <= last_date,
                    Measurement.prcp.isnot(None)
            ).order_by(
                    Measurement.date
            ).all()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for each_precipitation in results:
        precipitation_dict = {}
        precipitation_dict[each_precipitation.date] = each_precipitation.precipitation
        all_precipitation.append(precipitation_dict)

    session.close()

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for '/api/v1.0/stations' page ...")

    # Query all station
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    session.close()

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for '/api/v1.0/tobs' page ...")

    # Calculate the date one year from the last date in data set
    last_date, = session.query(Measurement.date).order_by(desc(Measurement.id)).first()

    year_ago_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    year_ago_date = year_ago_date.strftime('%Y-%m-%d')

    temp_data_query = session.query(
                            Measurement.tobs.label('temperature')
                    ).filter(
                            Measurement.date >= year_ago_date,
                            Measurement.date <= last_date,
                            Measurement.tobs.isnot(None)
                    ).order_by(
                            Measurement.date
                    ).all()

    # Convert list of tuples into normal list
    all_temperature = list(np.ravel(temp_data_query))

    session.close()

    return jsonify(all_temperature)


@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    print("Server received request for '/api/v1.0/<start>' page ...")

    """TMIN, TAVG, and TMAX for a list of dates.

    Args:
        start_date (string): A date string in the format %Y-%m-%d

    Returns:
        TMIN, TAVE, and TMAX
    """

    results = session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs)
            ).filter(
                Measurement.date >= start_date
            ).all()

    # Convert list of tuples into normal list
    temp_summary = list(np.ravel(results))

    session.close()

    return jsonify(temp_summary)


@app.route("/api/v1.0/<start_date>/<end_date>")
def start_and_end_date(start_date, end_date):
    print("Server received request for ',/api/v1.0/<start>/<end>' page ...")

    """TMIN, TAVG, and TMAX for a list of dates.

    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d

    Returns:
        TMIN, TAVE, and TMAX
    """

    results = session.query(
                    func.min(Measurement.tobs),
                    func.avg(Measurement.tobs),
                    func.max(Measurement.tobs)
                ).filter(
                    Measurement.date >= start_date,
                    Measurement.date <= end_date
                ).all()

    # Convert list of tuples into normal list
    temp_summary = list(np.ravel(results))

    session.close()

    return jsonify(temp_summary)


if __name__ == "__main__":
    app.run(debug=True)
