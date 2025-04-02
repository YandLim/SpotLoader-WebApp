document.getElementById("download-BTN").addEventListener("click", function() {
    let btn = this;
    btn.disabled = true;  // Nonaktifkan tombol setelah diklik

    fetch("/run_download", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json()) 
    .then(data => {
        if (data.download_url) {
            window.location.href = "/download_zip";
            // btn.disabled = false; // Redirect ke link download
        } else {
            document.getElementById("response-text").innerText = data.message;
            // btn.disabled = false;  // Aktifkan tombol jika gagal
        }
    })
    .catch(error => {
        console.error("Error:", error);
        // btn.disabled = false;  // Pastikan tombol diaktifkan kembali jika ada error
    });
});