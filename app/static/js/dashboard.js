const socket = io();

/* Chart Js */
const ctx = document.getElementById('genderRatioChart').getContext('2d');
const genderRatioChart = new Chart(ctx, {
    type: 'bar', // You can choose 'line', 'bar', etc.
    data: {
        labels: ['Male', 'Female'],
        datasets: [{
            label: 'Gender Ratio',
            data: [0, 0], // Initial values
            backgroundColor: ['#007bff', '#dc3545'], // Blue for male, red for female
            borderColor: ['#0056b3', '#c82333'], // Darker shades for borders
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                beginAtZero: true
            },
            y: {
                beginAtZero: true
            }
        }
    }
});

// js/dashboard.js


socket.on('connect', () => {
    console.log('Connected to server');
    socket.emit('start_video');
});

socket.on('update_counts', (data) => {
    document.getElementById('male-count').textContent = data.male_count;
    document.getElementById('female-count').textContent = data.female_count;

    // Update the chart with new data
    genderRatioChart.data.datasets[0].data = [data.male_count, data.female_count];
    genderRatioChart.update();
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

socket.on('alert', function (data) {
    showToast(data.message);
});

function displayAlert(message) {
    var alertContainer = document.getElementById('alert-container');
    
    // Remove any existing alert divs
    while (alertContainer.firstChild) {
        alertContainer.removeChild(alertContainer.firstChild);
    }

    // Create a new alert div element
    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `${message}`;

    // Append the alert to the dashboard
    var alertContainer = document.getElementById('alert-container');
    alertContainer.appendChild(alertDiv);

    // Optionally, remove the alert after a certain time
    setTimeout(function () {
        alertDiv.remove();
    }, 5000); // Remove after 5 seconds
}

function showToast(message) {
    // Update the toast message
    document.querySelector('#liveToast .toast-body').textContent = message;

    // Get the toast element
    var toastElement = document.getElementById('liveToast');
    
    // Create a new Bootstrap Toast instance
    var toast = new bootstrap.Toast(toastElement);
    
    // Show the toast
    toast.show();
}

