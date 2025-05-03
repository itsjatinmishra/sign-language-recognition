let videoStream = null;
let video = document.getElementById("video");
let canvas = document.getElementById("canvas");
let context = canvas && canvas.getContext ? canvas.getContext("2d") : null;

// GSAP Animations
document.addEventListener("DOMContentLoaded", function () {
    gsap.from(".navbar", { duration: 1, y: -50, opacity: 0, ease: "power3.out" });
    gsap.from(".container", { duration: 1, y: 50, opacity: 0, delay: 0.5, ease: "power3.out" });

    // Apply Dark Mode on Page Load
    if (localStorage.getItem("darkMode") === "true") {
        document.body.classList.add("dark-mode");
        document.querySelector(".navbar").classList.add("dark-mode");
    }
});

// Dark Mode Toggle
function toggleDarkMode() {
    let body = document.body;
    body.classList.toggle("dark-mode");
    localStorage.setItem("darkMode", body.classList.contains("dark-mode"));
}

// Start Camera
function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoStream = stream;
            video.srcObject = stream;
            video.style.display = "block";
        })
        .catch(error => {
            alert("🚫 Camera access was denied! Please allow camera permission.");
            console.error("Camera access error:", error);
        });
}

// Stop Camera
function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
        video.style.display = "none";
    }
}

// Take Picture
function takePicture() {
    if (!canvas || !context) {
        alert("⚠️ Camera not initialized!");
        return;
    }
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    document.getElementById("capturedImage").src = canvas.toDataURL("image/png");
    document.getElementById("capturedImage").style.display = "block";
}

// Predict from Camera Image
function predictCapturedImage() {
    if (!canvas || !context) {
        alert("⚠️ Error: Camera is not initialized!");
        return;
    }

    let imageData = canvas.toDataURL("image/png");

    fetch("/predict_camera", {
        method: "POST",
        body: JSON.stringify({ image: imageData }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("predictionResult").innerText = "Prediction: " + data.prediction;
        speakWord(data.prediction);
        setTimeout(() => location.reload(), 5000);
    })
    .catch(error => console.error("Prediction Error:", error));
}

// Upload Image
function uploadImage() {
    let fileInput = document.getElementById("imageUpload");
    let simpleFileInput = document.getElementById("simpleUpload");
    let file = fileInput.files[0] || simpleFileInput.files[0];

    if (!file) {
        alert("⚠️ Please select an image first!");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    fetch("/predict", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("predictionResult").innerText = "Prediction: " + data.prediction;
        speakWord(data.prediction);
        setTimeout(() => location.reload(), 30000);
    })
    .catch(error => console.error("Prediction Error:", error));
}

// Show Image Preview Before Uploading
document.getElementById("imageUpload").addEventListener("change", function () {
    previewImage(this);
});

document.getElementById("simpleUpload").addEventListener("change", function () {
    previewImage(this);
});

function previewImage(input) {
    let file = input.files[0];
    if (file) {
        let reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById("preview-image").src = e.target.result;
            document.getElementById("preview-image").style.display = "block";
            document.getElementById("predict-btn").style.display = "block";
        };
        reader.readAsDataURL(file);
    }
}

// Drag & Drop Upload Feature
let dropArea = document.getElementById("drop-area");
let fileInput = document.getElementById("imageUpload");

if (dropArea) {
    // Prevent default behaviors
    ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight the drop area when file is dragged over
    ["dragenter", "dragover"].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add("highlight"), false);
    });

    // Remove highlight when dragging leaves the area
    ["dragleave", "drop"].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove("highlight"), false);
    });

    // Handle dropped files
    dropArea.addEventListener("drop", function (e) {
        let files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            previewImage(fileInput); // Show preview
        }
    });
}

// Text-to-Speech
function speakWord(word) {
    let speech = new SpeechSynthesisUtterance();
    speech.text = word;
    speech.rate = 1;
    speech.pitch = 1;
    speech.volume = 1;
    window.speechSynthesis.speak(speech);
}
