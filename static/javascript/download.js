try {
    const popup = document.getElementById("see-all-popup")
    const openBTN = document.getElementById("see-all-BTN")
    const close = document.querySelector(".close")

    openBTN.addEventListener("click", function() {
        popup.style.display = "block"
    });

    close.addEventListener("click", function() {
        popup.style.display = "none"
    });

    window.addEventListener("click", function(event) {
        if (event.target === popup) {
            popup.style.display = "none"
        }
    });
} catch (error) {
    console.warn("Couldn't find pop up window");
}


try {
    const download_btn = document.getElementById("download-album-BTN");
    download_btn.addEventListener("click", handleDownload);
} catch (error) {
    console.warn("download-album-BTN tidak ditemukan, lanjut ke download-song-BTN");
}

try {
    const download_btn_song = document.getElementById("download-song-BTN");
    download_btn_song.addEventListener("click", handleDownload);
} catch (error) {
    console.warn("download-song-BTN tidak ditemukan");
}

try {
    const download_btn_song = document.getElementById("download-playlist-BTN");
    download_btn_song.addEventListener("click", handleDownload);
} catch (error) {
    console.warn("download-song-BTN tidak ditemukan");
}


function handleDownload() {
    let btn = this;
    btn.disabled = true; // Nonaktifkan tombol setelah diklik

    fetch("/run_download", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.download_url) {
            window.location.href = "/download_zip";
            btn.disabled = false; // Redirect ke link download
        } else {
            document.getElementById("response-text").innerText = data.message;
            btn.disabled = false; // Aktifkan tombol jika gagal
        }
    })
    .catch(error => {
        console.error("Error:", error);
        btn.disabled = false; // Pastikan tombol diaktifkan kembali jika ada error
    });
}