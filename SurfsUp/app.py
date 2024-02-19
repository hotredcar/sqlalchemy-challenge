# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Define homepage route
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


# Define route to retrieve precipitation data
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date 1 year ago from the last data point
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()
    
    session.close()
    
    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)


# Define route to retrieve list of stations
#################################################
@app.route("/api/v1.0/stations")
def stations():

    # Query all stations
    stations = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(stations))
    
    return jsonify(station_list)


# Define route to retrieve temperature observations for the previous year
#################################################
@app.route("/api/v1.0/tobs")
def tobs():

    # Calculate the date 1 year ago from the last data point
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the most active station for the last year of temperature data
    most_active_station_tobs = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(most_active_station_tobs))
    
    return jsonify(tobs_list)


# Define route to retrieve temperature statistics for a given start date
#################################################
@app.route("/api/v1.0/<start>")
def temperature_start(start):

    # Query temperature statistics
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()
    
    # Convert list of tuples into normal list
    temperature_stats_list = list(np.ravel(temperature_stats))

    return jsonify(temperature_stats_list)


# Define route to retrieve temperature statistics for a given date range
#################################################
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):

    # Query temperature statistics
    temperature_stats_range = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()
    
    # Convert list of tuples into normal list
    temperature_stats_range_list = list(np.ravel(temperature_stats_range))
    
    return jsonify(temperature_stats_range_list)

if __name__ == '__main__':
    app.run(debug=True)