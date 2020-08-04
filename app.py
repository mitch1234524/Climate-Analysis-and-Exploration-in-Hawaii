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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'Start date here *YYYY-MM-DD*'<start>/'End date here'<end><br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    result = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > '2016-08-23'  ).\
    order_by(Measurement.date).all()
    session.close
    
    
    precipitation_dates = []
    for date, prcp in result:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        precipitation_dates.append(prcp_dict)
        
    return jsonify(precipitation_dates)

@app.route("/api/v1.0/stations")

def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()
    
    all_stations = list(results)

    return jsonify(all_stations)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    most_active = session.query(Measurement.station).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).\
                    subquery()
    
    lastdate = session.query(func.max(Measurement.date)).scalar()
    last_day = dt.datetime.strptime(lastdate,'%Y-%m-%d').date()
    start_day = last_day - dt.timedelta(days=365)
    Startdate = start_day.strftime('%Y-%m-%d')
    
    
    result = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date >= Startdate).\
            filter(Measurement.station == most_active).\
            order_by(Measurement.date.asc()).all()
     
    
    session.close()
        
    tobs = []
    for results in result:
        i = {}
        i['date'] = result[1]
        i['temperature'] = result[2]
        tobs.append(i)
        
    return jsonify(result)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end=None):
    session = Session(engine)
    if end == None:
        enddate = session.query(func.max(Measurement.date)).\
        scalar()
    else:
        enddate = str(end)
        datestart = str(start)
        results = session.query(func.min(Measurement.tobs),\
                            func.max(Measurement.tobs),\
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date.between(datestart, enddate)).\
                            first()
        
    session.close()
    return jsonify(results)
    

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    
    
    
    
    