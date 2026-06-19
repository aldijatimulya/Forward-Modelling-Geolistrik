import os
import numpy as np
import matplotlib.pyplot as plt
# Pastikan resipy sudah terinstal: pip install resipy
import resipy as rp

print("=========================================================")
print("  PROGRAM FORWARD MODELING GEOLISTRIK 2D AUTOMATION      ")
print("=========================================================")

# 1. Membuat Direktori untuk Menyimpan Hasil Output Gambar
output_dir = "hasil_simulasi_forward"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. Definisikan Parameter Variasi Sesuai Arahan Penelitian
variasi_spasi = [1.0, 2.0, 3.0]
# Kode tipe konfigurasi di ResIPy: 'w' = Wenner, 'ws' = Wenner-Schlumberger, 'dd' = Dipole-Dipole
variasi_konfigurasi = {
    'Wenner': 'w',
    'Wenner-Schlumberger': 'ws',
    'Dipole-Dipole': 'dd'
}

# Jumlah elektroda disesuaikan dengan data lapangan Anda (contoh: 24 elektroda)
jumlah_elektroda = 24 

# 3. Looping Otomatis untuk Mengeksekusi Semua Kombinasi
for spasi in variasi_spasi:
    for nama_konfig, kode_konfig in variasi_konfigurasi.items():
        print(f"\n[PROSES] Menghitung {nama_konfig} dengan Spasi {spasi} meter...")
        
        # Membuat objek survey baru di ResIPy
        k = rp.Project()
        
        # Membuat susunan elektroda di permukaan (Z = 0)
        x_coords = np.arange(0, jumlah_elektroda * spasi, spasi)
        elec_coords = np.zeros((jumlah_elektroda, 3))
        elec_coords[:, 0] = x_coords  # Mengisi posisi X
        
        k.setElec(elec_coords)
        
        # Membuat rangkaian skema penembakan arus berdasarkan konfigurasi pilihan
        k.createSequence(kode_konfig)
        
        # 4. Mendesain Model Geologi Acuan (True Resistivity Grid)
        # Membuat mesh batuan bawah permukaan
        k.createMesh(mesh_type='survey')
        
        # Mengisi nilai resistivitas background (Misal: Lempung = 100 Ohm.m)
        true_resistivity = np.ones(len(k.mesh.elements)) * 100.0
        
        # Menyisipkan Lapisan Gambut (Misal: Resistivitas 30 Ohm.m pada kedalaman dangkal di tengah)
        # Kita memfilter elemen mesh berdasarkan koordinat X dan Z nya
        for i, el in enumerate(k.mesh.elements):
            centroid = el.centroid() # Mendapatkan titik tengah elemen [X, Y, Z]
            x_pos = centroid[0]
            z_pos = centroid[2] # Di geofisika Python, Z biasanya bernilai negatif ke bawah
            
            # Jika posisi berada di kedalaman 0 sampai -3 meter, dan di tengah bentangan
            if (-3.0 < z_pos <= 0.0) and (5.0 < x_pos < (jumlah_elektroda * spasi) - 5.0):
                true_resistivity[i] = 30.0 # Ubah menjadi resistivitas gambut
                
        # Masukkan array resistivitas sejati ini ke dalam mesh model
        k.mesh.setRes(true_resistivity)
        
        # 5. Jalankan Forward Computation (Menghitung Potensial & Apparent Resistivity)
        k.forward()
        
        # 6. Pembuatan Grafik Penampang Kontur Semu (Pseudosection)
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Mengambil data koordinat semu (pseudo-plots)
        # ResIPy memiliki fungsi built-in untuk memplot pseudosection data
        k.plotPseudosection(attr='app_res', ax=ax, cmap='jet')
        
        ax.set_title(f"Pseudosection Sintetik: {nama_konfig} (Spasi {spasi}m)", fontsize=12, fontweight='bold')
        ax.set_xlabel("Panjang Lintasan / Midpoint (m)")
        ax.set_ylabel("Pseudo-Depth (m)")
        
        # Simpan gambar secara otomatis dengan penamaan yang rapi
        filename = f"{output_dir}/Forward_{nama_konfig.replace('-', '_')}_spasi_{int(spasi)}m.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[SUKSES] Gambar berhasil disimpan: {filename}")

print("\n=========================================================")
print("  SIMULASI SELESAI! SILAKAN CEK FOLDER: hasil_simulasi_forward")
print("=========================================================")
