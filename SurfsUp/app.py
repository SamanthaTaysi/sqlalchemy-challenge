from flask import Flask, jsonify
import datetime as dt
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Create Flask app
app = Flask(__name__)

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Calculate the date 1 year ago from the last data point in the database
last_date = session.query(func.max(Measurement.date)).scalar()
last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
one_year_ago = last_date - relativedelta(years=1)

# Find the most active station
most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

# Define routes
@app.route("/")
def home():
    """Homepage with available routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/&lt;start&gt;'>/api/v1.0/&lt;start&gt;</a><br/>"
        f"<a href='/api/v1.0/&lt;start&gt;/&lt;end&gt;'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON representation of precipitation data for the last 12 months."""
    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                         filter(Measurement.date >= one_year_ago).all()
    
    # Convert to dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    stations = session.query(Station.station).all()
    station_list = [station for station, in stations]
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
    # Query the last 12 months of temperature observation data for the most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= one_year_ago).\
                filter(Measurement.station == most_active_station).all()
    
    # Convert to list of dictionaries
    tobs_list = [{"date": date, "temperature": tobs} for date, tobs in tobs_data]
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return a JSON list of the minimum temperature, the average temperature,
    and the maximum temperature for a specified start date."""
    # Query TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    
    # Convert to list of dictionaries
    temp_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temps]
    
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature,
    and the maximum temperature for a specified date range."""
    # Query TMIN, TAVG, and TMAX for the date range
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert to list of dictionaries
    temp_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temps]
    
    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)