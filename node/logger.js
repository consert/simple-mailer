const bunyan = require('bunyan');
const fs = require('fs');
const path = require('path');
const logsDir = path.resolve(__dirname, 'logs');

const getLogFileName = () => {
  "use strict";
  const fileBase = 'log_';
  let fileName = `${fileBase}0`;                // Default: logs/log_0.txt
  const filesInDir = fs.readdirSync(logsDir);
  const filesLength = filesInDir.length;
  if (filesLength > 0) {                        // folder logs has files
    fileName = `${fileBase}${filesLength - 1}`;
    const filePath = `${logsDir}/${fileName}.txt`;  // logs/log_{number_of_files -1}.txt
    if (fs.existsSync(filePath)) {
      const stats = fs.statSync(filePath);
      const fileSizeInBytes = stats["size"];
      if ((fileSizeInBytes / 1000000.0) > 2 ) {     // file logs/log_{number_of_files -1}.txt in more than 2 MB
        fileName = `${fileBase}${filesLength}`;     // change it to logs/log_{number_of_files}.txt
      }
    }
  }
  return fileName;
};

module.exports= {

  logData: (data) => {
    if (!fs.existsSync(logsDir)){
      fs.mkdirSync(logsDir);
    }
    const fileName = getLogFileName();
    const logger = bunyan.createLogger({
      name: fileName,
      streams: [{
        type: 'file',
        path: logsDir + '/' + fileName + '.txt'
      }]
    });
    logger.info(JSON.stringify(data));
  }
};