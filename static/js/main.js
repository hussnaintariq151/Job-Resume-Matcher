// Apply fade-in animation on page load
document.addEventListener("DOMContentLoaded", function () {
    const introContainer = document.querySelector(".intro-container");
    if (introContainer) {
        introContainer.classList.add("fade-in");
    }

    const formContainer = document.querySelector(".form-container");
    if (formContainer) {
        formContainer.classList.add("fade-in");
    }

    // Handle file input label update
    const fileInput = document.getElementById("resumeFile");
    const fileLabel = document.getElementById("fileLabel");

    if (fileInput && fileLabel) {
        fileInput.addEventListener("change", function () {
            const fileName = this.files[0]?.name || "Choose file";
            fileLabel.innerText = fileName;
        });
    }

    // Add loading text after form submit
    const form = document.querySelector("form");
    const loadingText = document.getElementById("loadingText");

    if (form && loadingText) {
        form.addEventListener("submit", function () {
            loadingText.innerText = "Uploading resume and analyzing... Please wait.";
        });
    }
});
