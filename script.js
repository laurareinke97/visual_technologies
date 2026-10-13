"use strict";

/**
 * SpritePlayer: zeigt immer genau ein Einzelbild eines Sprite-Sheets in einem <img>.
 * Das Sheet liegt im <img>, das Fenster (.viewport) schneidet per overflow:hidden aus.
 * Positionen sind in Prozent, dadurch skaliert alles mit dem Fenster mit.
 */
class SpritePlayer {
  constructor({ img, url, frames, cols, onFrame }) {
    this.img = img;
    this.url = url;
    this.frames = frames;
    this.cols = cols;
    this.rows = Math.ceil(frames / cols);
    this.onFrame = onFrame || (() => {});
    this.index = 0;
    this.dir = 1;            // 1 = vorwärts, -1 = rückwärts
    this.running = false;
    this.fps = 12;
    this._last = 0;
    this._acc = 0;
    this._tick = this._tick.bind(this);

    this.img.style.width = this.cols * 100 + "%";
    this.img.style.height = this.rows * 100 + "%";
  }

  /** Lädt das Sheet vor; liefert ein Promise. */
  load() {
    return new Promise((resolve, reject) => {
      const probe = new Image();
      probe.onload = () => {
        this.img.src = this.url;
        this.show(0);
        resolve();
      };
      probe.onerror = () => reject(new Error("Konnte " + this.url + " nicht laden."));
      probe.src = this.url;
    });
  }

  show(i) {
    this.index = ((i % this.frames) + this.frames) % this.frames;   // Umlauf in beide Richtungen
    const col = this.index % this.cols;
    const row = Math.floor(this.index / this.cols);
    this.img.style.left = -col * 100 + "%";
    this.img.style.top = -row * 100 + "%";
    this.onFrame(this.index);
  }

  step(dir) {
    this.dir = dir;
    this.show(this.index + dir);
  }

  toggle() {
    this.running ? this.stop() : this.start();
    return this.running;
  }

  start() {
    if (this.running) return;
    this.running = true;
    this._last = 0;
    this._acc = 0;
    requestAnimationFrame(this._tick);
  }

  stop() { this.running = false; }

  _tick(now) {
    if (!this.running) return;
    if (this._last) {
      this._acc += now - this._last;
      const frameTime = 1000 / this.fps;
      while (this._acc >= frameTime) {          // zeitbasiert, unabhängig von der Monitorfrequenz
        this._acc -= frameTime;
        this.show(this.index + this.dir);
      }
    }
    this._last = now;
    requestAnimationFrame(this._tick);
  }
}

/* ------------------------------------------------------------------ Aufbau */
const $ = (id) => document.getElementById(id);

const DISC_FRAMES = 24;
const DISC_STEP_DEG = 360 / DISC_FRAMES;

const disc = new SpritePlayer({
  img: $("disc-img"),
  url: "img/disc.png",
  frames: DISC_FRAMES,
  cols: 6,
  onFrame: (i) => {
    $("disc-status").textContent =
      "Drehwinkel " + i * DISC_STEP_DEG + "° (Bild " + (i + 1) + " von " + DISC_FRAMES + ")";
  },
});

const bunny = new SpritePlayer({
  img: $("bunny-img"),
  url: "img/bunny.png",
  frames: 12,
  cols: 6,
  onFrame: (i) => {
    $("bunny-status").textContent = "Bild " + (i + 1) + " von 12";
  },
});
bunny.fps = 10;

/* -------------------------------------------------------------- Bedienung */
const btnLeft = $("btn-left");
const btnRight = $("btn-right");
const btnAuto = $("btn-auto");
const btnBunny = $("btn-bunny");

function setAutoUi(button, running, textOn, textOff) {
  button.setAttribute("aria-pressed", String(running));
  button.querySelector("span").textContent = running ? textOn : textOff;
}

function toggleDiscAuto() {
  const running = disc.toggle();
  setAutoUi(btnAuto, running, "Automatik stoppen", "Automatisch drehen");
}
function toggleBunny() {
  const running = bunny.toggle();
  setAutoUi(btnBunny, running, "Hase anhalten", "Hase hüpfen lassen");
}

btnLeft.addEventListener("click", () => disc.step(-1));
btnRight.addEventListener("click", () => disc.step(1));
btnAuto.addEventListener("click", toggleDiscAuto);
btnBunny.addEventListener("click", toggleBunny);

$("disc-speed").addEventListener("input", (e) => {
  disc.fps = Number(e.target.value);
  $("disc-speed-out").textContent = disc.fps + " Bilder/s";
});

function flash(button) {
  button.classList.add("pressed");
  setTimeout(() => button.classList.remove("pressed"), 120);
}

document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.metaKey || e.altKey || e.repeat) return;   // ein Druck = ein Schritt
  if (btnLeft.disabled) return;                                 // noch nicht geladen
  switch (e.key.toLowerCase()) {
    case "l": disc.step(-1); flash(btnLeft); break;
    case "r": disc.step(1); flash(btnRight); break;
    case "a": toggleDiscAuto(); flash(btnAuto); break;
    case "h": toggleBunny(); flash(btnBunny); break;
  }
});

/* -------------------------------------------------------------- Start/Laden */
function fail(statusId, err) {
  const el = $(statusId);
  el.textContent = err.message + " Bitte Seite über einen Webserver öffnen und Dateipfade prüfen.";
  el.classList.add("error");
  console.error(err);
}

disc.load()
  .then(() => { btnLeft.disabled = btnRight.disabled = btnAuto.disabled = false; })
  .catch((err) => fail("disc-status", err));

bunny.load()
  .then(() => { btnBunny.disabled = false; })
  .catch((err) => fail("bunny-status", err));
