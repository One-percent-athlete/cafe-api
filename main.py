import inspect
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)



# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random():
    with app.app_context():
        random_cafe = db.session.execute(db.select(Cafe).order_by(db.sql.func.random()).limit(1)).scalar()
        return jsonify(cafe={
            "id":random_cafe.id,
            "name":random_cafe.name,
            "map_url":random_cafe.map_url,
            "img_url":random_cafe.img_url,
            "seats":random_cafe.seats,
            "has_toilet":random_cafe.has_toilet,
            "has_wifi":random_cafe.has_wifi,
            "has_sockets":random_cafe.has_sockets,
            "can_take_calls":random_cafe.can_take_calls,
            "coffee_price":random_cafe.coffee_price,
        })

### angela's solution  
### returns attribute error 
### cafe does not have attribute to_dict()
    
# @app.route("/all", methods=["GET"])
# def get_all():
#     with app.app_context():
#         cafes = db.session.execute(db.select(Cafe).order_by(Cafe.name))
#         all_cafes = cafes.scalars().all()
#     return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
        
@app.route("/all", methods=["GET"])
def get_all():
    with app.app_context():
        cafes = db.session.execute(db.select(Cafe).order_by(Cafe.id))
        all_cafes = cafes.scalars().all()
    all_cafes_list = []
    for cafe in all_cafes:
      cafe_dict = {  # Use a descriptive name
        "id": cafe.id,
        "name": cafe.name,
        "map_url": cafe.map_url,
        "img_url": cafe.img_url,
        "seats": cafe.seats,
        "has_toilet": cafe.has_toilet,
        "has_wifi": cafe.has_wifi,
        "has_sockets": cafe.has_sockets,
        "can_take_calls": cafe.can_take_calls,
        "coffee_price": cafe.coffee_price,
      }
      all_cafes_list.append(cafe_dict)
    return jsonify(cafes=all_cafes_list)

@app.route("/search", methods=["GET"])
def get_cafe_location():
    query_location = request.args.get("loc")
    with app.app_context():
        all_cafes = db.session.execute(db.select(Cafe).where(Cafe.location == query_location)).scalars()
        if all_cafes:
            for cafe in all_cafes:
                cafe_dict = {  # Use a descriptive name
                "id": cafe.id,
                "name": cafe.name,
                "map_url": cafe.map_url,
                "img_url": cafe.img_url,
                "seats": cafe.seats,
                "has_toilet": cafe.has_toilet,
                "has_wifi": cafe.has_wifi,
                "has_sockets": cafe.has_sockets,
                "can_take_calls": cafe.can_take_calls,
                "coffee_price": cafe.coffee_price,
            }
            return jsonify(cafe=cafe_dict)
        else:
            return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404  

# HTTP POST - Create Record       
@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."}),200

# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_cafe(cafe_id):
    cafe_to_update = db.get_or_404(Cafe, cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = request.args.get("new_price")
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}),200
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe with the id."}), 404  

# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api = request.args.get("api-key")
    if api == "TopSecretAPIKey":
        cafe_to_delete = db.get_or_404(Cafe, cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"Success": "Successfully deleted the cafe."}),200
        else:
            return jsonify(error={"Not Found": "Sorry, we don't have a cafe with the id."}),404  
    else:
        return jsonify(error={"Forbiden": "Sorry, Your api-key is not right."}),403 


if __name__ == '__main__':
    app.run(debug=True)
