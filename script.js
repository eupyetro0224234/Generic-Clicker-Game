const { ipcRenderer } = require('electron');

let score = 0;
const scoreDisplay = document.getElementById('scoreDisplay');
const clickButton = document.getElementById('clickButton');

// Carrega a pontuação salva
ipcRenderer.invoke('load-score').then((savedScore) => {
    score = savedScore;
    scoreDisplay.innerText = 'Pontos: ' + score;
});

// Evento de clique
clickButton.addEventListener('click', () => {
    score++;
    scoreDisplay.innerText = 'Pontos: ' + score;
    ipcRenderer.send('save-score', score);
});

// === ExitHandler HTML ===
const exitModal = document.getElementById('exitModal');
const exitInput = document.getElementById('exitInput');
const exitPrompt = document.getElementById('exitPrompt'); 

// Força Comic Sans no modal
exitPrompt.style.fontFamily = '"Comic Sans MS", "Comic Sans", cursive';
exitInput.style.fontFamily = '"Comic Sans MS", "Comic Sans", cursive';

let exitActive = false;

function openExitHandler() {
    exitActive = true;
    exitInput.value = '';
    exitModal.classList.add('active');
    exitInput.focus(); // Foco automático
}

function closeExitHandler() {
    exitActive = false;
    exitModal.classList.remove('active');
}

// Recebe evento do Electron para abrir modal
ipcRenderer.on('trigger-exit', () => {
    openExitHandler();
});

// Input handling
exitInput.addEventListener('keydown', (e) => {
    if (!exitActive) return;

    if (e.key === 'Enter') {
        const txt = exitInput.value.trim().toLowerCase();
        if (txt === 'sim') {
            fadeOutAndExit();
        } else {
            // apaga entradas inválidas
            exitInput.value = '';
        }
    } else if (e.key === 'Escape') {
        closeExitHandler();
    }
});

// Função fade-out antes de fechar (preto)
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
            ipcRenderer.send('confirmed-exit'); // avisa o main process para fechar
        }
    }, 30);
}
