# 🤖 Discord Botu

Python ve discord.py ile yazılmış kapsamlı Discord botu.

## ✨ Özellikler

- **🛡️ Moderasyon** — Ban, kick, mute, mesaj temizleme, yasak kaldırma
- **🎵 Müzik** — YouTube'dan müzik çalma, kuyruk, ses kontrolü, tekrar modu
- **🏷️ Rol Yönetimi** — Rol verme/alma, oluşturma, silme, bilgi görüntüleme

---

## 🚀 Kurulum

### 1. Gereksinimler

- Python 3.10+
- ffmpeg (müzik için)

**ffmpeg kurulumu:**
```bash
# Linux/Mac
sudo apt install ffmpeg   # veya brew install ffmpeg

# Windows
# https://ffmpeg.org/download.html adresinden indirin, PATH'e ekleyin
```

### 2. Paketleri kur

```bash
pip install -r requirements.txt
```

### 3. Token al

1. https://discord.com/developers/applications adresine gidin
2. "New Application" → uygulamanıza isim verin
3. Sol menüde "Bot" → "Add Bot"
4. "Reset Token" ile token kopyalayın
5. **Privileged Gateway Intents** altında şunları açın:
   - ✅ Server Members Intent
   - ✅ Message Content Intent

### 4. .env dosyası oluştur

```bash
cp .env.example .env
```

`.env` dosyasını açıp token'ınızı yapıştırın:
```
DISCORD_TOKEN=MTxxxxxxxxxxxxxxxxxxxxxxxx.Gxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Botu sunucuya ekle

Bot için OAuth2 URL oluşturun (Developer Portal → OAuth2 → URL Generator):
- Scopes: `bot`, `applications.commands`
- Permissions: `Administrator` (veya gerekli izinleri tek tek seçin)

### 6. Çalıştır

```bash
python bot.py
```

---

## 📋 Komutlar

### 🛡️ Moderasyon

| Komut | Açıklama | Yetki |
|-------|----------|-------|
| `/ban @üye [sebep]` | Üyeyi yasakla | Ban Members |
| `/kick @üye [sebep]` | Üyeyi at | Kick Members |
| `/mute @üye [dakika] [sebep]` | Üyeyi sustur | Moderate Members |
| `/unmute @üye` | Susturmayı kaldır | Moderate Members |
| `/unban [id]` | Yasağı kaldır | Ban Members |
| `/temizle [adet]` | Mesajları sil (max 100) | Manage Messages |

### 🎵 Müzik

| Komut | Açıklama |
|-------|----------|
| `/cal [şarkı/url]` | Müzik çal |
| `/dur` | Duraklat / Devam et |
| `/gec` | Sonraki şarkıya geç |
| `/kuyruk` | Kuyruğu göster |
| `/ses [1-100]` | Ses seviyesini ayarla |
| `/tekrar` | Tekrar modunu aç/kapat |
| `/cik` | Ses kanalından çık |

### 🏷️ Rol Yönetimi

| Komut | Açıklama | Yetki |
|-------|----------|-------|
| `/rolver @üye @rol` | Üyeye rol ver | Manage Roles |
| `/rolal @üye @rol` | Üyeden rol al | Manage Roles |
| `/rolbilgi @rol` | Rol bilgisi göster | — |
| `/rolekle [isim] [renk]` | Yeni rol oluştur | Manage Roles |
| `/rolsil @rol` | Rolü sil | Manage Roles |
| `/rollerim` | Kendi rollerini gör | — |

---

## 📁 Proje Yapısı

```
discord-bot/
├── bot.py              # Ana dosya
├── requirements.txt    # Bağımlılıklar
├── .env                # Token (paylaşmayın!)
├── .env.example        # Token şablonu
└── cogs/
    ├── moderasyon.py   # Moderasyon komutları
    ├── muzik.py        # Müzik komutları
    └── rol.py          # Rol yönetimi komutları
```

---

## ⚠️ Önemli Notlar

- `.env` dosyasını asla GitHub'a yüklemeyin
- Müzik için `ffmpeg` kurulu olmalı
- Slash komutları ilk çalıştırmada senkronize edilir (1-2 dakika sürebilir)
