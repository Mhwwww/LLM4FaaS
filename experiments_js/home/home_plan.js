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