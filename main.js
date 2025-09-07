const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');

const scoreDir = path.join(os.homedir(), 'AppData', 'Roaming', '.GenericClickerGame', 'score');
const scoreFile = path.join(scoreDir, 'score.dat');

function ensureScoreFile() {
    if (!fs.existsSync(scoreDir)) fs.mkdirSync(scoreDir, { recursive: true });
    if (!fs.existsSync(scoreFile)) fs.writeFileSync(scoreFile, '0', 'utf-8');
}

function createWindow() {
    const win = new BrowserWindow({
        width: 1280,
        height: 720,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true,
            contextIsolation: false
        },
        show: false,
        autoHideMenuBar: true,
        frame: true
    });

    win.loadFile('index.html');

    win.once('ready-to-show', () => {
        win.maximize();
        win.show();
    });

    // Forçar resolução mínima
    win.on('resize', () => {
        const [width, height] = win.getSize();
        if (width < 1280 || height < 720) {
            win.setSize(Math.max(width, 1280), Math.max(height, 720));
        }
    });

    // Intercepta fechamento da janela
    win.on('close', (e) => {
        e.preventDefault(); // cancela o fechamento
        win.webContents.send('trigger-exit'); // envia evento para o front-end
    });
}

app.whenReady().then(() => {
    ensureScoreFile();
    createWindow();
});

ipcMain.handle('load-score', () => {
    ensureScoreFile();
    const data = fs.readFileSync(scoreFile, 'utf-8');
    return parseInt(data) || 0;
});

ipcMain.on('save-score', (event, score) => {
    ensureScoreFile();
    fs.writeFileSync(scoreFile, score.toString(), 'utf-8');
});

ipcMain.on('confirmed-exit', (event) => {
    const win = BrowserWindow.getFocusedWindow();
    if (win) {
        win.destroy(); // fecha a janela sem disparar outro evento close
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});