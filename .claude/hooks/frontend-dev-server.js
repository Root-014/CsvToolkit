// PostToolUse hook: ensures the Vite dev server is running whenever Claude
// edits a frontend file, so changes are visible live (Vite HMR handles the reload).
const { spawn } = require('child_process');
const net = require('net');
const path = require('path');

const PORT = 5173;
const FRONTEND_DIR = path.join(__dirname, '..', '..', 'frontend');

let input = '';
process.stdin.on('data', (c) => { input += c; });
process.stdin.on('end', () => {
  let payload;
  try {
    payload = JSON.parse(input || '{}');
  } catch {
    process.exit(0);
  }

  const filePath = payload?.tool_input?.file_path || payload?.tool_input?.filePath || '';
  if (!/frontend/i.test(filePath)) {
    process.exit(0);
  }

  const socket = net.createConnection({ port: PORT, host: 'localhost' });
  const timer = setTimeout(() => {
    socket.destroy();
    startServer();
  }, 1500);

  socket.on('connect', () => {
    clearTimeout(timer);
    socket.destroy();
    process.exit(0); // already running, Vite HMR will pick up the change
  });

  socket.on('error', () => {
    clearTimeout(timer);
    startServer();
  });

  function startServer() {
    const child = spawn('npm run dev', {
      cwd: FRONTEND_DIR,
      detached: true,
      stdio: 'ignore',
      shell: true,
    });
    child.unref();
    console.log(JSON.stringify({
      systemMessage: `Started frontend dev server (vite) on http://localhost:${PORT}`,
    }));
    process.exit(0);
  }
});
