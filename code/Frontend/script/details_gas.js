'use strict';

const backend_IP = `http://127.0.0.1:5000`;
const backend = backend_IP + '/api/v1';
const lanIP = `${window.location.hostname}:5000`;

const showWaardes = function (jsonObject) {
  console.log('details');
  const htmlWaarde = document.querySelector('.js-list-details');
  let htmlString = ``;
  for (let waarde of jsonObject.waardes) {
    htmlString += `<li class="u-pt-8 u-pb-8">ID: ${waarde.historiekID} | Time: ${waarde.historiekTijd} | Value: ${waarde.historiekWaarde} %</li>`;
  }
  htmlWaarde.innerHTML = htmlString;
};

const getWaardeLoad = function (id) {
  console.log('in get waarde');
  handleData(`http://${lanIP}/api/v1/5waardes/${id}`, showWaardes);
};

const zoeken = function () {};

document.addEventListener('DOMContentLoaded', function () {
  console.info('DOM geladen');
  getWaardeLoad(3);
});
