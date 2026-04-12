#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

const isWindows = os.platform() === 'win32';
const scriptName = isWindows ? 'install.bat' : 'install.sh';
const scriptPath = path.join(__dirname, scriptName);

// Forward all command line arguments to the underlying installer
const args = process.argv.slice(2);

console.log(`[guide-for-ai] Launching installer: ${scriptName}`);

const spawnArgs = isWindows ? ['/c', scriptPath, ...args] : [scriptPath, ...args];

const child = spawn(isWindows ? 'cmd.exe' : 'sh', spawnArgs, {
  stdio: 'inherit',
  cwd: __dirname
});

child.on('exit', (code) => {
  process.exit(code);
});

child.on('error', (err) => {
  console.error(`[guide-for-ai] Failed to start installer: ${err.message}`);
  process.exit(1);
});
