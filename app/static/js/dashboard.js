// js/dashboard.js
const socket = io();

socket.on('connect', () => {
    console.log('Connected to server');
    socket.emit('start_video');
});

socket.on('update_counts', (data) => {
    document.getElementById('male-count').textContent = data.male_count;
    document.getElementById('female-count').textContent = data.female_count;
});

socket.on('video_frame', (frame) => {
    const videoElement = document.getElementById('video');
    const loader = document.getElementById('loader');
    
    // Hide the loader and display the video when the first frame is received
    if (loader.style.display !== 'none') {
        loader.style.display = 'none';
        videoElement.style.display = 'block';
    }
    videoElement.src = 'data:image/jpeg;base64,' + frame;
});

socket.on('alert', function(data) {
    displayAlert(data.message);
});

function displayAlert(message) {
    // Create a new alert div element
    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `${message}`;

    // Append the alert to the dashboard
    var alertContainer = document.getElementById('alert-container');
    alertContainer.appendChild(alertDiv);

    // Optionally, remove the alert after a certain time
    setTimeout(function() {
        alertDiv.remove();
    }, 10000); // Remove after 10 seconds
}
