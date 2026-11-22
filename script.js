const TEAS = [
  {
    id: "black",
    name: "Black Tea",
    seconds: 3 * 60,
    liquidPrefix: "liquid_black",
  },
  {
    id: "green",
    name: "Green Tea",
    seconds: 2 * 60,
    liquidPrefix: "liquid_green",
  },
  {
    id: "herbal",
    name: "Herbal Tea",
    seconds: 4 * 60,
    liquidPrefix: "liquid_herbal",
  },
];

const menuScreen = document.querySelector("#menu-screen");
const brewScreen = document.querySelector("#brew-screen");
const teaOptions = document.querySelector(".tea-options");
const menuButton = document.querySelector("#menu-button");
const doneMessage = document.querySelector("#done-message");
const timer = document.querySelector("#timer");
const liquidLayer = document.querySelector("#liquid-layer");
const mugLayer = document.querySelector("#mug-layer");
const steamLayer = document.querySelector("#steam-layer");

let activeTea = null;
let remainingSeconds = 0;
let timerId = null;

function buildMenu() {
  TEAS.forEach((tea) => {
    const button = document.createElement("button");
    button.className = "tea-option";
    button.type = "button";
    button.dataset.tea = tea.id;
    button.setAttribute("aria-label", tea.name);
    button.addEventListener("click", () => startTea(tea));
    teaOptions.append(button);
  });
}

function showMenu() {
  clearTimer();
  activeTea = null;
  menuScreen.classList.remove("hidden");
  brewScreen.classList.add("hidden");
}

function startTea(tea) {
  clearTimer();
  activeTea = tea;
  remainingSeconds = tea.seconds;
  menuButton.textContent = "Home";
  doneMessage.classList.add("hidden");
  menuScreen.classList.add("hidden");
  brewScreen.classList.remove("hidden");
  drawBrewing();
  timerId = window.setTimeout(tick, 1000);
}

function tick() {
  timerId = null;

  if (!activeTea) {
    return;
  }

  remainingSeconds -= 1;
  if (remainingSeconds <= 0) {
    drawDone();
    return;
  }

  drawBrewing();
  timerId = window.setTimeout(tick, 1000);
}

function drawBrewing() {
  const stage = getLiquidStage();
  const steamFile = remainingSeconds % 2 === 0 ? "steam_1.png" : "steam_2.png";

  liquidLayer.src = `sprites/${activeTea.liquidPrefix}${stage}.png`;
  mugLayer.src = "sprites/mug_empty.png";
  steamLayer.src = `sprites/${steamFile}`;
  steamLayer.classList.remove("hidden");
  timer.textContent = formatTime(remainingSeconds);
}

function drawDone() {
  clearTimer();
  liquidLayer.src = `sprites/${activeTea.liquidPrefix}3.png`;
  mugLayer.src = "sprites/done.png";
  steamLayer.classList.add("hidden");
  doneMessage.classList.remove("hidden");
  menuButton.textContent = "Brew another one?";
  timer.textContent = "";
}

function getLiquidStage() {
  const elapsed = activeTea.seconds - remainingSeconds;
  const third = activeTea.seconds / 3;
  return Math.min(3, Math.floor(elapsed / third) + 1);
}

function clearTimer() {
  if (timerId !== null) {
    window.clearTimeout(timerId);
    timerId = null;
  }
}

function formatTime(seconds) {
  const safeSeconds = Math.max(0, seconds);
  const minutes = Math.floor(safeSeconds / 60);
  const remaining = String(safeSeconds % 60).padStart(2, "0");
  return `${minutes}:${remaining}`;
}

menuButton.addEventListener("click", showMenu);
buildMenu();
