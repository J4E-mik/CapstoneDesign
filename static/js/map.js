let map, marker;

function initTmap() {
    map = new Tmapv2.Map("map", {
        center: new Tmapv2.LatLng(37.5665, 126.9780),
        width: "100%",
        height: "600px",
        zoom: 15
    });

    marker = new Tmapv2.Marker({
        position: new Tmapv2.LatLng(37.5665, 126.9780),
        map: map
    });

    setInterval(fetchUserLocation, 3000);
}

function fetchUserLocation() {
    const userId = "user000";

    fetch(`/gps/location?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            console.log("[DEBUG] 위치 응답:", data);
            if (data.lat && data.lon) {
                updateUserMarker(data.lat, data.lon);
            }
        })
        .catch(console.error);
}

function updateUserMarker(lat, lon) {
    const newPos = new Tmapv2.LatLng(lat, lon);
    marker.setPosition(newPos);
    map.setCenter(newPos);
}

window.onload = initTmap;