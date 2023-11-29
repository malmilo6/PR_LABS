from flasgger import swag_from
from flask import request, jsonify
from models.database import db
from models.data import ElectroScooter


def get_routes(app):
    @app.route('/api/electro-scooters', methods=['POST'])
    def create_electro_scooter():
        try:
            data = request.get_json()

            name = data['name']
            bat_lvl = data['battery_level']

            data = ElectroScooter(name=name, battery_level=bat_lvl)

            db.session.add(data)
            db.session.commit()

            return jsonify({"message": "Electro Scooter created successfully"}), 201

        except KeyError:
            return jsonify({"error": "Invalid request data"}), 400


    @app.route('/api/electro-scooters/<int:scooter_id>', methods=['GET'])
    def get_scooter(scooter_id):

        scooter = ElectroScooter.query.get(scooter_id)

        if scooter is not None:
            return jsonify({
                "id": scooter.id,
                "name": scooter.name,
                "battery_level": scooter.battery_level
            }), 200

        else:
            return jsonify({"error": "Electro Scooter not found"}), 404


    @app.route('/api/electro-scooters/<int:scooter_id>', methods=['PUT'])
    def update_scooter(scooter_id):
        try:
            scooter = ElectroScooter.query.get(scooter_id)

            if scooter is not None:
                data = request.get_json()
                scooter.name = data.get('name', scooter.name)
                scooter.battery_level = data.get('battery_level', scooter.battery_level)

                db.session.commit()
                return jsonify({"message": "Electro Scooter updated successfully"}), 200

            else:
                return jsonify({"error": "Electro Scooter not found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/api/electro-scooters/<int:scooter_id>', methods=['DELETE'])
    def delete_scooter(scooter_id):
        try:
            scooter = ElectroScooter.query.get(scooter_id)

            if scooter is not None:
                password = request.headers.get('X-Delete-Password')

                if password == 'your_secret_password':
                    db.session.delete(scooter)
                    db.session.commit()
                    return jsonify({"message": "Electro Scooter deleted successfully"}), 200
                else:
                    return jsonify({"error": "Incorrect password"}), 401

            else:
                return jsonify({"error": "Electro Scooter not found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500
