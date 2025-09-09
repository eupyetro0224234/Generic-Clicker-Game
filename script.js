const { ipcRenderer } = require('electron');
const path = require('path');
const os = require('os');
const fs = require('fs');

// Verifica se é a primeira execução
const isFirstRun = !fs.existsSync(path.join(os.homedir(), 'AppData', 'Roaming', '.GenericClickerGame', 'score', 'score.dat'));

// ---------- Score ----------
let score = 0;
const scoreDisplay = document.getElementById('scoreDisplay');

ipcRenderer.invoke('load-score').then(savedScore => {
    score = savedScore;
    scoreDisplay.innerText = score; // Removido o texto "Pontos: "
});

// ---------- Botão de Click ----------
const clickButton = document.getElementById('clickButton');
// Carrega a imagem do botão
clickButton.src = `file://${path.join(os.homedir(),'AppData','Roaming','.GenericClickerGame','assets','botão.gif').replace(/\\/g,'/')}`;

// ---------- Prevenir comportamentos indesejados ----------
// Desabilitar menu de contexto (clique direito)
document.addEventListener('contextmenu', e => {
    // Permitir apenas no menu e no botão de click
    if (!e.target.closest('#menuContainer') && !e.target.closest('#clickButtonContainer')) {
        e.preventDefault();
    }
});

// Desabilitar zoom com gestos de pinça
document.addEventListener('gesturestart', e => {
    e.preventDefault();
});

// Desabilitar arrastar e soltar
document.addEventListener('dragstart', e => {
    e.preventDefault();
});

// Desabilitar seleção de texto
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
    }, 100); // dura 100ms, igual ao clique
}

// ---------- Multi-button Click Handling (apenas no botão) ----------
let activeButtons = new Set();

function addScore(points) {
    score += points;
    scoreDisplay.innerText = score; // Removido o texto "Pontos: "
    ipcRenderer.send('save-score', score);
}

// Adiciona event listener apenas ao botão
clickButton.addEventListener('mousedown', e => {
    if (exitActive) return;

    // Scroll do mouse (button 1) sempre conta 1 ponto
    if (e.button === 1) {
        addScore(1);
        animateClickButton(); // animação de clique
        return;
    }

    // Clique esquerdo (0), direito (2) ou outros (>=3) contam 1 ponto
    if (e.button === 0 || e.button === 2 || e.button >= 3) {
        addScore(1);
        animateClickButton(); // animação de clique
    }

    activeButtons.add(e.button);
});

clickButton.addEventListener('mouseup', e => {
    activeButtons.delete(e.button);
});

// ---------- Mouse Wheel (scroll) no botão ----------
clickButton.addEventListener('wheel', e => {
    if (exitActive) return;

    // Cada rolagem da roda soma 1 ponto (independente da direção)
    addScore(1);
    animateClickButton(); // animação de clique
    e.preventDefault(); // Prevenir scroll da página
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
    let unlockedCount=0; // ligar conquistas aqui
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
    e.stopPropagation(); // Impede que o evento se propague
    menuOpen=!menuOpen;
    menuOptions.classList.toggle('visible',menuOpen);
});

function handleMenuOption(opt){
    menuOpen=false;
    menuOptions.classList.remove('visible');
    switch(opt){
        case "Configurações": alert("Abrir menu de configurações"); break;
        case "Controles": alert("Abrir menu de controles"); break;
        case "Conquistas": alert("Abrir menu de conquistas"); break;
        case "Eventos": alert("Abrir menu de eventos"); break;
        case "Sair": openExitHandler(); break;
    }
}

updateMenu();