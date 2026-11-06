# Praktikum 10 — Blender Materials, UV & Texturing

**Nama:** Mario Napitupulu  
**NRP:** 5025241085  
**Aplikasi:** Blender 5.2.3  
**Engine render:** Cycles (CPU)  
**Output:** 1200 × 900 px

## Isi scene

Scene **Kestrel Workshop** menggabungkan toolbox Kestrel-09 hasil modeling Praktikum 9 dengan model lampu industri dari Poly Haven. Keduanya ditempatkan di atas meja kerja dengan papan nama, lalu diterangi key light hangat, fill light kebiruan, dan top light netral. Kamera memakai focal length 65 mm untuk komposisi produk dari sudut tiga perempat.

Toolbox menggunakan UV map `UV_Kestrel_Manual`. Seam ditandai pada batas terbuka dan transisi permukaan yang tajam, kemudian mesh di-unwrap dengan metode Angle Based dan island dikemas ke ruang UV. Saya memeriksa kerapian serta distorsi memakai checker sebelum memasang tekstur final.

## Material dan tekstur

Material buatan sendiri untuk toolbox memakai enam peta PNG 512 × 512 yang dibuat secara prosedural untuk tugas ini:

| Peta | Color space | Pemakaian |
|---|---|---|
| `kestrel09_basecolor.png` | sRGB | Warna permukaan |
| `kestrel09_ao.png` | Non-Color | Detail bayangan AO, dikalikan halus dengan base color |
| `kestrel09_roughness.png` | Non-Color | Variasi kekasaran |
| `kestrel09_metallic.png` | Non-Color | Nilai metalik |
| `kestrel09_normal.png` | Non-Color | Detail permukaan melalui node Normal Map |
| `kestrel09_emission.png` | sRGB | Aksen menyala pada material |

Model eksternal **Industrial Pipe Lamp** memakai peta PBR Poly Haven: diffuse/base color, AO, roughness, metallic, normal, dan emission. Peta data memakai Non-Color; diffuse dan emission memakai sRGB. Sumber model dan tekstur: [Poly Haven — Industrial Pipe Lamp](https://polyhaven.com/a/industrial_pipe_lamp). Aset Poly Haven dirilis di bawah [lisensi CC0](https://polyhaven.com/license).

Pada kedua material, peta masuk ke Principled BSDF. AO digabungkan secara halus dengan base color, dan peta normal diteruskan melalui node Normal Map. Lampu memakai peta emission untuk detail sumber cahayanya, dilengkapi pencahayaan scene agar bentuk dan bayangan tetap terbaca.

## Bukti proses dan hasil

- `screenshots/01_model.png` — toolbox sebelum tekstur final.
- `screenshots/02_seam.png` — seam UV.
- `screenshots/03_uv.png` — UV layout setelah island dikemas.
- `screenshots/04_checker.png` — uji checker untuk meninjau distribusi UV.
- `screenshots/05_nodes.png` — alur peta PBR ke Principled BSDF.
- `screenshots/06_final.png` — render scene final.

## Membuka proyek

Buka `P10_5025241085_Mario_Napitupulu.blend` di Blender. File Blender menyimpan tekstur yang digunakan dalam scene; folder `textures/` dan `external_assets/` turut disertakan sebagai file sumber. Untuk melihat komposisi kamera, pilih camera view lalu jalankan render dengan **F12**.

`build_praktikum10.py` adalah script bantu untuk membangun ulang scene. Script ini membaca file toolbox Praktikum 9 dari path lokal proyek, sehingga path `P9_BLEND` di awal script perlu disesuaikan bila folder sumber dipindah.

## Refleksi

Tantangan utama adalah menjaga texel tetap terbaca pada toolbox yang terdiri dari banyak panel dan detail kecil. Penandaan seam pada batas dan sudut tajam membantu membuka permukaan kotak tanpa merusak siluet utama. Checker dipakai untuk melihat sebaran UV sebelum tekstur buatan sendiri diterapkan. Perbedaan roughness dan metallic membuat toolbox terasa lebih seperti lapisan pelindung, sementara lampu memiliki respons logam yang lebih realistis. Susunan key, fill, dan top light membantu mempertahankan detail gelap sekaligus menunjukkan bayangan di atas meja.
