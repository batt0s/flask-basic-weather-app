#importing packages
import requests
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from pytemperature import k2c

app = Flask(__name__)

#configs
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "secretkey"
db = SQLAlchemy(app)

#creating city model
class City(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


#a function for getting weather data
def get_weather_data(city):

    api_key = "your api key"

    url = f"http://api.openweathermap.org/data/2.5/weather?q={ city }&appid={ api_key }"

    r = requests.get(url).json()
    return r


#index function (method = get)
@app.route("/")
def index_get():

    cities = City.query.all()

    if cities:

        weather_data = []

        for city in cities:

            r = get_weather_data(city.name)

            print("\n", r, "\n")

            weather = {
                "city": r["name"],
                "temp": k2c(r["main"]["temp"]),
                "description": r["weather"][0]["description"],
                "icon": r["weather"][0]["icon"]
            }

            weather_data.append(weather)

            print("\n", weather, "\n")

        return render_template("weather.html", weather_data=weather_data)

    else:

        return render_template("weather.html")


#index function (method = post)
@app.route("/", methods=["POST"])
def index_post():

    err_msg = ""

    new_city = request.form.get("city")

    if new_city:

        is_exist = City.query.filter_by(name=new_city).first()

        if not is_exist:

            new_city_data = get_weather_data(new_city)

            if new_city_data["cod"] == 200:

                new_city_name = new_city_data["name"]

                new_city_obj = City(name=new_city_name)

                db.session.add(new_city_obj)
                db.session.commit()

            else:

                err_msg = "City not found."

        else:

            err_msg = "City already exist."

    if err_msg:
        flash(err_msg)
    else:
        flash("City added.")

    return redirect(url_for("index_get"))


#a function for deleting city
@app.route("/delete/<name>")
def delete_city(name):

    city = City.query.filter_by(name=name).first()

    db.session.delete(city)
    db.session.commit()


    flash("Deleted")
    return redirect(url_for("index_get"))






if __name__ == "__main__":

    app.run(debug=True)