<div align="center">
    <h1>Tugas 1 - Pembuatan EC2 Instance di AWS Academy</h1>
    <i>Tugas Akhir Mata Kuliah Arsitektur Jaringan Terkini</i>
</div>

# Table of Contents
- [Getting Started](#getting-started)
    - [Name and Tags](#name-and-tags)
    - [OS Images](#os-images)
    - [Instance Type and Key Pair](#instance-type-and-key-pair)
    - [Edit Network Settings](#edit-network-settings)
    - [Configure Storage](#configure-storage)
    - [Launch Instance](#launch-instance)
- [Connect to EC2 Instance](#connect-to-ec2-instance)
    - [Mininet + OpenFlow Installation](#mininet--openflow-installation)
    - [Flowmanager Installation](#flowmanager-installation)
    - [Ryu Installation](#ryu-installation)
- [Verify](#verify)
- [Ready to Go](#ready-to-go)

## Getting Started
Untuk membuat EC2 Instance baru di AWS Academy, maka bukalah console Amazon EC2 di <a href="https://console.aws.amazon.com/ec2/">sini</a>, lalu klik <b>Launch Instance</b>. <br>Setelah itu, maka ikuti langkah-langkah berikut:

### Name and Tags
<img src="https://media1.giphy.com/media/JihEZvKylB1JX1Zoqr/giphy.gif"><br>
Masukan dengan nama <b>Tugas Akhir</b>.

### OS Images
<img src="https://media2.giphy.com/media/UUOacW2eOIn8BjVZ9X/giphy.gif"><br>
Setelah memasukkan nama, silahkan pilih OS Images, yaitu <b>Ubuntu Server 22.04 LTS</b> dengan arsitektur <b>64-bit (x86)</b>.

### Instance Type and Key Pair
<img src="https://media3.giphy.com/media/3o5yfFAYnUtiuZer8C/giphy.gif"><br>
Untuk instance type, silahkan pilih <b>t2.medium</b> dan untuk key pair silahkan pilih <b>vockey</b>.

### Edit Network Settings
<img src="https://media2.giphy.com/media/plMbO6cGbJJQlAbAgw/giphy.gif"><br>
Pada bagian ini, silahkan klik checkbox untuk <b>Allow SSH, allow HTTP dan HTTPS</b>. Setelah itu, maka kita menambahkan dua group role dengan protokol TCP dengan cara mengklik tombol <b>Edit</b>. <br>- Untuk group role pertama akan diisi dengan <b>port 8080</b> dengan source type <b>anywhere</b>. <br>- Dan untuk group role kedua akan diisi dengan <b>port 8081</b> dengan source typenya yaitu <b>anywhere</b> juga.

### Configure Storage
<img src="https://media1.giphy.com/media/jiLqn2cmrsxwAHnVAd/giphy.gif"><br>
Dan pada bagian terakhir, yaitu Configure Storage, silahkan isi storagenya dengan nilai <b>30GB</b> dengan root volumenya yaitu <b>General Purpose SSD (gp3)</b>

###
> Note: Silahkan memverifikasi apakah sudah mengikuti ketentuan yang diberikan.

### Launch Instance
<img src="https://media3.giphy.com/media/mzgXm7LcZi52oh17tJ/giphy.gif"><br>
Jika sudah memverifikasi semua bagian, maka silahkan klik tombol <b>Launch Instance</b> untuk membuat EC2 Instance baru.

--------------------------------------------------------------------------------

## Connect to EC2 Instance

<img src="https://daptong.files.wordpress.com/2022/05/instances-1.png"><br>
Setelah membuat EC2 Instance baru, maka Instance baru tersebut akan keluar di halamanan Instance di AWS Academy. Untuk <i>connect</i> ke EC2 Instance Tugas Akhir, maka klik <b>Instance ID</b> dari Instance Tugas Akhir.<br><br>

<img src="https://daptong.files.wordpress.com/2022/05/publicipv4dns.png"><br>
Setelah itu, tinggal <i>copy</i> saja alamat dari Public IPv4 DNS.<br><br>

<img src="https://media.giphy.com/media/cuKT0CIHDWefI23REt/giphy.gif"><br>
Setelah alamat Public IPv4 DNS ter-<i>copy</i>. Maka, buka halaman Vocareum Labs dan klik <b>Start Lab</b>. Setelah keluar console seperti dibawah ini, maka ketiklah <i>line</i> berikut untuk <i>connect</i> ke Instance dengan cara SSH (tanpa tandak kurung):

```
ssh -i .ssh/labsuser.pem ubuntu@(alamat Public IPv4 DNS dari instance Tugas Akhir)
```

## Mininet + OpenFlow Installation
<img src="https://media1.giphy.com/media/A0NpunoAUarJKckg5q/giphy.gif"><br>
Untuk instalasi Mininet + OpenFlow, silahkan ketik line:

```
git clone https://github.com/mininet/mininet
```

Lalu tunggu hingga <b>git</b> selesai meng-<i>cloning</i>. Setelah itu, maka jalankan perintah berikut untuk meng-<i>install</i> Mininet:

```
mininet/util/install.sh -nfv
```

<img src="https://media2.giphy.com/media/o8YQbUpZ0FEoCNsCxG/giphy.gif"><br>

Setelah itu, biarkan hingga instalasi selesai.

## Flowmanager Installation
<img src="https://media4.giphy.com/media/KGrHtqDVguAomfypnu/giphy.gif"><br>
Langkah selanjutnya adalah meng-<i>install</i> Flowmanager. Silahkan ketik perintah berikut di <i>console</i>:

```
git clone https://github.com/martimy/flowmanager
```

Setelah itu, tunggu hingga <b>git</b> selesai meng-<i>cloning</i>.

## Ryu Installation
<img src="https://media0.giphy.com/media/eDd0EJkJzJYqWHysdc/giphy.gif">
Yang terakhir adalah meng-<i>install</i> Ryu. Gunakan perintah berikut untuk men-<i>download</i> package git Ryu.

```
git clone https://github.com/osrg/ryu.git
```

Setelah meng-<i>cloning</i> Ryu, maka langkah selanjutnya adalah meng-<i>install</i> Ryu dengan cara seperti berikut:

```
cd ryu
pip install .
```

<img src="https://media0.giphy.com/media/B8nBLbaaC8qVoHgwtu/giphy.gif"><br>
Lalu tinggal tunggu saja hingga proses instalasi Ryu selesai.

--------------------------------------------------------------------------------

## Verify
Silahkan verifikasi apakah semua program sudah ter-<i>install</i>, program yang harus di-<i>install</i> adalah <b>Mininet + OpenFlow</b>, <b>Flowmanager</b>, dan <b>Ryu</b>. Silahkan gunakan perintah <b>ls</b> di direktory <b>Home</b> untuk melihat isi dari direktori <b>Home</b>.

```
ls
```

<img src="https://media0.giphy.com/media/0n3OyR0CfE9suD1HB4/giphy.gif">

Direktori yang harus ada adalah <b>flowmanager</b>, <b>mininet</b>, <b>openflow</b>, dan <b>ryu</b>.

--------------------------------------------------------------------------------

## Ready to Go
Jika semuanya sudah mengikuti aturan maupun perintah yang diberikan, maka tinggal menjalankan program-program yang sudah di-<i>install</i> untuk memvisualisasi suatu topology jaringan.
