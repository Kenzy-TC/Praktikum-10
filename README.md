# Praktikum 10 — Blender Materials, UV & Texturing

| Data | Keterangan |
|---|---|
| Kelompok | 2 |
| Nama | Mario Napitupulu |
| NRP | 5025241085 |
| Objek utama | Radio retro portabel **Mistral 58** |
**Blender:** 5.2.3 · **Render:** Cycles, 1200 × 900 px

## Scene dan objek

Radio Mistral 58 dibuat untuk tugas ini. Modelnya memiliki casing membulat, speaker grille, dial frekuensi, layar, dua knob, tombol preset, handle, dan antena. Radio digabungkan dengan lampu industri dari Poly Haven di atas meja kerja. Key light hangat, fill light kebiruan, rim light, dan top light membantu menampilkan bentuk serta perbedaan material. Kamera memakai focal length 65 mm dengan sudut tiga perempat.

Model eksternal: [Industrial Pipe Lamp — Poly Haven](https://polyhaven.com/a/industrial_pipe_lamp), berlisensi [CC0](https://polyhaven.com/license). Peta yang disertakan: diffuse/base color, AO, roughness, metallic, normal OpenGL, dan emission.

## Modeling, UV, dan tekstur

Casing radio dibuat dari mesh box dengan bevel pada sudutnya. Seam ditandai di tepi-tepi tajam, lalu Smart UV Project menghasilkan UV map `UV_Mistral58_Smart`; island dikemas ke bidang UV. Pass checker dipakai untuk meninjau sebaran UV sebelum material final dipasang.

Enam peta casing dibuat sendiri secara prosedural pada resolusi 512 × 512 px dan tersedia di folder `textures/`:

| Peta | Color space | Fungsi |
|---|---|---|
| `radio_basecolor.png` | sRGB | Warna cat krem dan variasi permukaan |
| `radio_ao.png` | Non-Color | Ambient occlusion |
| `radio_roughness.png` | Non-Color | Kekasaran permukaan |
| `radio_metallic.png` | Non-Color | Nilai metallic |
| `radio_normal.png` | Non-Color | Detail normal melalui node Normal Map |
| `radio_emission.png` | sRGB | Mask emission |

Enam peta lampu Poly Haven juga disertakan di folder yang sama. Di material PBR, AO dikalikan halus dengan base color dan peta normal diteruskan lewat node Normal Map. Bagian radio seperti speaker, dial, knob, serta trim memakai material terpisah agar bakelit/plastik, kaca, cat, kuningan, dan logam punya respons yang berbeda. Tekstur gambar tersimpan di dalam file Blender agar project dapat dibuka tanpa mencari ulang file sumber.

## Cara membuka dan mendemokan

1. Buka `P10_Kelompok2_Mario_Napitupulu.blend` di Blender.
2. Tekan **Numpad 0** untuk melihat kamera. Ubah viewport ke **Material Preview** untuk melihat material.
3. Pilih `Mistral58_Body`, buka workspace **UV Editing**, masuk **Edit Mode**, lalu tekan **A**. Tunjukkan UV map `UV_Mistral58_Smart`. `screenshots/02_seam.png` menampilkan seam; `screenshots/03_uv.png` menampilkan UV island final.
4. Tunjukkan `screenshots/04_checker.png` untuk menjelaskan pemeriksaan distribusi UV. Tekstur final casing memakai enam peta buatan sendiri.
5. Buka **Shader Editor** pada casing: base color memakai sRGB, peta data memakai Non-Color, dan normal masuk ke node Normal Map. Tunjukkan juga enam peta PBR pada material lampu eksternal.
6. Tunjukkan kamera, area light, serta `screenshots/05_nodes.png`. Tekan **F12** untuk render; tekan **F11** untuk melihat hasilnya.

Urutan presentasi yang mudah diikuti: **model radio → seam dan UV → tekstur PBR buatan sendiri → lampu PBR eksternal → lighting dan kamera → hasil render**.

## Bukti proses

- `screenshots/01_model.png` — bentuk radio dan lampu sebelum tekstur PBR casing.
- `screenshots/02_seam.png` — seam UV.
- `screenshots/03_uv.png` — UV layout setelah island dikemas.
- `screenshots/04_checker.png` — uji checker.
- `screenshots/05_nodes.png` — alur peta PBR ke Principled BSDF.
- `screenshots/06_final.png` — render akhir.

## Refleksi

Tantangan utamanya adalah menata detail kecil radio tanpa membuat bagian depannya terlalu ramai. Speaker grille, dial, knob, dan trim dibuat terpisah supaya fungsi serta material tiap bagian mudah dikenali. Saya menandai seam pada sudut tajam casing, kemudian memeriksa UV dengan checker sebelum menghubungkan peta tekstur. Perbedaan roughness dan metallic memberi permukaan casing, kuningan, dan logam tampilan yang berbeda. Lampu eksternal menjadi pembanding untuk material PBR dengan peta lengkap. Pencahayaan dan kamera membantu menunjukkan bentuk, bayangan, dan kedalaman scene.
