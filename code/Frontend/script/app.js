'use strict';

const backend_IP = `http://127.0.0.1:5000`;
const backend = backend_IP + '/api/v1';
const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
let current_sensor = 0;

const listenToUI = function () {
  const knop = document.querySelector('.js-toggle');
  knop.addEventListener('click', function () {
    console.log('switch');
    socket.emit('F2B_switchNeo');
  });
};

const listenToSocket = function () {
  socket.on('connected', function () {
    console.log('verbonden met socket webserver');
  });
  socket.on('B2F_updateNeo', function (jsonObject) {
    console.log(jsonObject);
    const htmlCircle = document.querySelector('.js-circle-neopixel');
    let htmlString = ``;
    if (jsonObject.Neopixel == true) {
      htmlString += `<svg class="c-circle" height="150" width="150">
        <circle cx="75" cy="75" r="50" stroke="Green" stroke-width="10" fill="white" />
      </svg>`;
      htmlCircle.innerHTML = htmlString;
    } else {
      htmlString += `<svg class="c-circle" height="150" width="150">
        <circle cx="75" cy="75" r="50" stroke="Red" stroke-width="10" fill="white" />
      </svg>`;
      htmlCircle.innerHTML = htmlString;
    }
  });
};

const showWaardes = function (jsonObject) {
  console.log(current_sensor);
  if (current_sensor == 1) {
    const htmlWaarde = document.querySelector('.js-accelero-waarde');
    let htmlString = ``;
    htmlString += `${jsonObject.waarde.historiekWaarde}m/s<sup>2</sup> `;
    htmlWaarde.innerHTML = htmlString;
    if (jsonObject.waarde.historiekWaarde < 12) {
      const htmlCirkel = document.querySelector('.js-circle-accel');
      let htmlString = ``;
      htmlString += `<svg class="c-circle" height="70" width="50">
      <circle cx="25" cy="25" r="20" stroke="red" stroke-width="5" fill="white" />
      </svg>`;
      htmlCirkel.innerHTML = htmlString;
    } else {
      const htmlCirkel = document.querySelector('.js-circle-accel');
      let htmlString = ``;
      htmlString += `<svg class="c-circle" height="70" width="50">
      <circle cx="25" cy="25" r="20" stroke="green" stroke-width="5" fill="white" />
      </svg>`;
      htmlCirkel.innerHTML = htmlString;
    }
  } else if (current_sensor == 2) {
    console.log(jsonObject);
    const htmlWaardePulse = document.querySelector('.js-pulse-waarde');
    let htmlStringPulse = ``;
    htmlStringPulse += `${jsonObject.waarde.historiekWaarde} bpm `;
    htmlWaardePulse.innerHTML = htmlStringPulse;
    if (jsonObject.waarde.historiekWaarde > 110) {
      const htmlCirkel = document.querySelector('.js-circle-pulse');
      let htmlString = ``;
      htmlString += `<svg class="c-circle" height="70" width="50">
      <circle cx="25" cy="25" r="20" stroke="red" stroke-width="5" fill="white" />
      </svg>`;
      htmlCirkel.innerHTML = htmlString;
    } else {
      const htmlCirkel = document.querySelector('.js-circle-pulse');
      let htmlString = ``;
      htmlString += `<svg class="c-circle" height="70" width="50">
      <circle cx="25" cy="25" r="20" stroke="green" stroke-width="5" fill="white" />
      </svg>`;
      htmlCirkel.innerHTML = htmlString;
    }
  } else if (current_sensor == 3) {
    console.log(jsonObject);
    const htmlWaardeGas = document.querySelector('.js-gas-waarde');
    let htmlStringGas = ``;
    htmlStringGas += `${jsonObject.waarde.historiekWaarde} % `;
    htmlWaardeGas.innerHTML = htmlStringGas;
    if (jsonObject.waarde.historiekWaarde > 60) {
      const htmlCirkel = document.querySelector('.js-circle-gas');
      let htmlString = ``;
      htmlString += `<svg class="c-circle" height="70" width="50">
      <circle cx="25" cy="25" r="20" stroke="red" stroke-width="5" fill="white" />
      </svg>`;
      htmlCirkel.innerHTML = htmlString;
    } else {
      const htmlCirkel = document.querySelector('.js-circle-gas');
      let htmlString = ``;
      htmlString += `<svg class="c-circle" height="70" width="50">
      <circle cx="25" cy="25" r="20" stroke="green" stroke-width="5" fill="white" />
      </svg>`;
      htmlCirkel.innerHTML = htmlString;
    }
  }
};

const getWaardeLoad = function (id) {
  console.log('in get waarde');
  handleData(`http://${lanIP}/api/v1/waardes/${id}`, showWaardes);
};

const loop = function () {
  setInterval(function () {
    setTimeout(function () {
      console.log('accelero');
      current_sensor = 1;
      getWaardeLoad(1);
    }, 1000);
    setTimeout(function () {
      console.log('pulse');
      current_sensor = 2;
      getWaardeLoad(2);
    }, 2000);
    setTimeout(function () {
      console.log('gas');
      current_sensor = 3;
      getWaardeLoad(3);
    }, 3000);
    console.log('in loop');
  }, 8000);
};

document.addEventListener('DOMContentLoaded', function () {
  console.info('DOM geladen');
  loop();
  listenToUI();
  listenToSocket();
});
