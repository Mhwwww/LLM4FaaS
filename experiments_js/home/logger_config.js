const LOG_LEVELS = {
    "info": 0,      // 最低级别，info 消息会显示
    "warning": 1,   // 只显示 warning 和 error
    "error": 2,     // 只显示 error
};

// 默认日志级别
let currentLogLevel = "warning";  // 设置为 "warning"，如果你希望显示 warning 和 error 级别的日志

// 获取时间戳的格式化函数
function getTimestamp() {
    const now = new Date();
    return now.toISOString();
}

// 获取调用堆栈信息，用来获取文件名和函数名
function getCallerInfo() {
    const stack = new Error().stack.split("\n")[3];  // 获取调用栈的第三行
    const regex = /at (.*) \((.*):(\d+):(\d+)\)/; // 正则提取函数名、文件路径、行号
    const match = stack.match(regex);
    if (match) {
        return {
            funcName: match[1],
            fileName: match[2].split('/').pop(),  // 只取文件名
        };
    }
    return {
        funcName: "unknown",
        fileName: "unknown",
    };
}

const logger = {
    info: (msg) => {
        if (LOG_LEVELS[currentLogLevel] <= LOG_LEVELS["info"]) {
            const { funcName, fileName } = getCallerInfo();
            const timestamp = getTimestamp();
            console.log(`[INFO] ${timestamp} - ${fileName} - ${funcName} - ${msg}`);
        }
    },
    warning: (msg) => {
        if (LOG_LEVELS[currentLogLevel] <= LOG_LEVELS["warning"]) {
            const { funcName, fileName } = getCallerInfo();
            const timestamp = getTimestamp();
            console.warn(`[WARNING] ${timestamp} - ${fileName} - ${funcName} - ${msg}`);
        }
    },
    error: (msg) => {
        if (LOG_LEVELS[currentLogLevel] <= LOG_LEVELS["error"]) {
            const { funcName, fileName } = getCallerInfo();
            const timestamp = getTimestamp();
            console.error(`[ERROR] ${timestamp} - ${fileName} - ${funcName} - ${msg}`);
        }
    },
    setLogLevel: (level) => {
        if (LOG_LEVELS[level] !== undefined) {
            currentLogLevel = level;
        } else {
            console.warn(`Invalid log level: ${level}`);
        }
    }
};

module.exports = { logger };