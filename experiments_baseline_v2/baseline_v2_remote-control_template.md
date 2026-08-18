# Preparation
Hi, I want you to provide me with a smart home application in Python based on my given functional description.

The required application should be able to be run in a Linux terminal with a command. Provide me the command as well.

Four code files can be used as a reference, i.e., sensor.py, actuator.py, home_plan.py, and config.py. They are in the 'home' folder.

I will first give you the functional description, then give you the 4 Python source codes.


# Functional Description
<!-- INSERT HERE -->


# Source Code
## sensor.py
```python
import random
from home.logger_config import logger

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
        return round(random.uniform(10, 40), 2)


class OutdoorTemperatureSensor(Sensor):
    def __init__(self, room_name):
        super().__init__("OutdoorTemperature", room_name)

    def _generate_reading(self):
        return round(random.uniform(-10, 40), 2)


class HumiditySensor(Sensor):
    def __init__(self, room_name):
        super().__init__("Humidity", room_name)

    def _generate_reading(self):
        return round(random.uniform(0, 100), 2)


class LightIntensiveSensor(Sensor):
    def __init__(self, room_name):
        super().__init__("LightIntensive", room_name)

    def _generate_reading(self):
        return round(random.uniform(900, 1000), 2)


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
```

## actuator.py
```python
import random
import time
from home.logger_config import logger

from home.config import DAILY_ROUTINE_DURATION


# Currently, we send notification/logger.warning(msg) to the user when we need to turn on the actuators before using
# them.

class Actuator:
    actuator_count = {}  # Dictionary to keep track of sensor count for each room and sensor type

    def __init__(self, actuator_type, room_name):
        if room_name not in Actuator.actuator_count:
            Actuator.actuator_count[room_name] = {}  # Initialize sensor count for the room if not already present
        if actuator_type not in Actuator.actuator_count[room_name]:
            Actuator.actuator_count[room_name][
                actuator_type] = 0  # Initialize sensor count for the sensor type if not already present

        Actuator.actuator_count[room_name][actuator_type] += 1  # Increment sensor count for the sensor type in the room

        self.id = f"/Actuator/{actuator_type}/{room_name}/{Actuator.actuator_count[room_name][actuator_type]}"
        self.actuator_type = actuator_type
        self.room_name = room_name
        self.status = "off"

    def turn_on(self):
        self.status = "on"
        print(f"{self.id} is now {self.status}.")
        logger.info(format("\'" + self.id + "\' is turned " + self.status.upper()))

    def turn_off(self):
        self.status = "off"
        print(f"{self.id} is now {self.status}.")
        logger.info(format("\'" + self.id + "\' is turned " + self.status.upper()))

    def get_status(self):
        print(f"{self.id} current status is {self.status}")
        logger.info(format("\'" + self.id + "\' CURRENT STATUS is: " + self.status.upper()))
        return self.status


class Heater(Actuator):
    def __init__(self, room_name):
        super().__init__("Heater", room_name)
        self.target_temperature = None

    def set_target_temperature(self, target_temperature):
        self.target_temperature = target_temperature
        logger.info(format(f"Set the target temperature of {self.id} to {self.target_temperature}°C."))
        print(f"Set the target temperature of {self.id} to {self.target_temperature}°C.")

    def adjust_temperature(self, current_temperature):
        if self.target_temperature is not None:
            if current_temperature < self.target_temperature:
                self.turn_on()
            else:
                self.turn_off()


class AC(Actuator):
    def __init__(self, room_name):
        super().__init__("AC", room_name)
        self.target_temperature = None

    def set_target_temperature(self, target_temperature):
        self.target_temperature = target_temperature
        logger.info(format(f"Set the target temperature of {self.id} to {self.target_temperature}°C."))
        print(f"Set the target temperature of {self.id} to {self.target_temperature}°C.")

    def adjust_temperature(self, current_temperature):
        if self.target_temperature is not None:
            if current_temperature > self.target_temperature:
                self.turn_on()
            else:
                self.turn_off()


class CoffeeMachine(Actuator):
    def __init__(self, room_name):
        super().__init__("CoffeeMachine", room_name)

    def make_coffee(self, coffee_type):
        if self.status == "on":
            logger.info(format(self.id + "Start making " + coffee_type))
        elif self.status == "off":
            print(f" {self.id} is OFF now")
            logger.warning(format("\' " + self.id + " \'" + " is OFF now, Need to Turn it On First."))
            # self.turn_on()
            # self.make_coffee(coffee_type)
        else:
            logger.error("There is Some Error with the Coffee Machine" + self.id + ".")
            print("There is Some Error with the Coffee Machine" + self.id + ".")


class Window(Actuator):
    def __init__(self, room_name):
        super().__init__("Window", room_name)


class Door(Actuator):
    def __init__(self, room_name):
        super().__init__("Door", room_name)

    def lock(self):
        logger.info(format("Lock the door" + self.id + "."))
        print(f"Lock the door {self.id}.")

    def unlock(self):
        logger.info(format("Unlock the door" + self.id + "."))
        print(f"Unlock the door {self.id}.")


class Curtain(Actuator):
    def __init__(self, room_name):
        super().__init__("Curtain", room_name)


class CleaningRobot(Actuator):
    def __init__(self, room_name):
        super().__init__("CleaningRobot", room_name)

    def daily_routine(self):
        if self.status == "off":
            logger.warning(format("Cleaning Robot " + self.id + " is OFF now, Need to Turn it ON First"))
            print("Cleaning Robot " + self.id + " is OFF now, Need to Turn it ON First")
        elif self.status == "on":
            logger.info(format("Cleaning Robot " + self.id + " Starts Daily Cleaning Routine"))
            print(f"Cleaning Robot {self.id} Starts Daily Cleaning Routine")
            time.sleep(DAILY_ROUTINE_DURATION)
            logger.info(format(f"{self.id} Finish Daily Cleaning Routine, Will Turn it OFF"))
            print(f"{self.id} Finish Daily Cleaning Routine, Will Turn it OFF")
            self.turn_off()
        else:
            logger.error("There is Some Error with the Cleaning Robot" + self.id + ".")
            print(f"There is Some Error with the Cleaning Robot {self.id}.")


class NotificationSender(Actuator):
    def __init__(self, room_name):
        super().__init__("NotificationSender", room_name)

    def notification_sender(self, message):
        if self.status == "on":
            logger.info(format("Notification Sender " + self.id + " sends message: " + message))
            print(f"Notification Sender {self.id} send message: {message}")
        elif self.status == "off":
            logger.warning(format("Notification Sender " + self.id + " is OFF, Turn it On First."))
            print(f"Notification Sender {self.id} is OFF, please turn it on then send the message again.")
        else:
            logger.error("Fail to send the message. There is some error with the Notification Sender")
            print("Fail to send the message. There is some error with the Notification Sender.")


class MusicPlayer(Actuator):
    def __init__(self, room_name):
        super().__init__("MusicPlayer", room_name)

    def play_music(self, playlist):
        if self.status == "on":
            print(f"{self.id} start playing {playlist}")
            logger.info(format(f"{self.id} start playing {playlist}"))
        elif self.status == "off":
            print(f"Music Player {self.id} is OFF now, Turn it ON First")
            logger.warning(format("Music Player" + self.id + " is OFF now, Turn it ON First"))
            # self.turn_on()
            # self.play_music(playlist)
            # print(f"Turn {self.id} on and Start playing {playlist} list")
        else:
            logger.error("Fail to play " + playlist + ", There is some error with the music player.")
            print("Fail to play " + playlist + ", There is some error with the music player.")


class Light(Actuator):
    def __init__(self, room_name):
        super().__init__("Light", room_name)
        self.brightness_levels = {
            "low": 30,
            "medium": 60,
            "high": 90
        }
        self.brightness_level = 0

    def set_brightness_level(self, level_name):
        if level_name in self.brightness_levels:
            if self.status == "on":
                self.brightness_level = self.brightness_levels[level_name]
                print(f"Set {self.id} light brightness level to {level_name.upper()}")
                logger.info(format("Set the " + self.id + " light brightness level to " + level_name.upper()))
            elif self.status == "off":
                print(f"Light {self.id} is OFF. Please turn it on before setting the brightness level.")
                logger.warning(
                    format("Light " + self.id + " is OFF. Please turn it on before setting the brightness level."))
            else:
                print("There is an error with the Light.")
                logger.error("There is an error with the Light.")
        else:
            print(
                f"Invalid brightness level: {level_name}. Available levels are {list(self.brightness_levels.keys())}.")
            logger.error(format("Invalid brightness level: " + level_name + ". Available levels are " + str(
                list(self.brightness_levels.keys()))))


class SmartTV(Actuator):
    def __init__(self, room_name):
        super().__init__("SmartTV", room_name)

    def play_channel(self, channel_name):
        if self.status == "on":
            logger.info(format("Start playing " + channel_name + " on the " + self.id + " in " + self.room_name))
            print(f"Start playing {channel_name} on the {self.id} in {self.room_name}")
        elif self.status == "off":
            logger.warning(format("\'" + self.id + "\' is OFF now, Need to Turn it ON First."))
            print(f"\'{self.id}\' is OFF now, Need to Turn it ON First.")
            # self.turn_on()
            # self.play_channel(channel_name)
        else:
            logger.error("Fail to play " + channel_name + ", There is some error with the TV.")
            print("Fail to play " + channel_name + ", There is some error with the TV.")


class SmartSocket(Actuator):
    def __init__(self, room_name):
        super().__init__("SmartSocket", room_name)


class Humidifier(Actuator):
    def __init__(self, room_name):
        super().__init__("Humidifier", room_name)

    def increase_humidity(self):
        logger.info(f"Increasing humidity in {self.room_name}")
        print(f"Increasing humidity in {self.room_name}")

    def decrease_humidity(self):
        logger.info(f"Decreasing humidity in {self.room_name}")
        print(f"Decreasing humidity in {self.room_name}")

# if __name__ == '__main__':
#   ns = NotificationSender("LivingRoom")
#   ns.turn_on()
#   ns.notification_sender("test test test")
```

## home_plan.py
```python
from home.sensor import IndoorTemperatureSensor, HumiditySensor, LightIntensiveSensor, SmokeSensor, \
    OutdoorTemperatureSensor
from home.actuator import NotificationSender, Light, Window, Curtain, MusicPlayer, Heater, AC, CoffeeMachine, \
    SmartSocket, Door, \
    CleaningRobot, SmartTV
from home.logger_config import logger


class Room:
    def __init__(self, name):
        self.name = name
        self.sensors = []
        self.actuators = []

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def add_actuator(self, actor):
        self.actuators.append(actor)

    def print_info(self):
        print(f"\n{self.name}:")
        print("Sensors:")
        for sensor in self.sensors:
            print("-", sensor.id)
        print("Actuators:")
        for actor in self.actuators:
            print("-", actor.id)


def create_room_with_components(name, sensor_types, actuator_types):
    room = Room(name)
    for sensor_type in sensor_types:
        room.add_sensor(sensor_type(name))
    for actuator_type in actuator_types:
        room.add_actuator(actuator_type(name))
    return room


def home_plan():
    # print("Starting Home Plan Now")
    # Define rooms and their components
    rooms = [
        create_room_with_components("LivingRoom", [LightIntensiveSensor, IndoorTemperatureSensor, HumiditySensor],
                                    [Door, Light, Window, Window, Curtain, MusicPlayer, SmartSocket, SmartSocket,
                                     CleaningRobot, SmartTV, NotificationSender, AC, Heater]),
        create_room_with_components("Bedroom", [IndoorTemperatureSensor, HumiditySensor, LightIntensiveSensor],
                                    [Light, Light, Window, Curtain, AC, Heater, MusicPlayer, Door, SmartSocket,
                                     SmartSocket, CleaningRobot]),
        create_room_with_components("Kitchen", [HumiditySensor, SmokeSensor],
                                    [Light, Window, Heater, CoffeeMachine, SmartSocket, SmartSocket, SmartSocket,
                                     Door]),
        create_room_with_components("Bathroom", [IndoorTemperatureSensor, HumiditySensor],
                                    [Light, Window, Heater, Door, SmartSocket, SmartSocket]),
        create_room_with_components("Balcony", [OutdoorTemperatureSensor, HumiditySensor],
                                    [Door])
    ]

    # Print Home plan
    # for room in rooms:
    #     room.print_info()

    return rooms


# Example invocation
# home_plan()

def print_home_plan(home):
    print(f"\n---Home Plan---")
    for room in home:
        room.print_info()


def get_room(home, room_name):
    for room in home:
        if room.name == room_name:
            print(f"We find {room_name}!")
            logger.info(f"We find {room_name}!")
            return room

    print(f"there is no room called {room_name} at home")
    logger.warning(f"there is no room called {room_name} at home")
    return None


def get_room_sensors(home, room_name):
    for room in home:
        # if room.name.lower() == room_name.lower():
        if room.name == room_name:
            # room.print_info()
            return room.sensors

    print(f"there is no Sensor found in {room_name}")
    logger.warning(f"there is no Sensor found in {room_name}")
    return None  # no room_name room


def get_room_actuators(home, room_name):
    for room in home:
        if room.name == room_name:
            # room.print_info()
            return room.actuators

    print(f"there is no Actuator found in {room_name}")
    logger.warning(f"there is no Actuator found in {room_name}")
    return None


def get_all_sensors(home, sensor_type):
    all_sensors = []
    for room in home:
        for sensor in room.sensors:
            if sensor.sensor_type == sensor_type:
                # print(sensor.id)
                all_sensors.append(sensor)

    return all_sensors


def get_all_actuators(home, actuator_type):
    all_actuators = []
    for room in home:
        for actuator in room.actuators:
            if actuator.actuator_type == actuator_type:
                all_actuators.append(actuator)

    # print(all_actuators)
    return all_actuators


if __name__ == "__main__":
    # get_room(home_plan(), "outdoor")
    home = home_plan()
    # get_all_sensors(home, "IndoorTemperature")
    get_all_actuators(home, "Light")
```

## config.py
```python
# wait duration
TEMP_CHANGE_DURATION_WINDOW = 1

# threshold
TEMP_LOW = 15 # Celsius degree
TEMP_HIGH = 25

HUMIDITY_LOW = 30 # percentage
HUMIDITY_HIGH = 50

LIGHT_INTENSITY_LOW = 300 #lux: lumen per square meter
LIGHT_INTENSITY_HIGH = 900


DAILY_ROUTINE_DURATION = 5
```