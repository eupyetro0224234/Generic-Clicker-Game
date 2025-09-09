const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { https } = require('follow-redirects');

const gameDir = path.join(os.homedir(), 'AppData', 'Roaming', '.GenericClickerGame');
const scoreDir = path.join(gameDir, 'score');
const assetsDir = path.join(gameDir, 'assets');
const configsDir = path.join(gameDir, 'configs');
const scoreFile = path.join(scoreDir, 'score.dat');
const menuImagePath = path.join(assetsDir, 'menu.jpg');
const buttonGifPath = path.join(assetsDir, 'botão.gif');
const configFile = path.join(configsDir, 'config.json');
const imageUrl = 'https://i.postimg.cc/J08Qx3p9/menu.png';
const buttonGifUrl = 'https://drive.google.com/uc?export=download&id=1B4NIU1OXL_-lUFxtyyPcmpxq4d6JJRWK';

const defaultConfig = {
    "Clique Esquerdo": true,
    "Clique Direito": true,
    "Clique Botão do Meio": true,
    "Rolagem do Mouse": true,
    "Ativar Mods": false,
    "Verificar atualizações": true,
    "Mostrar conquistas ocultas": false,
    "Pular o loading": false,
    "Menu vertical": false
};

let loadingWindow = null;
let mainWindow = null;

function ensureDirectories() {
    if (!fs.existsSync(gameDir)) fs.mkdirSync(gameDir, { recursive: true });
    if (!fs.existsSync(scoreDir)) fs.mkdirSync(scoreDir, { recursive: true });
    if (!fs.existsSync(assetsDir)) fs.mkdirSync(assetsDir, { recursive: true });
    if (!fs.existsSync(configsDir)) fs.mkdirSync(configsDir, { recursive: true });
}

function ensureScoreFile() {
    ensureDirectories();
    if (!fs.existsSync(scoreFile)) fs.writeFileSync(scoreFile, '0', 'utf-8');
}

function ensureConfigFile() {
    ensureDirectories();
    if (!fs.existsSync(configFile)) {
        fs.writeFileSync(configFile, JSON.stringify(defaultConfig, null, 4), 'utf-8');
        console.log('Arquivo config.json criado com sucesso:', configFile);
    }
}

function downloadFile(url, filePath, description) {
    return new Promise((resolve, reject) => {
        if (fs.existsSync(filePath)) {
            console.log(`${description} já existe:`, filePath);
            resolve();
            return;
        }

        console.log(`Baixando ${description}...`);
        
        const file = fs.createWriteStream(filePath);
        https.get(url, (response) => {
            if (response.statusCode === 200) {
                const totalSize = parseInt(response.headers['content-length'], 10);
                let downloadedSize = 0;
                
                response.on('data', (chunk) => {
                    downloadedSize += chunk.length;
                    const progress = Math.round((downloadedSize / totalSize) * 100);
                    
                    // Enviar progresso para a janela de loading
                    if (loadingWindow && !loadingWindow.isDestroyed()) {
                        loadingWindow.webContents.send('download-progress', {
                            description: description,
                            progress: progress
                        });
                    }
                });
                
                response.pipe(file);
                file.on('finish', () => {
                    file.close();
                    console.log(`${description} baixado com sucesso:`, filePath);
                    resolve();
                });
            } else {
                console.error(`Erro ao baixar ${description}:`, response.statusCode);
                file.close();
                if (fs.existsSync(filePath)) {
                    fs.unlinkSync(filePath);
                }
                reject(new Error(`HTTP ${response.statusCode}`));
            }
        }).on('error', (err) => {
            console.error(`Erro na requisição do ${description}:`, err.message);
            file.close();
            if (fs.existsSync(filePath)) {
                fs.unlinkSync(filePath);
            }
            reject(err);
        });
    });
}

function createLoadingWindow() {
    loadingWindow = new BrowserWindow({
        width: 400,
        height: 300,
        resizable: false,
        movable: false,
        minimizable: false,
        maximizable: false,
        closable: false,
        alwaysOnTop: true,
        frame: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    loadingWindow.loadFile('loading.html');
    loadingWindow.center();
    
    return loadingWindow;
}

function createMainWindow() {
    return new Promise((resolve) => {
        mainWindow = new BrowserWindow({
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

        mainWindow.loadFile('index.html');

        mainWindow.webContents.once('did-finish-load', () => {
            mainWindow.maximize();
            mainWindow.show();
            resolve(); // Resolve a Promise quando a janela estiver totalmente carregada
        });

        mainWindow.on('resize', () => {
            const [width, height] = mainWindow.getSize();
            if (width < 1280 || height < 720) {
                mainWindow.setSize(Math.max(width, 1280), Math.max(height, 720));
            }
        });

        mainWindow.on('close', (e) => {
            e.preventDefault();
            mainWindow.webContents.send('trigger-exit');
        });
    });
}

function closeLoadingWindow() {
    if (loadingWindow && !loadingWindow.isDestroyed()) {
        loadingWindow.destroy();
        loadingWindow = null;
        console.log('Janela de loading fechada');
    }
}

async function initializeGame() {
    // Verificar se já existe tudo que precisamos
    const allReady =
        fs.existsSync(scoreFile) &&
        fs.existsSync(configFile) &&
        fs.existsSync(menuImagePath) &&
        fs.existsSync(buttonGifPath);

    if (allReady) {
        // Tudo pronto, abre direto o jogo sem loading
        await createMainWindow();
        return;
    }

    // Criar janela de loading se faltar algo
    createLoadingWindow();

    try {
        // Enviar status inicial
        if (loadingWindow && !loadingWindow.isDestroyed()) {
            loadingWindow.webContents.send('download-progress', {
                description: "Verificando diretórios",
                progress: 0
            });
        }

        // Criar diretórios necessários
        ensureDirectories();

        // Verificar e criar arquivo de pontuação
        if (loadingWindow && !loadingWindow.isDestroyed()) {
            loadingWindow.webContents.send('download-progress', {
                description: "Configurando arquivo de pontuação",
                progress: 25
            });
        }
        ensureScoreFile();

        // Verificar e criar arquivo de configuração
        if (loadingWindow && !loadingWindow.isDestroyed()) {
            loadingWindow.webContents.send('download-progress', {
                description: "Configurando arquivo de configuração",
                progress: 50
            });
        }
        ensureConfigFile();

        // Baixar imagem do menu
        await downloadFile(imageUrl, menuImagePath, "imagem do menu");

        // Baixar GIF do botão
        await downloadFile(buttonGifUrl, buttonGifPath, "GIF do botão");

        // Criar janela principal e esperar ela carregar completamente
        await createMainWindow();

        // Só então fechar a janela de loading
        closeLoadingWindow();

    } catch (error) {
        console.error('Erro durante a inicialização:', error);

        // Em caso de erro, fechar a loading window e a aplicação
        closeLoadingWindow();
        
        // Mostrar mensagem de erro antes de sair
        setTimeout(() => {
            app.quit();
        }, 3000);
    }
}

app.whenReady().then(() => {
    initializeGame();
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
        win.destroy();
    }
});

// Handler para fechar a janela de loading
ipcMain.on('close-loading-window', () => {
    closeLoadingWindow();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});