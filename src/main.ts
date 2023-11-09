import './style.css';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

const aero = L.tileLayer('map/{z}/{x}/{y}.png', {
    attribution: 'Kartendaten &copy; <a href="https://www.openflightmaps.org/copyright">OpenFlightMap</a>',
    maxZoom: 11,
    minZoom: 4,

});


const map = L.map('app', {
    center: [52.7924386,9.930284],
    zoom: 8,
    zoomControl: true,
    layers: [aero]
});

const zimt = [53.0551608,8.7835603]

const marker = L.marker(zimt).addTo(map);

const circle = L.circle(zimt, {
    color: 'green',
    fillColor: '#00ff3366',
    fillOpacity: 0.3,
    radius: 200_000
}).addTo(map);

const circle1 = L.circle(zimt, {
    color: 'blue',
    fillColor: '#3300ff66',
    fillOpacity: 0.3,
    radius: 50_000
}).addTo(map);

const circle2 = L.circle(zimt, {
    color: 'red',
    fillColor: '#ff003366',
    fillOpacity: 0.3,
    radius: 10_000
}).addTo(map);

