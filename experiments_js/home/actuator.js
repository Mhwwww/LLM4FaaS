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
        console.log(`${this.id} is turned ${this.status}.`);
        logger.info(`${this.id} is turned ON.`);
    }

    turnOff() {
        this.status = "off";
        console.log(`${this.id} is turned ${this.status}.`);
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
        console.log(`Lock the door ${this.id}.`);
        logger.info(`Lock the door ${this.id}.`);
    }

    unlock() {
        console.log(`Unlock the door ${this.id}.`);
        logger.info(`Unlock the door ${this.id}.`);
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
                console.log(`Set ${this.id} light brightness level to ${level.toUpperCase()}`);
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