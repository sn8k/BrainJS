const { exec } = require('child_process');
const fs = require('fs');
const logger = require('../logger');

function createService(serviceName, serviceScript) {
  const serviceFilePath = `/etc/systemd/system/${serviceName}.service`;
  const serviceFileContent = `
  [Unit]
  Description=${serviceName}

  [Service]
  ExecStart=${serviceScript}

  [Install]
  WantedBy=multi-user.target
  `;

  fs.writeFileSync(serviceFilePath, serviceFileContent);
  exec(`systemctl enable ${serviceName} && systemctl start ${serviceName}`, (err, stdout, stderr) => {
    if (err) {
      logger.error(`Error creating service ${serviceName}: ${err.message}`);
      return;
    }
    logger.info(`Service ${serviceName} created and started successfully.`);
  });
}

module.exports = { createService };
