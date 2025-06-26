// Game data
const words = {
    action: ['DIEHARD', 'MADMAX', 'BATMAN', 'ALIENS', 'PREDATOR'],
    drama: ['TITANIC', 'JOKER', 'PARASITE', 'LA LA LAND', 'THE NOTEBOOK'],
    thriller: ['SEVEN', 'GET OUT', 'US', 'PSYCHO', 'THE GAME'],
    comedy: ['ANCHORMAN', 'SUPERBAD', 'HANGOVER', 'MEAN GIRLS', 'DEADPOOL'],
    scifi: ['STAR WARS', 'STAR TREK', 'DUNE', 'GRAVITY', 'HER']
};

// Game state
let currentWord = '';
let guessedLetters = new Set();
let lives = 6;
let score = 0;
let streak = 0;

// DOM elements
const welcomeScreen = document.getElementById('welcome-screen');
const genreScreen = document.getElementById('genre-screen');
const gameScreen = document.getElementById('game-screen');
const wordDisplay = document.getElementById('word-display');
const keyboard = document.getElementById('keyboard');
const livesDisplay = document.getElementById('lives');
const scoreDisplay = document.getElementById('score');
const streakDisplay = document.getElementById('streak');
const messageDisplay = document.getElementById('message');

// Audio elements
const correctSound = document.getElementById('correct-sound');
const wrongSound = document.getElementById('wrong-sound');
const winSound = document.getElementById('win-sound');
const loseSound = document.getElementById('lose-sound');
const clickSound = document.getElementById('click-sound');

// Initialize screens
welcomeScreen.style.display = 'block';
genreScreen.style.display = 'none';
gameScreen.style.display = 'none';

// Create keyboard
function createKeyboard() {
    keyboard.innerHTML = '';
    for (let i = 65; i <= 90; i++) {
        const letter = String.fromCharCode(i);
        const button = document.createElement('button');
        button.textContent = letter;
        button.addEventListener('click', () => handleGuess(letter));
        keyboard.appendChild(button);
    }
}

// Show random genres
function showRandomGenres() {
    const genreContainer = document.querySelector('.genre-buttons');
    genreContainer.innerHTML = '';
    
    const allGenres = Object.keys(words);
    const shuffledGenres = allGenres.sort(() => Math.random() - 0.5);
    const selectedGenres = shuffledGenres.slice(0, 3);
    
    selectedGenres.forEach(genre => {
        const button = document.createElement('button');
        button.classList.add('genre-btn');
        button.textContent = genre.toUpperCase();
        button.addEventListener('click', () => startGame(genre));
        genreContainer.appendChild(button);
    });
}

// Start game
function startGame(genre) {
    currentWord = words[genre][Math.floor(Math.random() * words[genre].length)];
    guessedLetters.clear();
    lives = 6;
    livesDisplay.textContent = lives;
    messageDisplay.textContent = '';
    
    // Reset hangman
    document.querySelectorAll('.hangman-part').forEach(part => {
        part.style.display = 'none';
    });
    document.getElementById('stand').style.display = 'block';
    
    // Reset keyboard
    Array.from(keyboard.children).forEach(button => {
        button.classList.remove('used');
        button.disabled = false;
    });
    
    updateWordDisplay();
    
    // Show game screen
    welcomeScreen.style.display = 'none';
    genreScreen.style.display = 'none';
    gameScreen.style.display = 'flex';
}

// Handle guess
function handleGuess(letter) {
    if (guessedLetters.has(letter) || lives <= 0) return;
    
    guessedLetters.add(letter);
    const button = Array.from(keyboard.children).find(btn => btn.textContent === letter);
    button.classList.add('used');
    
    if (currentWord.includes(letter)) {
        playSound(correctSound);
        updateWordDisplay();
        if (isWordComplete()) {
            handleWin();
        }
    } else {
        playSound(wrongSound);
        lives--;
        livesDisplay.textContent = lives;
        showHangmanPart();
        if (lives === 0) {
            handleLoss();
        }
    }
}

// Update word display
function updateWordDisplay() {
    wordDisplay.textContent = currentWord
        .split('')
        .map(letter => guessedLetters.has(letter) ? letter : '_')
        .join(' ');
}

// Check if word is complete
function isWordComplete() {
    return currentWord.split('').every(letter => guessedLetters.has(letter));
}

// Show hangman part
function showHangmanPart() {
    const parts = ['right-leg', 'left-leg', 'right-arm', 'left-arm', 'body', 'head'];
    const part = parts[lives];
    document.getElementById(part).style.display = 'block';
}

// Handle win
function handleWin() {
    playSound(winSound);
    streak++;
    streakDisplay.textContent = streak;
    score += lives * 10;
    scoreDisplay.textContent = score;
    messageDisplay.textContent = 'CONGRATULATIONS! YOU WON!';
    messageDisplay.style.color = '#00ff00';
    disableKeyboard();
}

// Handle loss
function handleLoss() {
    playSound(loseSound);
    streak = 0;
    streakDisplay.textContent = streak;
    messageDisplay.textContent = `GAME OVER! THE MOVIE WAS: ${currentWord}`;
    messageDisplay.style.color = '#ff00ff';
    disableKeyboard();
}

// Disable keyboard
function disableKeyboard() {
    Array.from(keyboard.children).forEach(button => {
        button.disabled = true;
    });
}

// Play sound
function playSound(sound) {
    sound.currentTime = 0;
    sound.play();
}

// Event listeners
document.querySelectorAll('.difficulty-btn').forEach(button => {
    button.addEventListener('click', () => {
        playSound(clickSound);
        welcomeScreen.style.display = 'none';
        genreScreen.style.display = 'block';
        showRandomGenres();
    });
});

// Initialize game
createKeyboard(); 