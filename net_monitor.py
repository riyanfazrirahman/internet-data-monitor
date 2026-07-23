import tkinter as tk
from tkinter import ttk
import psutil
import time
import threading

class ModernDataTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Monitor")
        self.root.geometry("400x650")
        self.root.configure(bg="#F8F9FA") # Background abu-abu sangat muda bersih
        
        # Variabel Logika
        self.is_running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.local_start_str = "--:--:--"
        
        self.start_sent = 0
        self.start_recv = 0
        self.last_sent = 0
        self.last_recv = 0
        self.last_check_time = 0

        # Menyimpan data string terakhir untuk disuplai ke overlay saat aktif
        self.current_duration = "00:00:00"
        self.txt_speed_total = "0.00 KB/s"
        self.txt_speed_sent = "Sent: 0.00 KB/s"
        self.txt_speed_recv = "Recv: 0.00 KB/s"
        self.txt_usage_total = "0.00 MB"

        # Variabel Overlay
        self.overlay_window = None

        # Protokol saat tombol X di Window Utama ditekan
        self.root.protocol("WM_DELETE_WINDOW", self.show_overlay)

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Konfigurasi Font & Warna Dasar Komponen
        self.style.configure("TLabel", background="#F8F9FA", font=("Helvetica", 10))
        self.style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
        
        # Gaya Tombol Modern
        self.style.configure("Start.TButton", font=("Helvetica", 11, "bold"), foreground="white", background="#6F42C1", borderwidth=0)
        self.style.map("Start.TButton", background=[("active", "#5A32A3")])
        
        self.style.configure("Stop.TButton", font=("Helvetica", 11, "bold"), foreground="white", background="#DC3545", borderwidth=0)
        self.style.map("Stop.TButton", background=[("active", "#BD2130")])

    def setup_ui(self):
        # --- HEADER ---
        header_frame = tk.Frame(self.root, bg="#FFFFFF", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        lbl_title = tk.Label(header_frame, text="Data Monitor", font=("Helvetica", 14, "bold"), bg="#FFFFFF", fg="#212529")
        lbl_title.pack(side=tk.LEFT, padx=20, pady=15)
        
        # --- BODY WRAPPER ---
        body = tk.Frame(self.root, bg="#F8F9FA", padx=20, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        # Bagian 1: Kecepatan Saat Ini (Real-time Speed) - Card Merah Muda
        card_speed = tk.Frame(body, bg="#FFE3E3", bd=0, highlightthickness=1, highlightbackground="#FFC9C9")
        card_speed.pack(fill=tk.X, pady=10, ipady=15)
        
        lbl_speed_title = tk.Label(card_speed, text="⚡ Kecepatan Internet", font=("Helvetica", 11, "bold"), bg="#FFE3E3", fg="#C92A2A")
        lbl_speed_title.pack(anchor="w", padx=15, pady=(5,0))
        
        self.lbl_speed_total = tk.Label(card_speed, text="0.00 KB/s", font=("Helvetica", 20, "bold"), bg="#FFE3E3", fg="#212529")
        self.lbl_speed_total.pack(anchor="w", padx=15)
        
        frame_speed_sub = tk.Frame(card_speed, bg="#FFE3E3")
        frame_speed_sub.pack(fill=tk.X, padx=15, pady=(5,0))
        self.lbl_speed_sent = tk.Label(frame_speed_sub, text="Sent: 0.00 KB/s", font=("Helvetica", 9), bg="#FFE3E3", fg="#868E96")
        self.lbl_speed_sent.pack(side=tk.LEFT)
        self.lbl_speed_recv = tk.Label(frame_speed_sub, text="Recv: 0.00 KB/s", font=("Helvetica", 9), bg="#FFE3E3", fg="#868E96")
        self.lbl_speed_recv.pack(side=tk.RIGHT)

        # Bagian 2: Total Digunakan (Data Usage) - Card Hijau Muda
        card_usage = tk.Frame(body, bg="#E3F9E5", bd=0, highlightthickness=1, highlightbackground="#C3FAE8")
        card_usage.pack(fill=tk.X, pady=10, ipady=15)
        
        lbl_usage_title = tk.Label(card_usage, text="📊 Total Digunakan", font=("Helvetica", 11, "bold"), bg="#E3F9E5", fg="#2B8A3E")
        lbl_usage_title.pack(anchor="w", padx=15, pady=(5,0))
        
        self.lbl_usage_total = tk.Label(card_usage, text="0.00 MB", font=("Helvetica", 20, "bold"), bg="#E3F9E5", fg="#212529")
        self.lbl_usage_total.pack(anchor="w", padx=15)
        
        frame_usage_sub = tk.Frame(card_usage, bg="#E3F9E5")
        frame_usage_sub.pack(fill=tk.X, padx=15, pady=(5,0))
        self.lbl_usage_sent = tk.Label(frame_usage_sub, text="Sent: 0.00 MB", font=("Helvetica", 9), bg="#E3F9E5", fg="#868E96")
        self.lbl_usage_sent.pack(side=tk.LEFT)
        self.lbl_usage_recv = tk.Label(frame_usage_sub, text="Recv: 0.00 MB", font=("Helvetica", 9), bg="#E3F9E5", fg="#868E96")
        self.lbl_usage_recv.pack(side=tk.RIGHT)

        # Bagian 3: Waktu / Timer - Card Ungu/Putih info
        card_time = tk.Frame(body, bg="#F3F0FF", bd=0, highlightthickness=1, highlightbackground="#E5DBFF")
        card_time.pack(fill=tk.X, pady=10, ipady=12)
        
        lbl_time_title = tk.Label(card_time, text="⏱️ Informasi Waktu", font=("Helvetica", 10, "bold"), bg="#F3F0FF", fg="#5F3DC4")
        lbl_time_title.pack(anchor="w", padx=15, pady=(5,0))
        
        self.lbl_time_start = tk.Label(card_time, text="Waktu Mulai: --:--:--", font=("Helvetica", 10), bg="#F3F0FF", fg="#495057")
        self.lbl_time_start.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_time_total = tk.Label(card_time, text="Total Durasi: 00:00:00", font=("Helvetica", 12, "bold"), bg="#F3F0FF", fg="#212529")
        self.lbl_time_total.pack(anchor="w", padx=15, pady=2)

        # --- FOOTER BUTTON ---
        self.btn_action = ttk.Button(body, text="START MONITORING", style="Start.TButton", command=self.toggle_monitoring)
        self.btn_action.pack(fill=tk.X, side=tk.BOTTOM, pady=5, ipady=10)

        # Tombol manual aktifkan overlay tanpa perlu klik close window
        self.btn_overlay = ttk.Button(body, text="AKTIFKAN OVERLAY", command=self.show_overlay)
        self.btn_overlay.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 10), ipady=5)

    def toggle_monitoring(self):
        if not self.is_running:
            # Aksi START
            self.is_running = True
            self.btn_action.config(text="STOP MONITORING", style="Stop.TButton")
            
            # Waktu
            self.start_time = time.time()
            self.local_start_str = time.strftime("%H:%M:%S", time.localtime(self.start_time))
            self.lbl_time_start.config(text=f"Waktu Mulai: {self.local_start_str}")
            
            # Ambil kuota internet awal
            io = psutil.net_io_counters()
            self.start_sent = io.bytes_sent
            self.start_recv = io.bytes_recv
            
            # Inisialisasi penghitung kecepatan internet
            self.last_sent = io.bytes_sent
            self.last_recv = io.bytes_recv
            self.last_check_time = time.time()
            
            # Jalankan background thread
            threading.Thread(target=self.monitor_loop, daemon=True).start()
        else:
            # Aksi STOP
            self.is_running = False
            self.btn_action.config(text="START MONITORING", style="Start.TButton")
            
            # Reset label kecepatan saat di-stop
            self.lbl_speed_total.config(text="0.00 KB/s")
            self.lbl_speed_sent.config(text="Sent: 0.00 KB/s")
            self.lbl_speed_recv.config(text="Recv: 0.00 KB/s")
            
            # Reset variabel teks overlay
            self.txt_speed_total = "0.00 KB/s"
            self.txt_speed_sent = "Sent: 0.00 KB/s"
            self.txt_speed_recv = "Recv: 0.00 KB/s"
            
            if self.overlay_window:
                self.update_overlay_ui()

    def monitor_loop(self):
        while self.is_running:
            time.sleep(1)
            
            now = time.time()
            io = psutil.net_io_counters()
            
            # 1. Hitung Kecepatan Jaringan (Speed per Second)
            time_delta = now - self.last_check_time
            if time_delta <= 0: time_delta = 1
                
            speed_sent_bytes = (io.bytes_sent - self.last_sent) / time_delta
            speed_recv_bytes = (io.bytes_recv - self.last_recv) / time_delta
            speed_total_bytes = speed_sent_bytes + speed_recv_bytes
            
            # Format kecepatan (KB/s atau MB/s)
            speed_total_kb = speed_total_bytes / 1024
            speed_sent_kb = speed_sent_bytes / 1024
            speed_recv_kb = speed_recv_bytes / 1024
            
            # 2. Hitung Total Data yang Digunakan (Sejak Start)
            total_sent_mb = (io.bytes_sent - self.start_sent) / (1024 * 1024)
            total_recv_mb = (io.bytes_recv - self.start_recv) / (1024 * 1024)
            total_usage_mb = total_sent_mb + total_recv_mb
            
            # 3. Hitung Waktu Durasi
            self.elapsed_time = int(now - self.start_time)
            hours, remainder = divmod(self.elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Simpan data sekarang untuk iterasi kecepatan berikutnya
            self.last_sent = io.bytes_sent
            self.last_recv = io.bytes_recv
            self.last_check_time = now
            
            # Simpan string untuk didistribusikan ke Window Utama dan Overlay secara realtime
            if speed_total_kb >= 1024:
                self.txt_speed_total = f"{speed_total_kb/1024:.2f} MB/s"
            else:
                self.txt_speed_total = f"{speed_total_kb:.2f} KB/s"
                
            self.txt_speed_sent = f"Sent: {speed_sent_kb:.2f} KB/s"
            self.txt_speed_recv = f"Recv: {speed_recv_kb:.2f} KB/s"
            self.txt_usage_total = f"{total_usage_mb:.2f} MB"
            self.current_duration = time_string

            # --- Update Tampilan Ke UI ---
            self.root.after(0, self.update_ui_elements, 
                            speed_total_kb, speed_sent_kb, speed_recv_kb,
                            total_usage_mb, total_sent_mb, total_recv_mb, 
                            time_string)

    def update_ui_elements(self, spd_tot, spd_snt, spd_rcv, use_tot, use_snt, use_rcv, duration):
        # Update Window Utama jika sedang aktif terbuka
        if self.root.winfo_viewable():
            if spd_tot >= 1024:
                self.lbl_speed_total.config(text=f"{spd_tot/1024:.2f} MB/s")
            else:
                self.lbl_speed_total.config(text=f"{spd_tot:.2f} KB/s")
                
            self.lbl_speed_sent.config(text=f"Sent: {spd_snt:.2f} KB/s")
            self.lbl_speed_recv.config(text=f"Recv: {spd_rcv:.2f} KB/s")
            self.lbl_usage_total.config(text=f"{use_tot:.2f} MB")
            self.lbl_usage_sent.config(text=f"Sent: {use_snt:.2f} MB")
            self.lbl_usage_recv.config(text=f"Recv: {use_rcv:.2f} MB")
            self.lbl_time_total.config(text=f"Total Durasi: {duration}")

        # Update Jendela Overlay secara real-time jika overlay sedang aktif mendeteksi
        if self.overlay_window and self.overlay_window.winfo_exists():
            self.update_overlay_ui()

    def show_overlay(self):
        """Sembunyikan Window utama, nyalakan Overlay Semi-Transparan yang Jelas."""
        self.root.withdraw()

        if self.overlay_window is not None:
            return

        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.title("NetOverlay")
        
        # Pengaturan Windowless & Paling Depan
        self.overlay_window.overrideredirect(True)
        self.overlay_window.attributes("-topmost", True)
        
        # PERBAIKAN: Menggunakan alpha transparency (0.8 = 80% opacity)
        # Background diset abu-abu gelap/hitam solid agar teks terang di atasnya kontras dan tajam
        bg_color = "#1E1E24" 
        self.overlay_window.configure(bg=bg_color)
        self.overlay_window.attributes("-alpha", 0.82) # Mengatur tingkat transparan seluruh jendela

        # Posisi di Kanan Bawah Layar Monitor
        screen_width = self.overlay_window.winfo_screenwidth()
        screen_height = self.overlay_window.winfo_screenheight()
        self.overlay_window.geometry(f"200x145+{screen_width - 220}+{screen_height - 210}")

        # Drag Handler Mouse Klik Kiri
        self.overlay_window.bind("<Button-1>", self.start_drag)
        self.overlay_window.bind("<B1-Motion>", self.do_drag)

        # Setup Label di Overlay dengan kontras warna yang tajam (Neon/Putih di atas Gelap)
        style_title = {"bg": bg_color, "fg": "#BB86FC", "font": ("Helvetica", 9, "bold")}
        style_main = {"bg": bg_color, "fg": "#00E676", "font": ("Helvetica", 16, "bold")} # Hijau neon untuk speed utama
        style_sub = {"bg": bg_color, "fg": "#FFFFFF", "font": ("Helvetica", 9, "bold")}
        style_time = {"bg": bg_color, "fg": "#A5A5A5", "font": ("Helvetica", 8, "bold")}

        tk.Label(self.overlay_window, text="⚡ INTERNET SPEED", **style_title).pack(pady=(8, 0))
        
        self.ol_speed_total = tk.Label(self.overlay_window, text=self.txt_speed_total, **style_main)
        self.ol_speed_total.pack()

        self.ol_speed_sent = tk.Label(self.overlay_window, text=self.txt_speed_sent, **style_time)
        self.ol_speed_sent.pack()

        self.ol_speed_recv = tk.Label(self.overlay_window, text=self.txt_speed_recv, **style_time)
        self.ol_speed_recv.pack()

        self.ol_usage_total = tk.Label(self.overlay_window, text=f"📊 Total Data: {self.txt_usage_total}", **style_sub)
        self.ol_usage_total.pack(pady=(5, 0))

        self.ol_time_info = tk.Label(self.overlay_window, text=f"Start: {self.local_start_str} | Dur: {self.current_duration}", **style_time)
        self.ol_time_info.pack(pady=(4, 0))

        # Menu Klik Kanan untuk Aksi Manajemen
        self.menu = tk.Menu(self.overlay_window, tearoff=0)
        self.menu.add_command(label="Buka Window Utama", command=self.restore_main_window)
        self.menu.add_separator()
        self.menu.add_command(label="Exit Aplikasi", command=self.exit_application)

        self.overlay_window.bind("<Button-3>", self.show_popup_menu)
    def update_overlay_ui(self):
        """Memperbarui teks pada widget komponen overlay."""
        self.ol_speed_total.config(text=self.txt_speed_total)
        self.ol_speed_sent.config(text=self.txt_speed_sent)
        self.ol_speed_recv.config(text=self.txt_speed_recv)
        self.ol_usage_total.config(text=f"📊 Total Data: {self.txt_usage_total}")
        self.ol_time_info.config(text=f"Start: {self.local_start_str} | Dur: {self.current_duration}")

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def do_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.overlay_window.winfo_x() + deltax
        y = self.overlay_window.winfo_y() + deltay
        self.overlay_window.geometry(f"+{x}+{y}")

    def show_popup_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def restore_main_window(self):
        if self.overlay_window:
            self.overlay_window.destroy()
            self.overlay_window = None
        self.root.deiconify()

    def exit_application(self):
        self.is_running = False
        if self.overlay_window:
            self.overlay_window.destroy()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernDataTracker(root)
    root.mainloop()