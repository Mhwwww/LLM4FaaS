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
        console.log(`'${this.id}' is now ${this.status.toUpperCase()}.`);
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
            console.log(`Cannot Get Sensor Reading, ${this.id} is Currently OFF.`);
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