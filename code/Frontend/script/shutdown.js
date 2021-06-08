'use strict';

const backend_IP = `http://127.0.0.1:5000`;
const backend = backend_IP + '/api/v1';
const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

const listenToUI = function () {
  const knop = document.querySelector('.js-shutdown');
  knop.addEventListener('click', function () {
    console.log('shutting off');
    socket.emit('F2B_shutdown');
  });
};

document.addEventListener('DOMContentLoaded', function () {
  console.info('DOM geladen');
  listenToUI();
});
