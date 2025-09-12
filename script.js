const { ipcRenderer } = require('electron');
const path = require('path');
const os = require('os');
const fs = require('fs');

// Verifica se é a primeira execução
const isFirstRun = !fs.existsSync(path.join(os.homedir(), 'AppData', 'Roaming', '.GenericClickerGame', 'score', 'score.dat'));

// Caminho para o arquivo de configuração
const configPath = path.join(os.homedir(), 'AppData', 'Roaming', '.GenericClickerGame', 'configs', 'config.json');

// Configurações padrão
const defaultConfig = {
    "Clique Esquerdo": true,
    "Clique Direito": true,
    "Clique Botão do Meio": true,
    "Rolagem do Mouse": true,
    "Ativar Mods": false,
    "Verificar atualizações": true,
    "Mostrar conquistas ocultas": false,
    "Menu vertical": false
};

// Configurações atuais
let config = { ...defaultConfig };

// ---------- Funções para gerenciar configurações ----------
function loadConfig() {
    try {
        if (fs.existsSync(configPath)) {
            const configData = fs.readFileSync(configPath, 'utf8');
            const savedConfig = JSON.parse(configData);
            config = { ...defaultConfig, ...savedConfig };
            console.log('Configurações carregadas:', config);
            
            // Aplicar configurações imediatamente após carregar
            applyConfig();
        } else {
            // Se o arquivo não existe, cria com as configurações padrão
            saveConfig();
            // Aplicar configurações padrão
            applyConfig();
        }
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
        config = { ...defaultConfig };
        applyConfig();
    }
    return config;
}

function saveConfig() {
    try {
        // Garante que o diretório existe
        const configDir = path.dirname(configPath);
        if (!fs.existsSync(configDir)) {
            fs.mkdirSync(configDir, { recursive: true });
        }
        
        // Salva as configurações
        fs.writeFileSync(configPath, JSON.stringify(config, null, 4), 'utf8');
        console.log('Configurações salvas:', config);
    } catch (error) {
        console.error('Erro ao salvar configurações:', error);
    }
}

function updateConfig(newConfig) {
    config = { ...config, ...newConfig };
    saveConfig();
    
    // Aplica as configurações no jogo
    applyConfig();
    
    return config;
}

function applyConfig() {
    console.log('Aplicando configurações:', config);
    
    // Menu vertical - aplicar imediatamente ao carregar
    const menuOptions = document.getElementById('menuOptions');
    if (menuOptions) {
        if (config["Menu vertical"]) {
            menuOptions.classList.add("vertical");
        } else {
            menuOptions.classList.remove("vertical");
        }
    }
    
    // Aqui você pode adicionar lógica para aplicar outras configurações no jogo
}

// Carrega as configurações ao iniciar
loadConfig();

// ---------- Score ----------
let score = 0;
const scoreDisplay = document.getElementById('scoreDisplay');

ipcRenderer.invoke('load-score').then(savedScore => {
    score = savedScore;
    scoreDisplay.innerText = score;
});

// ---------- Botão de Click ----------
const clickButton = document.getElementById('clickButton');
clickButton.src = `file://${path.join(os.homedir(),'AppData','Roaming','.GenericClickerGame','assets','botão.gif').replace(/\\/g,'/')}`;

// ---------- Prevenir comportamentos indesejados ----------
document.addEventListener('contextmenu', e => {
    if (!e.target.closest('#menuContainer') && !e.target.closest('#clickButtonContainer')) {
        e.preventDefault();
    }
});

document.addEventListener('gesturestart', e => {
    e.preventDefault();
});

document.addEventListener('dragstart', e => {
    e.preventDefault();
});

document.addEventListener('selectstart', e => {
    if (!e.target.closest('#exitInput')) {
        e.preventDefault();
    }
});

// ---------- Função para animar o clique do botão ----------
function animateClickButton() {
    clickButton.style.transform = 'scale(0.95)';
    setTimeout(() => {
        clickButton.style.transform = 'scale(1)';
    }, 100);
}

// ---------- Efeito de pontos flutuantes (AGORA EM PRETO) ----------
function showFloatingPoints(points, x, y) {
    const floatEl = document.createElement('div');
    floatEl.textContent = `+${points}`;
    floatEl.style.position = 'fixed';
    floatEl.style.left = `${x}px`;
    floatEl.style.top = `${y}px`;
    floatEl.style.fontSize = '24px';
    floatEl.style.fontWeight = '900';
    floatEl.style.color = '#FFFFFF'; // branco
    floatEl.style.textShadow = '1px 1px 2px rgba(0, 0, 0, 1)';
    floatEl.style.pointerEvents = 'none';
    floatEl.style.transition = 'transform 0.8s ease, opacity 0.8s ease';
    floatEl.style.zIndex = '1000'; // Garante que fique acima de outros elementos
    document.body.appendChild(floatEl);

    // Inicia a animação para subir e desaparecer
    setTimeout(() => {
        floatEl.style.transform = 'translateY(-60px)';
        floatEl.style.opacity = '0';
    }, 10);

    // Remove o elemento após a animação
    setTimeout(() => {
        floatEl.remove();
    }, 900);
}

// ---------- Atualiza addScore para mostrar o efeito ----------
// Agora recebe também x e y (posição do clique)
function addScore(points, x, y) {
    score += points;
    scoreDisplay.innerText = score;
    ipcRenderer.send('save-score', score);

    // Se coordenadas foram passadas, usa elas. Senão, mostra no meio do botão.
    if (x !== undefined && y !== undefined) {
        showFloatingPoints(points, x, y);
    } else {
        const rect = clickButton.getBoundingClientRect();
        const bx = rect.left + rect.width / 2;
        const by = rect.top - 20;
        showFloatingPoints(points, bx, by);
    }
}

// ---------- Multi-button Click Handling ----------
let activeButtons = new Set();

// ---------- Atualiza o evento do botão para suportar múltiplos cliques ----------
clickButton.addEventListener('mousedown', e => {
    if (exitActive) return;

    let allowedPoints = 0;

    if (e.button === 0 && config["Clique Esquerdo"]) allowedPoints++;
    if (e.button === 1 && config["Clique Botão do Meio"]) allowedPoints++;
    if (e.button === 2 && config["Clique Direito"]) allowedPoints++;
    if (e.button >= 3 && config["Clique Esquerdo"]) allowedPoints++;

    if (allowedPoints > 0) {
        addScore(allowedPoints, e.clientX, e.clientY); // 🔹 usa posição real do clique
        animateClickButton();
    }

    activeButtons.add(e.button);
});

clickButton.addEventListener('mouseup', e => {
    activeButtons.delete(e.button);
});

// ---------- Mouse Wheel (scroll) no botão ----------
clickButton.addEventListener('wheel', e => {
    if (exitActive) return;

    if (config["Rolagem do Mouse"]) {
        addScore(1, e.clientX, e.clientY); // 🔹 também usa posição do scroll
        animateClickButton();
        e.preventDefault();
    }
});

// ---------- Exit Modal ----------
const exitModal = document.getElementById('exitModal');
const exitInput = document.getElementById('exitInput');
let exitActive = false;

function openExitHandler() {
    exitActive = true;
    exitInput.value = '';
    exitModal.classList.add('active');
    exitInput.focus();
}

function closeExitHandler() {
    exitActive = false;
    exitModal.classList.remove('active');
}

// Fecha o modal clicando fora da caixa
exitModal.addEventListener('click', (e) => {
    if (e.target === exitModal) {
        closeExitHandler();
    }
});

ipcRenderer.on('trigger-exit', openExitHandler);

exitInput.addEventListener('keydown', e => {
    if (!exitActive) return;

    if (e.key === 'Enter') {
        if (exitInput.value.trim().toLowerCase() === 'sim') fadeOutAndExit();
        else exitInput.value = '';
    } else if (e.key === 'Escape') {
        closeExitHandler();
    }
});

function fadeOutAndExit() {
    const fadeOverlay = document.createElement('div');
    fadeOverlay.style.position = 'fixed';
    fadeOverlay.style.top = 0;
    fadeOverlay.style.left = 0;
    fadeOverlay.style.width = '100%';
    fadeOverlay.style.height = '100%';
    fadeOverlay.style.backgroundColor = 'black';
    fadeOverlay.style.opacity = 0;
    fadeOverlay.style.zIndex = 9999;
    document.body.appendChild(fadeOverlay);

    let opacity = 0;
    const fade = setInterval(() => {
        opacity += 0.05;
        fadeOverlay.style.opacity = opacity;
        if (opacity >= 1) {
            clearInterval(fade);
            ipcRenderer.send('confirmed-exit');
        }
    }, 30);
}

// ---------- Background Canvas ----------
const canvas = document.getElementById('backgroundCanvas');
const ctx = canvas.getContext('2d');
let TILE_SIZE = 40;
const BASE_COLORS = [[200,230,201],[255,224,178],[255,205,210],[187,222,251],[255,249,196],[197,225,165]];
const FREQ = 0.5;
let GRID_WIDTH, GRID_HEIGHT, gridColors = [];

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    GRID_WIDTH = Math.ceil(canvas.width / TILE_SIZE)+1;
    GRID_HEIGHT = Math.ceil(canvas.height / TILE_SIZE)+1;

    gridColors = [];
    for(let y=0; y<GRID_HEIGHT; y++){
        const row = [];
        for(let x=0; x<GRID_WIDTH; x++){
            row.push(BASE_COLORS[(x+y)%BASE_COLORS.length]);
        }
        gridColors.push(row);
    }
}

function adjustBrightness(color,factor){return color.map(c=>Math.max(0,Math.min(255,c*factor)));}

function drawBackground(){
    const t = performance.now()/1000;
    for(let y=0;y<GRID_HEIGHT;y++){
        for(let x=0;x<GRID_WIDTH;x++){
            let brightness = 1+0.15*Math.sin(2*Math.PI*FREQ*t+(x+y));
            const color = adjustBrightness(gridColors[y][x],brightness);
            ctx.fillStyle = `rgb(${color[0]},${color[1]},${color[2]})`;
            ctx.fillRect(x*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE);
        }
    }
    requestAnimationFrame(drawBackground);
}

resizeCanvas(); 
drawBackground();
window.addEventListener('resize', resizeCanvas);

// ---------- Menu ----------
const menuContainer = document.getElementById('menuContainer');
const menuIcon = document.getElementById('menuIcon');
const menuOptions = document.getElementById('menuOptions');
menuIcon.src = `file://${path.join(os.homedir(),'AppData','Roaming','.GenericClickerGame','assets','menu.jpg').replace(/\\/g,'/')}`;

let menuOpen=false;
const baseOptions=["Configurações","Controles","Conquistas","Eventos","Sair"];
let options=[...baseOptions];

function updateMenu(){
    menuOptions.innerHTML="";
    let unlockedCount=0;
    options.forEach(opt=>{
        const btn=document.createElement('button');
        btn.textContent = opt.includes("Conquistas")?`Conquistas (${unlockedCount})`:opt;
        btn.classList.add('menuButton');
        if(opt==="Sair") btn.classList.add('fullWidth');
        btn.addEventListener('click',()=>handleMenuOption(opt));
        menuOptions.appendChild(btn);
    });
}

menuIcon.addEventListener('click',(e)=>{
    if (exitActive) return; // 🔹 Bloqueia quando modal está ativo
    e.stopPropagation();
    menuOpen=!menuOpen;
    menuOptions.classList.toggle('visible',menuOpen);
});

// ---------- Menu de Configurações ----------
let settingsVisible = false;
const settingsIframe = document.createElement('iframe');
settingsIframe.style.position = 'fixed';
settingsIframe.style.top = '0';
settingsIframe.style.left = '0';
settingsIframe.style.width = '100%';
settingsIframe.style.height = '100%';
settingsIframe.style.border = 'none';
settingsIframe.style.zIndex = '1000';
settingsIframe.style.display = 'none';
settingsIframe.src = 'configuracoes.html';
document.body.appendChild(settingsIframe);

// Ouvir mensagens do iframe de configurações
window.addEventListener('message', (event) => {
    if (event.data.action === 'closeSettings') {
        closeSettings();
    } else if (event.data.action === 'configUpdated') {
        updateConfig(event.data.config);
    }
});

function openSettings() {
    settingsVisible = true;
    settingsIframe.style.display = 'block';
    ipcRenderer.send('settings-open', true); // 🔹 avisa o main.js
}

function closeSettings() {
    settingsVisible = false;
    settingsIframe.style.display = 'none';
    ipcRenderer.send('settings-open', false); // 🔹 avisa o main.js
}

function handleMenuOption(opt){
    if (exitActive) return; // 🔹 Bloqueia quando modal está ativo
    menuOpen=false;
    menuOptions.classList.remove('visible');
    switch(opt){
        case "Configurações": openSettings(); break;
        case "Controles": alert("Abrir menu de controles"); break;
        case "Conquistas": alert("Abrir menu de conquistas"); break;
        case "Eventos": alert("Abrir menu de eventos"); break;
        case "Sair": openExitHandler(); break;
    }
}

updateMenu();

// Garantir que o menu seja atualizado quando as configurações forem carregadas
document.addEventListener('DOMContentLoaded', function() {
    // Isso já deve estar acontecendo no loadConfig(), mas vamos garantir
    setTimeout(applyConfig, 100);
});