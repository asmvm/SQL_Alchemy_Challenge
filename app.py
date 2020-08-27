import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import *

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measure = Base.classes.measurement
stn = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
        
#         f"Available Routes:<br/>"
#         f"/api/v1.0/names<br/>"
#         f"/api/v1.0/passengers"
    

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    query = session.query(measure.date, measure.prcp).order_by(measure.date.desc()).first()
    
    session.close
       
    # Create a dictionary from the row data and append to a list of all_passengers
    precipitation_data = []
    for date, prcp in query:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)    

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of stations from the dataset.
    query = session.query(stn.name).all()
    
    session.close
    
    return jsonify(query)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.
    
    query = session.query(measure.date, measure.station, measure.tobs).all()
    
    session.close
    
    most_active = session.query(func.distinct(measure.station), func.count(measure.station)).\
            group_by(measure.station).\
            order_by(func.count(measure.station).desc()).limit(1).scalar()
    
    one_year_ago = dt.date(2017, 8, 18) + relativedelta(years=-1)
    
    temps_data = [measure.date, measure.tobs]
    temps = session.query(*temps_data).filter(measure.station == most_active).\
        filter(func.strftime("%Y/%m/%d", measure.date) >= one_year_ago).\
        order_by(measure.date.asc()).all()
    
    tobsdata = []
    for date, tobs in temps:
        tobsdata_dict = {} 
        tobsdata_dict["date"] = date
        tobsdata_dict["tobs"] = tobs
        tobsdata.append(tobsdata_dict)
    
    
    return jsonify(tobsdata)


if __name__ == '__main__':
    app.run(debug=True)