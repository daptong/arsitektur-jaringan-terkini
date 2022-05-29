<div align="center">
    <h1>Tugas 2 - Custom Topology Mininet</h1>
    <i>Tugas Akhir Mata Kuliah Arsitektur Jaringan Terkini</i>
</div>

# Tugas 2 Contents
- [Custom Topology: 2 Switches and 2 Hosts](https://github.com/daptong/arsitektur-jaringan-terkini/tree/main/Tugas%202/custom-topo-2sw-2host)
- [Custom Topology: 3 Switches and 6 Hosts + Spanning Tree](https://github.com/daptong/arsitektur-jaringan-terkini/tree/main/Tugas%202/custom-topo-3sw-6host)

# Table of Contents
- [Getting Started](#getting-started)
- [Important Notes](#important-notes)
  - [Downgrade Python](#downgrade-python)
  - [Install python3.8-distutils](#install-python38-distutils)
  - [Update module greenlet](#update-module-greenlet)
  - [Downgrade module eventlet](#downgrade-module-eventlet)
  - [Install ulang Mininet](#install-ulang-mininet)

# Getting Started
Sebelum menjalakan program Mininet, maka yang perlu dilakukan adalah meng-<i>install</i> <b>Neovim</b> dan <b>Tmux</b>. Neovim digunakan sebagai <b>Code Editor</b> dan Tmux digunakan untuk <b>Terminal Multiplexer</b>.<br><br>
Gunakan perintah berikut untuk meng-<i>install</i> Neovim.

```bash
sudo apt install neovim
```
<img src="https://daptong.files.wordpress.com/2022/05/neovim.png"><br>

Dan gunakan perintah berikut untuk meng-<i>install</i> Tmux.

```bash
sudo apt-get install tmux
```

<img src="https://daptong.files.wordpress.com/2022/05/tmux.png"><br>

# Important Notes
Karena OS Images yang digunakan pada instance ini adalah <b>Ubuntu 22.04 Server LTS</b> dan <b>Ubuntu 22.04</b> ini menggunakan Python versi 3.10, maka akan ada beberapa program berbasis Python yang tidak <i>compatible</i> dengan Python versi 3.10. Agar program tersebut dapat berjalan, maka kita bisa men-<i>downgrade</i> versi Python kita dari 3.10 ke 3.8.

## Downgrade Python
Jalankan perintah-perintah di bawah ini untuk men-<i>downgrade</i> versi Python dari 3.10 ke 3.8.

- Cek versi Python terlebih dahulu

```bash
python3 --version
```
  Jika versi Python masih 3.10.4, maka ikut langkah-langkah dibawah ini:

- Update APT Packages dan Download Python 3.8

```bash
sudo apt update -y && sudo apt install python3.8
```

- Mengkonfigurasi `update-alternatives` agar dapat mengganti versi Python

```bash
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
```
- Cek konfigurasi `update-alternatives`

```bash
sudo update-alternatives --config python3
```

Setelah menjalankan perintah diatas, maka tampilan akan seperti dibawah ini (tampilan dapat berbeda-beda):

```
There are 2 choices for the alternative python3 (providing /usr/bin/python3).

  Selection    Path                Priority   Status
------------------------------------------------------------
  0            /usr/bin/python3.8   2         auto mode
  1            /usr/bin/python3.10   1         manual mode
* 2            /usr/bin/python3.8   2         manual mode

Press <enter> to keep the current choice[*], or type selection number: 
```

Masukkan angka yang menunjukkan Python3.8, dalam hal ini angkanya adalah 2.

- Cek lagi versi Python

```bash
python3 --version
```

## Install python3.8-distutils
python3.8-distutils ini berguna untuk meng-<i>install</i> module tambahan. Jalankan perintah berikut:

```bash
sudo apt install python3.8-distutils -y
```

## Update module greenlet
Jalankan perintah berikut untuk meng-<i>update</i> module <b>greenlet</b>

```bash
pip install interpret -ignore-installed greenlet
```

## Downgrade module eventlet
Jalankan perintah berikut untuk meng-<i>downgrade</i> module eventlet

```bash
pip install eventlet==0.30.2
```

## Install ulang Mininet
Jalankan perintah berikut untuk meng-<i>install</i> ulang Mininet

```bash
/mininet/util/install.sh -nfv
```
