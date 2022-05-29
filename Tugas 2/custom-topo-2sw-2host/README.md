<div align="center">
    <h1>Custom Topology: 2 Switches and 2 Hosts</h1>
    <i>Tugas 2 - Tugas Akhir Mata Kuliah Arsitektur Jaringan Terkini</i>
</div>

## Langkah 1
Silahkan membuat direktori baru bernama TugasAkhir. Lalu, di dalam direktori TugasAkhir buatlah direktori lagi bernama CustomTopologyMininet.

```bash
mkdir TugasAkhir
cd TugasAkhir
mkdir CustomTopologyMininet
```

Setelah itu, buatlah program baru bernama `custom-topo-2sw-2host.py`. Caranya adalah menggunakan Neovim. Masukkan perintah berikut ke terminal:

```bash
nvim custom-topo-2sw-2host.py
```

Lalu, tampilan terminal akan berubah menjadi seperti gambar berikut:
<img src="https://daptong.files.wordpress.com/2022/05/nvim1.png"><br>

Setelah itu, klik tombol <b>I</b> di keyboard untuk mengisi code untuk `custom-topo-2sw-2host.py`. Isi code dengan code dibawah ini:

```python
from mininet.topo import Topo
from mininet.log import setLogLevel, info

class MyTopo(Topo):
    def addSwitch(self, name, **opts):
        kwargs = {'protocols': 'OpenFlow13'}
        kwargs.update(opts)
        return super(MyTopo, self).addSwitch(name, **kwargs)
    
    def __init__(self):
        # Inisialisasi Topology
        Topo.__init__(self)

        # Tambahkan node, switch, dan host
        info('*** Add switches\n')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        info('*** Add hosts\n')
        h1 = self.addHost('h1', ip = '10.1.0.1/24')
        h2 = self.addHost('h2', ip = '10.1.0.2/24')

        info('*** Add links\n')
        self.addLink(s1, h1, port1 = 1, port2 = 1)
        self.addLink(s1, s2, port1 = 2, port2 = 1)
        self.addLink(s2, h2, port1 = 2, port2 = 1)

topos = {'mytopo': (lambda: MyTopo())}
```

Setelah mengisi code diatas, maka klik tombol <b>ESC</b> di keyboard lalu ketik <b>:wq</b> untuk menyimpan file `custom-topo-2sw-2host.py`

--------------------------------------------------------------------------------

## Langkah 2

Langkah kedua adalah menjalankan program `custom-topo-2sw-2host.py` dengan Mininet. Jalankan perintah dibawah ini untuk menjalankan Mininet tanpa menggunakan <i>controller</i> dan menggunakan custom topo yang sudah dibuat.

```bash
sudo mn --controller=none --custom custom-topo-2sw-2host.py --topo mytopo --mac --arp
```

Setelah perintah tersebut dijalankan, maka tampilan akan berubah seperti gamabr dibawah ini:
<img src="https://daptong.files.wordpress.com/2022/05/t2_sudomn1.png"><br>

Setelah itu, jalankan perintah dibawah ini untuk menambahkan <i>flows</i> agar Host 1 dapat terhubung dengan Host2:

```
mininet> sh ovs-ofctl add-flow s1 -O OpenFlow13 "in_port=1,action=output:2"
mininet> sh ovs-ofct1 add-flow s1 -O OpenFlow13 "in_port=2,action=output:1"
mininet> sh ovs-ofctl add-flow s2 -O OpenFlow13 "in_port=1,action=output:2"
mininet> sh ovs-ofctl add-flow s2 -O OpenFlow13 "in_port=2,action=output:1"
```
<img src="https://daptong.files.wordpress.com/2022/05/t2_sudomn2.png"><br>

Lalu kita coba untuk uji koneksi antara Host 1 dengan Host 2 dengan perintah berikut:

```
mininet> h1 ping -c 2 h2
```
<img src="https://daptong.files.wordpress.com/2022/05/t2_sudomn3.png"><br>
Pada gambar diatas, dapat dilihat di statistiknya, uji koneksi antara Host 1 dengan Host 2 berhasil.

--------------------------------------------------------------------------------

## Langkah 3
Jika ingin melihat gambar topology dari custom topology diatas, maka kita bisa gunakan Mininet + Ryu. Caranya adalah kita menggunakan <b>tmux</b> agar kita memiliki dua terminal dalam 1 layar. Gunakan perintah `tmux` untuk mulai menggunakan tmux. Lalu ketik di keyboard <b>`CTRL+B %`</b> untuk men-<i>split</i> terminal secara vertikal. Tampilan terminal akan seperti gambar berikut: 
<img src="https://daptong.files.wordpress.com/2022/05/t2_tmux1-1.png"><br>

Untuk berpindah antar terminal, kita bisa gunakan key <b>`CRTL+B O`</b>.<br>

Pada terminal 1, gunakan perintah dibawah ini untuk menjalankan `custom-topo-2sw-2host` pada Mininet:

> Pastikan Anda sudah masuk ke direktori ``TugasAkhir/CustomTopologyMininet``

```
sudo mn --controller=remote -custom custom-topo-2sw-2host.py --topo mytopo --mac --arp
```
Pada terminal 2, gunakan perintah ini untuk menjalankan web-server untuk melihat topology jaringan pada source code `custom-topo-2sw-host`.:

```
ryu-manager --observe-links ~/flowmanager/flowmanager.py ryu.app.simple_switch_13
```

> <b>Jalankan terminal kedua terlebih dahulu</b>

Setelah menjalankan kedua perintah tersebut, maka tampilan akan berubah seperti gambar berikut:
<img src="https://daptong.files.wordpress.com/2022/05/t2_tmux2-1.png"><br>

Untuk melihat visualisasi topology-nya, silahkan pergi ke website EC2 Instance Details dan cari <b>Public IPv4 Address</b>. <b>Public IPv4 Address</b> akan seperti gambar berikut:<br>
<img src="https://daptong.files.wordpress.com/2022/05/t2_ipv4-1.png"><br>

Salin alamat IPv4 tersebut, lalu buka tab baru di Browser. Lalu tambahkan port 8080 dan link pada IPv4 tersebut:

```
(Public IPv4 Address):8080/home/topology.html
```

Setelah itu, Browser akan memuat tampilan dari topology. Gambar topology dari `custom-topo-2sw-2host` akan seperti gambar berikut:
<img src="https://daptong.files.wordpress.com/2022/05/t2_topo1.png"><br>
