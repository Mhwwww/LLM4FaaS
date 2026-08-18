import random
from home.logger_config import logger


# todo: we do not need to specify 'room' in the logger msg, if we already have the 'id'
class Sensor:
    sensor_count = {}  # Dictionary to keep track of sensor count for each room and sensor type

    def __init__(self, sensor_type, room_name):
        if room_name not in Sensor.sensor_count:
            Sensor.sensor_count[room_name] = {}  # Initialize sensor count for the room if not already present
        if sensor_type not in Sensor.sensor_count[room_name]:
            Sensor.sensor_count[room_name][
                sensor_type] = 0  # Initialize sensor count for the sensor type if not already present

        Sensor.sensor_count[room_name][sensor_type] += 1  # Increment sensor count for the sensor type in the room

        self.id = f"/Sensor/{sensor_type}/{room_name}/{Sensor.sensor_count[room_name][sensor_type]}"
        self.sensor_type = sensor_type
        self.room_name = room_name
        self.status = "off"

    def turn_on(self):
        self.status = "on"
        print(f"'{self.id}' is now {self.status.upper()}.")
        logger.info(format("\'" + self.id + "\' is turned " + self.status.upper()))

    def turn_off(self):
        self.status = "off"
        print(f"{self.id} is now OFF.")
        logger.info(format("\'" + self.id + "\' is turned " + self.status.upper()))

    def get_reading(self):
        if self.status == "off":
            print(f"Cannot Get Sensor Reading, {self.id} is Currently OFF. ")
            logger.warning(format("\'" + self.id + "\' is currently OFF. Cannot get reading."))
            return None
        elif self.status == "on":
            reading = self._generate_reading()
            print(f"{self.id} reading is: {reading}")
            logger.info(format("\'" + self.id + "\' Reading is: " + str(reading)))
            return reading
        else:
            logger.error(format("\'" + self.id + "\' is in error status."))
            print(f"Status Error with status: {self.status}")

    def get_status(self):
        print(f"{self.id} current status is: {self.status}")
        logger.info(format("\'" + self.id + "\' CURRENT STATUS is: " + self.status.upper()))
        return self.status

    def _generate_reading(self):
        raise NotImplementedError("Subclasses must implement _generate_reading method.")


class IndoorTemperatureSensor(Sensor):
    def __init__(self, room_name):
        super().__init__("IndoorTemperature", room_name)

    def _generate_reading(self):
        return round(random.uniform(30, 40), 2)


class OutdoorTemperatureSensor(Sensor):
    def __init__(self, room_name):
        super().__init__("OutdoorTemperature", room_name)

    def _generate_reading(self):
        return round(random.uniform(20, 25), 2)


class HumiditySensor(Sensor):
    def __init__(self, room_name):
        super().__init__("Humidity", room_name)

    def _generate_reading(self):
        return round(random.uniform(12, 30), 2)


class LightIntensiveSensor(Sensor):
    def __init__(self, room_name):
        super().__init__("LightIntensive", room_name)

    def _generate_reading(self):
        return round(random.uniform(900, 1200), 2)


class SmokeSensor(Sensor):
    def __init__(self, room_name):
        super().__init__("Smoke", room_name)

    def _generate_reading(self):
        return round(random.uniform(0, 100), 2)


if __name__ == "__main__":
    # pass

    uv_sensor = LightIntensiveSensor("test")
    uv_sensor.turn_on()
    uv_sensor.get_status()
    print(uv_sensor.get_reading())
    uv_sensor.turn_off()
    print(uv_sensor.get_reading())

    outdoor_temp_sensor = OutdoorTemperatureSensor("test")
    outdoor_temp_sensor.turn_on()
    print(outdoor_temp_sensor.get_reading())
