# Preparation
Hi, I want you to provide me a NodeJs file, 'function.js', for my current smart home project based on my given functional description.

Four code files in my project, i.e., sensor.js, actuator.js, home_plan.js and config.js, are in the 'home' folder.
The required 'function.js' should locate in the 'functions' folder, function.js should contain main function.

I will first give you the functional description, then give you the 4 NodeJs source code.

# Functional Description
MORNING PLAN:
<!-- INSERT TEMPERATURE HERE -->

LEAVE HOME PLAN:
<!-- INSERT HUMIDITY HERE -->

MOVIE PLAN:
<!-- INSERT LIGHT HERE -->


# Source Code
## sensor.js
```javascript
const { logger } = require('./logger_config');

class Sensor {
    static sensorCount = {}; // Track sensor count for each room and sensor type

    constructor(sensorType, roomName) {
        if (!Sensor.sensorCount[roomName]) {
            Sensor.sensorCount[roomName] = {}; // Initialize room if not already present
        }
        if (!Sensor.sensorCount[roomName][sensorType]) {
            Sensor.sensorCount[roomName][sensorType] = 0; // Initialize sensor type count
        }

        Sensor.sensorCount[roomName][sensorType]++; // Increment sensor count

        this.id = `/Sensor/${sensorType}/${roomName}/${Sensor.sensorCount[roomName][sensorType]}`;
        this.sensorType = sensorType;
        this.roomName = roomName;
        this.status = "off";
    }

    turnOn() {
        this.status = "on";
        console.log(`${this.id} is now ON.`);
        logger.info(`${this.id} is turned ${this.status.toUpperCase()}.`);
    }

    turnOff() {
        this.status = "off";
        console.log(`${this.id} is now OFF.`);
        logger.info(`${this.id} is turned ${this.status.toUpperCase()}.`);
    }

    getStatus() {
        console.log(`${this.id} current status is: ${this.status}`);
        logger.info(`${this.id} CURRENT STATUS is: ${this.status.toUpperCase()}`);
        return this.status;
    }

    getReading() {
        if (this.status === "off") {
            console.log(`Cannot get reading, ${this.id} is Currently OFF.`);
            logger.warning(`${this.id} is currently OFF. Cannot get reading.`);
            return null;
        } else if (this.status === "on") {
            const reading = this._generateReading();
            console.log(`${this.id} reading is: ${reading}`);
            logger.info(`${this.id} Reading is: ${reading}`);
            return reading;
        } else {
            console.log(`Status Error with status: ${this.status}`);
            logger.error(`${this.id} is in error status`);
            return null;
        }

    }

    _generateReading() {
        throw new Error("Subclasses must implement _generateReading.");
    }
}

class IndoorTemperatureSensor extends Sensor {
    constructor(roomName) {
        super("IndoorTemperature", roomName);
    }

    _generateReading() {
        return parseFloat((Math.random() * (40 - 30) + 30).toFixed(2)); // Random temp between 30-40°C
    }
}

class OutdoorTemperatureSensor extends Sensor {
    constructor(roomName) {
        super("OutdoorTemperature", roomName);
    }

    _generateReading() {
        return parseFloat((Math.random() * (25 - 20) + 20).toFixed(2)); // Random temp between 20 and 25°C
    }
}

class HumiditySensor extends Sensor {
    constructor(roomName) {
        super("Humidity", roomName);
    }

    _generateReading() {
        return parseFloat((Math.random() * (30 - 12) + 12).toFixed(2)); // Random humidity between 12-30%
    }
}

class LightIntensiveSensor extends Sensor {
    constructor(roomName) {
        super("LightIntensive", roomName);
    }

    _generateReading() {
        return parseFloat((Math.random() * (1200 - 900) + 900).toFixed(2)); // Random light intensity between 900-1200 lux
    }
}

class SmokeSensor extends Sensor {
    constructor(roomName) {
        super("Smoke", roomName);
    }

    _generateReading() {
        return parseFloat((Math.random() * 100).toFixed(2)); // Random smoke level between 0-100
    }
}

module.exports = { IndoorTemperatureSensor, OutdoorTemperatureSensor, HumiditySensor, LightIntensiveSensor, SmokeSensor };
```

## actuator.js
```javascript
const { logger } = require('./logger_config');
const {DAILY_ROUTINE_DURATION} = require("./config");

class Actuator {
    static actuatorCount = {}; // Track actuator count for each room and actuator type

    constructor(actuatorType, roomName) {
        if (!Actuator.actuatorCount[roomName]) {
            Actuator.actuatorCount[roomName] = {}; // Initialize room if not already present
        }
        if (!Actuator.actuatorCount[roomName][actuatorType]) {
            Actuator.actuatorCount[roomName][actuatorType] = 0; // Initialize actuator type count
        }

        Actuator.actuatorCount[roomName][actuatorType]++; // Increment actuator count

        this.id = `/Actuator/${actuatorType}/${roomName}/${Actuator.actuatorCount[roomName][actuatorType]}`;
        this.actuatorType = actuatorType;
        this.roomName = roomName;
        this.status = "off";
    }

    turnOn() {
        this.status = "on";
        console.log(`${this.id} is turned ON.`);
        logger.info(`${this.id} is turned ON.`);
    }

    turnOff() {
        this.status = "off";
        console.log(`${this.id} is turned OFF.`);
        logger.info(`${this.id} is turned OFF.`);
    }

    getStatus() {
        console.log(`${this.id} current status is: ${this.status}`);
        logger.info(`${this.id} CURRENT STATUS is: ${this.status.toUpperCase()}`);
        return this.status;
    }
}

class Heater extends Actuator {
    constructor(roomName) {
        super("Heater", roomName);
        this.targetTemperature = null;
    }

    setTargetTemperature(targetTemperature) {
        this.targetTemperature = targetTemperature;
        console.log(`Set the target temperature of ${this.id} to ${this.targetTemperature}°C.`);
        logger.info(`Set the target temperature of ${this.id} to ${this.targetTemperature}°C.`);


    }

    adjustTemperature(currentTemperature) {
        if (this.targetTemperature && currentTemperature < this.targetTemperature) {
            this.turnOn();
        } else {
            this.turnOff();
        }
    }
}

class AC extends Actuator {
    constructor(roomName) {
        super("AC", roomName);
        this.targetTemperature = null;
    }

    setTargetTemperature(targetTemperature) {
        this.targetTemperature = targetTemperature;
        console.log(`Set the target temperature of ${this.id} to ${this.targetTemperature}°C.`);
        logger.info(`Set the target temperature of ${this.id} to ${this.targetTemperature}°C.`);
    }

    adjustTemperature(currentTemperature) {
        if (this.targetTemperature && currentTemperature > this.targetTemperature) {
            this.turnOn();
        } else {
            this.turnOff();
        }
    }
}

class CoffeeMachine extends Actuator {
    constructor(roomName) {
        super("CoffeeMachine", roomName);
    }

    makeCoffee(coffeeType) {
        if (this.status === "on") {
            console.log(`${this.id} Start making ${coffeeType}`);
            logger.info(`${this.id} Start making ${coffeeType}`);
        } else if (this.status === "off") {
            console.log(`${this.id} is OFF now.`);
            logger.warning(`${this.id} is OFF now, Need to turn it ON First.`);
        } else {
            logger.error(`There is some error with the Coffee Machine ${this.id}.`);
            console.log(`There is some error with the Coffee Machine ${this.id}.`);
        }
    }
}


class Window extends Actuator {
    constructor(roomName) {
        super("Window", roomName);
    }
}

class Door extends Actuator {
    constructor(roomName) {
        super("Door", roomName);
    }

    lock() {
        console.log(`Lock the door ${this.id}`);
        logger.info(`Lock the door ${this.id}`);
    }

    unlock() {
        console.log(`Unlock the door ${this.id}`);
        logger.info(`Unlock the door ${this.id}`);
    }
}


class Curtain extends Actuator {
    constructor(roomName) {
        super("Curtain", roomName);
    }
}

class CleaningRobot extends Actuator {
    constructor(roomName) {
        super("CleaningRobot", roomName);
    }

    dailyRoutine() {
        if (this.status === "off") {
            logger.warning(`Cleaning Robot ${this.id} is OFF, turn it ON First.`);
            console.log(`Cleaning Robot ${this.id} is OFF now, Need to Turn it ON First.`)
        }
        else if (this.status === "on") {
            logger.info(`Cleaning Robot ${this.id} Starts Daily Cleaning Routine.`);
            console.log(`Cleaning Robot ${this.id} Starts Daily Cleaning Routine.`);

            setTimeout(() => {
                console.log(`${this.id} Finish Daily Cleaning Routine, Will Turn it OFF.`);
                logger.info(`${this.id} Finish Daily Cleaning Routine, Will Turn it OFF.`);
                this.turnOff();
            }, DAILY_ROUTINE_DURATION * 1000);
        } else {
            console.log(`There is Some Error with the Cleaning Robot ${this.id}.`);
            logger.error(`There is Some Error with the Cleaning Robot ${this.id}.`);
        }
    }
}

class NotificationSender extends Actuator {
    constructor(roomName) {
        super("NotificationSender", roomName);
    }

    sendNotification(message) {
        if (this.status === "on") {
            console.log(`Notification from ${this.id} send message: ${message}`);
            logger.info(`Notification from ${this.id} send message: ${message}`)
        } else if (this.status === "off") {
            console.log(`${this.id} is OFF, turn it on first.`);
            logger.warning(`Notification Sender ${this.id} is OFF, Turn it On First.`);
        } else{
            logger.error("Fail to send the message. There is some error with the Notification Sender")
            console.log("Fail to send the message. There is some error with the Notification Sender.")
        }
    }
}

class MusicPlayer extends Actuator {
    constructor(roomName) {
        super("MusicPlayer", roomName);
    }

    playMusic(playlist) {
        if (this.status === "on") {
            console.log(`${this.id} start playing ${playlist}`);
            logger.info(`${this.id} start playing ${playlist}`)
        } else if(this.status === "off") {
            console.log(`${this.id} is OFF now, Turn it ON First.`);
            logger.warning(`${this.id} is OFF now, Turn it ON First.`);
        } else{
            logger.error(`Fail to play ${playlist}, There is some error with the music player.`)
            console.log(`Fail to play ${playlist}, There is some error with the music player.`)
        }
    }
}

class Light extends Actuator {
    constructor(roomName) {
        super("Light", roomName);
        this.brightnessLevels = { low: 30, medium: 60, high: 90 };
        this.brightnessLevel = 0;
    }

    setBrightness(level) {
        if (this.brightnessLevels[level] !== undefined) {
            if (this.status === "on") {
                this.brightnessLevel = this.brightnessLevels[level];
                console.log(`Set ${this.id} light brightness to ${level.toUpperCase()}`);
                logger.info(`Set the ${this.id} light brightness level to ${level.toUpperCase()}`);
            }else if (this.status === "off"){
                console.log(`Light ${this.id} is OFF. Please turn it on before setting the brightness level.`);
                logger.warning(`Light ${this.id} is OFF. Please turn it on before setting the brightness level.`);
            }else {
                console.log(`There is an error with the Light ${this.id}`);
                logger.error(`There is an error with the Light ${this.id}`);
            }
        } else {
            console.log(`Invalid brightness level: ${level}`);
            logger.error(`Invalid brightness level: ${level}`);
        }
    }
}

class SmartTV extends Actuator {
    constructor(roomName) {
        super("SmartTV", roomName);
    }

    playChannel(channelName) {
        if (this.status === "on") {
            console.log(`Start playing ${channelName} on ${this.id} in ${this.roomName}`);
            logger.info(`Start playing ${channelName} on ${this.id} in ${this.roomName}`);
        } else if(this.status === "off") {
          logger.warning(`${this.id} is OFF now, Need to Turn it ON First.`);
            console.log(`${this.id} is OFF now, Need to Turn it ON First.`);
        } else {
            console.log(`Fail to play ${channelName}, There is some error with the TV.`);
            logger.error(`Fail to play ${channelName}, There is some error with the TV.`);
        }
    }
}

class SmartSocket extends Actuator {
    constructor(roomName) {
        super("SmartSocket", roomName);
    }
}

class Humidifier extends Actuator {
    constructor(roomName) {
        super("Humidifier", roomName);
    }

    increaseHumidity() {
        logger.info(`${this.id} Increasing humidity in ${this.roomName}.`);
        console.log(`${this.id} Increasing humidity in ${this.roomName}.`);
    }

    decreaseHumidity() {
        console.log(`${this.id} Decreasing humidity in ${this.roomName}.`);
        logger.info(`${this.id} Decreasing humidity in ${this.roomName}.`);
    }
}

module.exports = { Actuator, Heater, AC, CoffeeMachine, Window, Door, Curtain, CleaningRobot, NotificationSender, MusicPlayer, Light, SmartTV, SmartSocket, Humidifier};
```

## home_plan.js
```javascript
const {
IndoorTemperatureSensor, HumiditySensor, LightIntensiveSensor, SmokeSensor,
OutdoorTemperatureSensor
} = require("./sensor");

const {
NotificationSender, Light, Window, Curtain, MusicPlayer, Heater, AC, CoffeeMachine,
SmartSocket, Door, CleaningRobot, SmartTV, Humidifier
} = require("./actuator");


const { logger } = require("./logger_config");

class Room {
constructor(name) {
this.name = name;
this.sensors = [];
this.actuators = [];
}

    addSensor(sensor) {
        this.sensors.push(sensor);
    }

    addActuator(actuator) {
        this.actuators.push(actuator);
    }

    printInfo() {
        console.log(`\n${this.name}:`);
        console.log("Sensors:");
        this.sensors.forEach(sensor => console.log("-", sensor.id));
        console.log("Actuators:");
        this.actuators.forEach(actuator => console.log("-", actuator.id));
    }
}

function createRoomWithComponents(name, sensorTypes, actuatorTypes) {
const room = new Room(name);
sensorTypes.forEach(SensorType => room.addSensor(new SensorType(name)));
actuatorTypes.forEach(ActuatorType => room.addActuator(new ActuatorType(name)));
return room;
}

function homePlan() {
const rooms = [
createRoomWithComponents("LivingRoom", [LightIntensiveSensor, IndoorTemperatureSensor, HumiditySensor],
[Door, Light, Light, Window, Window, Curtain, MusicPlayer, SmartSocket, SmartSocket,
CleaningRobot, SmartTV, NotificationSender, AC, Heater, Humidifier]),

        createRoomWithComponents("Bedroom", [IndoorTemperatureSensor, HumiditySensor, LightIntensiveSensor],
            [Light, Light, Window, Curtain, AC, Heater, MusicPlayer, Door, SmartSocket,
                SmartSocket, CleaningRobot, Humidifier]),

        createRoomWithComponents("Kitchen", [HumiditySensor, SmokeSensor],
            [Light, Window, Heater, CoffeeMachine, SmartSocket, SmartSocket, SmartSocket, Door]),

        createRoomWithComponents("Bathroom", [IndoorTemperatureSensor, HumiditySensor],
            [Light, Window, Heater, Door, SmartSocket, SmartSocket]),

        createRoomWithComponents("Balcony", [OutdoorTemperatureSensor, HumiditySensor],
            [Door])
    ];

    return rooms;
}

function printHomePlan(home) {
console.log("\n--- Home Plan ---");
home.forEach(room => room.printInfo());
}

function getRoom(home, roomName) {
const room = home.find(room => room.name === roomName);
if (room) {
console.log(`We found ${roomName}!`);
logger.info(`We found ${roomName}!`);
return room;
} else {
console.log(`There is no room called ${roomName} at home.`);
logger.warning(`There is no room called ${roomName} at home.`);
return null;
}
}

function getRoomSensors(home, roomName) {
const room = home.find(room => room.name === roomName);
if (room) return room.sensors;
console.log(`There are no sensors found in ${roomName}.`);
logger.warning(`There are no sensors found in ${roomName}.`);
return null;
}

function getRoomActuators(home, roomName) {
const room = home.find(room => room.name === roomName);
if (room) return room.actuators;
console.log(`There are no actuators found in ${roomName}.`);
logger.warning(`There are no actuators found in ${roomName}.`);
return null;
}

function getAllSensors(home, sensorType) {
return home.flatMap(room => room.sensors.filter(sensor => sensor.sensorType === sensorType));
}

function getAllActuators(home, actuatorType) {
return home.flatMap(room => room.actuators.filter(actuator => actuator.actuatorType === actuatorType));
}

if (require.main === module) {
const home = homePlan();
getAllActuators(home, "Light");
}

module.exports = {
homePlan,
printHomePlan,
getRoom,
getRoomSensors,
getRoomActuators,
getAllSensors,
getAllActuators
};

```

## config.js
```javascript
// Configuration constants
const TEMP_CHANGE_DURATION_WINDOW = 1;
const TEMP_LOW = 15;
const TEMP_HIGH = 25;
const HUMIDITY_LOW = 30;
const HUMIDITY_HIGH = 50;
const LIGHT_INTENSITY_LOW = 300;
const LIGHT_INTENSITY_HIGH = 900;
const DAILY_ROUTINE_DURATION = 5;

module.exports = {
    TEMP_CHANGE_DURATION_WINDOW, TEMP_LOW, TEMP_HIGH,
    HUMIDITY_LOW, HUMIDITY_HIGH, LIGHT_INTENSITY_LOW, LIGHT_INTENSITY_HIGH,
    DAILY_ROUTINE_DURATION
};
```
