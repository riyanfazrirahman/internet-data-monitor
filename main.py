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
        
        self.start_sent = 0
        self.start_recv = 0
        self.last_sent = 0
        self.last_recv = 0
        self.last_check_time = 0

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
        self.btn_action.pack(fill=tk.X, side=tk.BOTTOM, pady=20, ipady=10)

    def toggle_monitoring(self):
        if not self.is_running:
            # Aksi START
            self.is_running = True
            self.btn_action.config(text="STOP MONITORING", style="Stop.TButton")
            
            # Waktu
            self.start_time = time.time()
            local_start = time.strftime("%H:%M:%S", time.localtime(self.start_time))
            self.lbl_time_start.config(text=f"Waktu Mulai: {local_start}")
            
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
            
            # --- Update Tampilan Ke UI (Thread-safe safely) ---
            self.root.after(0, self.update_ui_elements, 
                            speed_total_kb, speed_sent_kb, speed_recv_kb,
                            total_usage_mb, total_sent_mb, total_recv_mb, 
                            time_string)

    def update_ui_elements(self, spd_tot, spd_snt, spd_rcv, use_tot, use_snt, use_rcv, duration):
        # Update UI Kecepatan
        if spd_tot >= 1024:
            self.lbl_speed_total.config(text=f"{spd_tot/1024:.2f} MB/s")
        else:
            self.lbl_speed_total.config(text=f"{spd_tot:.2f} KB/s")
            
        self.lbl_speed_sent.config(text=f"Sent: {spd_snt:.2f} KB/s")
        self.lbl_speed_recv.config(text=f"Recv: {spd_rcv:.2f} KB/s")
        
        # Update UI Total Kuota
        self.lbl_usage_total.config(text=f"{use_tot:.2f} MB")
        self.lbl_usage_sent.config(text=f"Sent: {use_snt:.2f} MB")
        self.lbl_usage_recv.config(text=f"Recv: {use_rcv:.2f} MB")
        
        # Update UI Waktu
        self.lbl_time_total.config(text=f"Total Durasi: {duration}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernDataTracker(root)
    root.mainloop()