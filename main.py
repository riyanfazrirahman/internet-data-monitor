import tkinter as tk
from tkinter import ttk
import psutil
import time
import threading

class DataTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Data Tracker")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        
        # Variabel Status
        self.is_running = False
        self.start_bytes_sent = 0
        self.start_bytes_recv = 0
        
        self.setup_ui()

    def setup_ui(self):
        # Frame Utama
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Label Judul
        title_label = ttk.Label(main_frame, text="Pencatat Kuota Internet", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)

        # Label Status
        self.status_label = ttk.Label(main_frame, text="Status: Berhenti", font=("Helvetica", 10), foreground="red")
        self.status_label.pack(pady=5)

        # Label untuk menampilkan hasil data
        self.data_label = ttk.Label(main_frame, text="Total Penggunaan: 0.00 MB", font=("Helvetica", 12))
        self.data_label.pack(pady=15)

        # Tombol Start / Stop
        self.btn_toggle = ttk.Button(main_frame, text="START", command=self.toggle_tracking)
        self.btn_toggle.pack(pady=10)

    def convert_to_mb(self, bytes_value):
        # Mengubah bytes menjadi Megabytes (MB)
        return bytes_value / (1024 * 1024)

    def toggle_tracking(self):
        if not self.is_running:
            # Aksi ketika tombol START ditekan
            self.is_running = True
            self.btn_toggle.config(text="STOP")
            self.status_label.config(text="Status: Mencatat...", foreground="green")
            
            # Ambil data internet saat ini sebagai titik awal (baseline)
            io_counters = psutil.net_io_counters()
            self.start_bytes_sent = io_counters.bytes_sent
            self.start_bytes_recv = io_counters.bytes_recv
            
            # Jalankan loop perhitungan di background thread agar GUI tidak membeku (freeze)
            self.tracking_thread = threading.Thread(target=self.update_loop, daemon=True)
            self.tracking_thread.start()
        else:
            # Aksi ketika tombol STOP ditekan
            self.is_running = False
            self.btn_toggle.config(text="START")
            self.status_label.config(text="Status: Berhenti (Selesai)", foreground="red")

    def update_loop(self):
        while self.is_running:
            # Ambil data internet terbaru
            current_io = psutil.net_io_counters()
            
            # Hitung selisihnya dari tombol start ditekan
            bytes_sent = current_io.bytes_sent - self.start_bytes_sent
            bytes_recv = current_io.bytes_recv - self.start_bytes_recv
            total_bytes = bytes_sent + bytes_recv
            
            # Konversi ke MB
            total_mb = self.convert_to_mb(total_bytes)
            
            # Update teks di UI Tkinter
            self.data_label.config(text=f"Total Penggunaan: {total_mb:.2f} MB")
            
            # Jeda 1 detik sebelum mengambil data berikutnya
            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = DataTrackerApp(root)
    root.mainloop()