from home.sensor import IndoorTemperatureSensor, HumiditySensor, LightIntensiveSensor, SmokeSensor, \
    OutdoorTemperatureSensor
from home.actuator import NotificationSender, Light, Window, Curtain, MusicPlayer, Heater, AC, CoffeeMachine, \
    SmartSocket, Door, \
    CleaningRobot, SmartTV, Humidifier
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
                                    [Door, Light, Light, Window, Window, Curtain, MusicPlayer, SmartSocket, SmartSocket,
                                     CleaningRobot, SmartTV, NotificationSender, AC, Heater, Humidifier]),
        create_room_with_components("Bedroom", [IndoorTemperatureSensor, HumiditySensor, LightIntensiveSensor],
                                    [Light, Light, Window, Curtain, AC, Heater, MusicPlayer, Door, SmartSocket,
                                     SmartSocket, CleaningRobot, Humidifier]),
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
