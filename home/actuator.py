import time
from home.logger_config import logger
from home.config import DAILY_ROUTINE_DURATION


class Actuator:
    actuator_count = {}  # Dictionary to keep track of sensor count for each room and sensor type

    def __init__(self, actuator_type, room_name):
        if room_name not in Actuator.actuator_count:
            # Initialize sensor count for the room if not already present
            Actuator.actuator_count[room_name] = {}
        if actuator_type not in Actuator.actuator_count[room_name]:
            # Initialize sensor count for the sensor type if not already present
            Actuator.actuator_count[room_name][
                actuator_type] = 0
        # Increment sensor count for the sensor type in the room
        Actuator.actuator_count[room_name][actuator_type] += 1

        self.id = f"/Actuator/{actuator_type}/{room_name}/{Actuator.actuator_count[room_name][actuator_type]}"
        self.actuator_type = actuator_type
        self.room_name = room_name
        self.status = "off"

    def turn_on(self):
        self.status = "on"
        print(f"{self.id} is turned {self.status}.")
        logger.info(format("\'" + self.id + "\' is turned " + self.status.upper()))

    def turn_off(self):
        self.status = "off"
        print(f"{self.id} is turned {self.status}.")
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
            print(f"{self.id} Start making {coffee_type}")
        elif self.status == "off":
            print(f" {self.id} is OFF now")
            logger.warning(format("\' " + self.id + " \'" + " is OFF now, Need to Turn it On First."))

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
        logger.info(f"{self.id} Increasing humidity in {self.room_name}")
        print(f"{self.id} Increasing humidity in {self.room_name}")

    def decrease_humidity(self):
        logger.info(f"{self.id} Decreasing humidity in {self.room_name}")
        print(f"{self.id} Decreasing humidity in {self.room_name}")
