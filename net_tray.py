import time
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import psutil

class TaskbarTrayMonitor:
    def __init__(self):
        self.is_running = True
        self.start_time = time.time()
        
        # Ambil data awal jaringan
        net_stats = psutil.net_io_counters()
        self.start_sent = net_stats.bytes_sent
        self.start_recv = net_stats.bytes_recv
        self.last_sent = net_stats.bytes_sent
        self.last_recv = net_stats.bytes_recv
        self.last_check_time = time.time()

        # String status untuk Tooltip
        self.tooltip_text = "Memulai monitor..."

        # Buat Ikon awal untuk System Tray
        self.icon = pystray.Icon(
            "net_monitor",
            icon=self.create_image(),
            title=self.tooltip_text,
            menu=pystray.Menu(
                item('Status Detail', self.show_status_action),
                item('Exit', self.exit_action)
            )
        )

    def create_image(self):
        """Membuat ikon generator sederhana berbentuk kotak ungu dengan simbol petir."""
        image = Image.new('RGB', (64, 64), color='#6F42C1')
        dc = ImageDraw.Draw(image)
        # Menggambar simbol kilat/petir kuning sederhana di dalam ikon tray
        dc.polygon([(32, 10), (45, 32), (35, 32), (32, 54), (19, 32), (29, 32)], fill='#00E676')
        return image

    def format_bytes(self, size_bytes):
        if size_bytes < 1024: return f"{size_bytes} B"
        elif size_bytes < 1024**2: return f"{size_bytes / 1024:.2f} KB"
        else: return f"{size_bytes / 1024**2:.2f} MB"

    def monitor_loop(self):
        while self.is_running:
            time.sleep(1)
            now = time.time()
            io = psutil.net_io_counters()
            
            # 1. Hitung Kecepatan
            time_delta = now - self.last_check_time
            if time_delta <= 0: time_delta = 1
            
            speed_sent = (io.bytes_sent - self.last_sent) / time_delta
            speed_recv = (io.bytes_recv - self.last_recv) / time_delta
            speed_total = speed_sent + speed_recv
            
            # 2. Hitung Total Data
            total_sent = io.bytes_sent - self.start_sent
            total_recv = io.bytes_recv - self.start_recv
            total_combined = total_sent + total_recv
            
            # 3. Hitung Durasi Waktu
            elapsed = int(now - self.start_time)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Update teks Tooltip yang akan muncul saat ikon didekati mouse
            self.tooltip_text = (
                f"⚡: {self.format_bytes(speed_total)}/s | ▲:{self.format_bytes(speed_sent)}/s | ▼: {self.format_bytes(speed_recv)}/s\n"
                f"📊: {self.format_bytes(total_combined)} | ⏱️: {hours:02d}:{minutes:02d}:{seconds:02d}"
            )
            
            # Perbarui title/tooltip ikon di taskbar secara live
            self.icon.title = self.tooltip_text
            
            self.last_sent = io.bytes_sent
            self.last_recv = io.bytes_recv
            self.last_check_time = now

    def show_status_action(self, icon, item):
        """Memunculkan notifikasi balon Windows saat menu diklik."""
        self.icon.notify(self.tooltip_text, title="Statistik Internet Aktif")

    def exit_action(self, icon, item):
        """Mematikan aplikasi total."""
        self.is_running = False
        self.icon.stop()

    def run(self):
        # Jalankan kalkulasi data jaringan di background thread
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        # Jalankan pystray ikon di main thread
        self.icon.run()

if __name__ == "__main__":
    app = TaskbarTrayMonitor()
    app.run()