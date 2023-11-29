from models.database import db
from models.data import ElectroScooter
from flask import Flask, request, jsonify
import requests
import time
import random
import sys
from Raft import RAFTFactory
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

service_info = {
    "host": "127.0.0.1",
    "port": int(sys.argv[1])
}

time.sleep(random.randint(1, 3))
node = RAFTFactory(service_info).create_server()
node.to_string()

db_ = 'electro-scooters'
if not node.leader:
    db_ += f'_0{str(service_info["port"])[-1]}'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_}.db'
print(f'DB NAME: {db_}')
db.init_app(app)

swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Test application"
        }
    )

app.register_blueprint(swaggerui_blueprint)

@app.route('/electro-scooters/<int:scooter_id>', methods=['GET'])
def get_electro_scooter_by_id(scooter_id):
    scooter = ElectroScooter.query.get(scooter_id)

    if scooter is not None:
        return jsonify({
            "id": scooter.id,
            "name": scooter.name,
            "battery_level": scooter.battery_level
        }), 200
    else:
        return jsonify({"error": "Electro Scooter not found"}), 404


@app.route('/electro-scooters', methods=['GET'])
def get_electro_scooters():
    scooters = ElectroScooter.query.all()
    response = {}
    response["scooters"] = []

    if len(scooters) != 0:
        for scooter in scooters:
            response["scooters"].append({
                "id": scooter.id,
                "name": scooter.name,
                "battery_level": scooter.battery_level
            })
        return jsonify(response), 200

    else:
        return jsonify({"error": "No Electro Scooters in the database"}), 404


@app.route('/electro-scooters', methods=['POST'])
def create_electro_scooter():
    headers = dict(request.headers)
    if not node.leader and ("Token" not in headers or headers["Token"] != "Leader"):
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            data = request.get_json()
            name = data['name']
            battery_level = data['battery_level']
            electro_scooter = ElectroScooter(name=name, battery_level=battery_level)

            db.session.add(electro_scooter)
            db.session.commit()

            if node.leader:
                for follower in node.followers:
                    requests.post(f"http://{follower['host']}:{follower['port']}/electro-scooters",
                                  json=request.json,
                                  headers={"Token": "Leader"})

            return jsonify({"message": "Electro Scooter created successfully"}), 201
        except KeyError:
            return jsonify({"error": "Invalid request data"}), 400


@app.route('/electro-scooters/<int:scooter_id>', methods=['PUT'])
def update_electro_scooter(scooter_id):
    headers = dict(request.headers)
    if not node.leader and ("Token" not in headers or headers["Token"] != "Leader"):
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            scooter = ElectroScooter.query.get(scooter_id)
            if scooter is not None:
                data = request.get_json()

                scooter.name = data.get('name', scooter.name)
                scooter.battery_level = data.get('battery_level', scooter.battery_level)

                db.session.commit()

                if node.leader:
                    for follower in node.followers:
                        requests.put(f"http://{follower['host']}:{follower['port']}/electro-scooters/{scooter_id}",
                                     json=request.json,
                                     headers={"Token": "Leader"})

                return jsonify({"message": "Electro Scooter updated successfully"}), 200
            else:
                return jsonify({"error": "Electro Scooter not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/electro-scooters/<int:scooter_id>', methods=['DELETE'])
def delete_electro_scooter(scooter_id):
    headers = dict(request.headers)
    if not node.leader and ("Token" not in headers or headers["Token"] != "Leader"):
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            scooter = ElectroScooter.query.get(scooter_id)
            if scooter is not None:
                password = request.headers.get('DP')

                if password == 'accept_delete':
                    db.session.delete(scooter)
                    db.session.commit()

                    if node.leader:
                        for follower in node.followers:
                            requests.delete(
                                f"http://{follower['host']}:{follower['port']}/electro-scooters/{scooter_id}",
                                headers={"Token": "Leader", "Delete-Password": "confirm_deletion"})

                    return jsonify({"message": "Electro Scooter deleted successfully"}), 200
                else:
                    return jsonify({"error": "Incorrect password"}), 401
            else:
                return jsonify({"error": "Electro Scooter not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        sample_scooter_1 = ElectroScooter(name="Scooter 1", battery_level=90.5)
        sample_scooter_2 = ElectroScooter(name="Scooter 2", battery_level=80.0)
        db.session.add(sample_scooter_1)
        db.session.add(sample_scooter_2)
        db.session.commit()

    app.run(
        host=service_info["host"],
        port=service_info["port"]
    )