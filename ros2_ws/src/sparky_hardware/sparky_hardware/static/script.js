// État de l'application
let currentAngles = Array(18).fill(90);
let isConnected = false;

// Éléments DOM
const servoSelect = document.getElementById('servoSelect');
const angleSlider = document.getElementById('angleSlider');
const angleValue = document.getElementById('angleValue');
const speedInput = document.getElementById('speedInput');
const sendBtn = document.getElementById('sendBtn');
const statusDiv = document.getElementById('status');
const currentStateDiv = document.getElementById('currentState');

// Mettre à jour l'affichage de l'angle quand le slider bouge
angleSlider.addEventListener('input', (e) => {
    angleValue.textContent = e.target.value;
});

// Validation de l'input vitesse
speedInput.addEventListener('input', (e) => {
    let value = parseInt(e.target.value);
    
    // Limiter la valeur entre 1 et 500
    if (value < 1) {
        e.target.value = 1;
    } else if (value > 500) {
        e.target.value = 500;
    }
});

// Envoyer la commande au clic sur le bouton
sendBtn.addEventListener('click', async () => {
    const servoId = parseInt(servoSelect.value);
    const angle = parseInt(angleSlider.value);
    const speed = parseInt(speedInput.value) || 100; // Valeur par défaut si vide
    
    await sendCommand(servoId, angle, speed);
});

// Fonction pour envoyer une commande au serveur
async function sendCommand(servoId, angle, speed) {
    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                servo: servoId,
                angle: angle,
                speed: speed
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'ok') {
            console.log(`✅ Servo ${servoId} → ${angle}° @ ${speed}°/sec`);
            updateConnectionStatus(true);
            
            // Mettre à jour l'état local
            currentAngles[servoId] = angle;
            updateStateDisplay();
        } else {
            console.error('❌ Erreur lors de l\'envoi de la commande');
        }
        
    } catch (error) {
        console.error('❌ Erreur de connexion:', error);
        updateConnectionStatus(false);
    }
}

// Fonction pour récupérer l'état actuel
async function fetchState() {
    try {
        const response = await fetch('/api/state');
        const data = await response.json();
        
        currentAngles = data.angles;
        updateStateDisplay();
        updateConnectionStatus(true);
        
    } catch (error) {
        console.error('❌ Impossible de récupérer l\'état:', error);
        updateConnectionStatus(false);
    }
}

// Mettre à jour l'affichage de l'état
function updateStateDisplay() {
    const servoNames = [
        'Servo 0', 'Servo 1', 'Servo 2',
        'Servo 4', 'Servo 5', 'Servo 6',
        'Servo 8', 'Servo 9', 'Servo 10',
        'Servo 12', 'Servo 13', 'Servo 14',
        'Servo 16', 'Servo 17', 'Servo 18',
        'Servo 20', 'Servo 21', 'Servo 22'
    ];
    
    let html = '';
    for (let i = 0; i < currentAngles.length; i++) {
        const angle = Math.round(currentAngles[i]);
        html += `<p>${servoNames[i]}: ${angle}°</p>`;
    }
    
    currentStateDiv.innerHTML = html;
}

// Mettre à jour le statut de connexion
function updateConnectionStatus(connected) {
    isConnected = connected;
    
    if (connected) {
        statusDiv.textContent = '● Connecté';
        statusDiv.classList.add('connected');
    } else {
        statusDiv.textContent = '● Déconnecté';
        statusDiv.classList.remove('connected');
    }
}

// Récupérer l'état toutes les 2 secondes
setInterval(fetchState, 2000);

// Récupérer l'état au chargement de la page
fetchState();

console.log('🚀 Interface Sparky chargée avec contrôle de vitesse');