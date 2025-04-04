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
    let progressText = document.getElementById("downloading-progress");
    let statusText = document.getElementById("status-text"); // Tambahkan elemen untuk status

    progressText.innerText = "Starting . . .";
    statusText.innerText = "Initializing...";

    statusText.style.display = "block";
    progressText.style.display = "block";

    let eventSource = new EventSource("/download_progress");

    eventSource.onmessage = function(event) {
        let data = event.data.split("|"); // Pisahkan berdasarkan "|"
        let progress = parseInt(data[0]); // Ambil persentase progress
        let status = data[1]; // Ambil status teks

        if (!isNaN(progress)) {
            progressText.innerText = `Downloading ${progress}%`;
        }

        if (status) {
            statusText.innerText = status;
        }

        if (progress >= 100) {
            eventSource.close();
            progressText.innerText = "✅ Download complete!";
            statusText.style.display = "none"; // Sembunyikan status-text saat selesai
            btn.disabled = false;            
        }
    };

    fetch("/run_download", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.download_url) {
            window.location.href = data.download_url; // Redirect ke link download
            btn.disabled = false;
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
