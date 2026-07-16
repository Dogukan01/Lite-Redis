# Lite-Redis 🚀

Lite-Redis, Redis'in temel veri yapısı işlevlerini ve davranışlarını taklit eden, Python ve FastAPI ile geliştirilmiş, bellek içi (in-memory) hafif bir anahtar-değer (key-value) veri deposudur.

Proje, HTTP REST API'leri aracılığıyla veri saklama, sorgulama ve silme işlemlerini gerçekleştirmeyi sağlar. Ayrıca **Docker** ile kolayca konteynerize edilebilir ve asenkron yük testleri ile performans analizleri yapılabilir.

---

## 🛠️ Özellikler

Lite-Redis aşağıdaki temel Redis veri tiplerini ve komutlarını destekler:

1. **String Veri Tipi**
   - `SET`: Bir anahtara string değer atar.
   - `GET`: Bir anahtarın değerini döndürür.
   - `INCR`: Sayısal değerli bir anahtarın değerini 1 artırır (tür dönüşümünü otomatik yönetir).
2. **Hash (Sözlük) Veri Tipi**
   - `HSET`: Bir anahtara ait hash yapısında alan-değer ikilisi oluşturur veya günceller.
   - `HGET`: Belirli bir hash alanının değerini getirir.
   - `HGETALL`: Hash yapısındaki tüm alan ve değerleri döndürür.
   - `HDEL`: Belirli bir hash alanını siler.
3. **Sorted Set (Sıralı Küme) Veri Tipi**
   - `ZADD`: Sıralı kümeye (Sorted Set) belirtilen skor (score) ile üye (member) ekler.
   - `ZSCORE`: Üyenin kümedeki skorunu döndürür.
   - `ZREM`: Belirtilen üyeyi sıralı kümeden siler.
   - `ZRANGE`: Üyeleri skorlarına göre (skorlar eşitse isme göre alfabetik) sıralayarak belirli bir aralıkta listeler.
4. **Hata Yönetimi ve Tip Güvenliği**
   - Gerçek Redis'te olduğu gibi bir anahtarın üzerinde ait olmadığı bir veri tipi işlemi yapılmak istendiğinde `HATA (WRONGTYPE)` fırlatır (HTTP 400 Bad Request).
5. **FastAPI Entegrasyonu**
   - Tüm işlemleri REST API üzerinden yönetmek için tasarlanmıştır. `root_path="/redis"` yapılandırması sayesinde ters proxy (Nginx vb.) arkasında çalışmaya hazırdır.

---

## 📁 Proje Yapısı

```text
Lite-Redis/
├── core/
│   ├── database.py       # Ana veri tabanı mantığı ve veri tipi orkestrasyonu (RedisDB sınıfı)
│   └── datatypes.py      # Özel Redis veri tipleri (RedisString, RedisHash, RedisSortedSet)
├── tests/
│   ├── test_redis.py     # pytest ve TestClient kullanılarak yazılmış fonksiyonel testler
│   └── load_test.py      # asyncio ve httpx kullanan asenkron performans/yük testi scripti
├── Dockerfile            # Uygulamanın Dockerize edilmesi için yapılandırma
├── main.py               # FastAPI uygulama tanımları ve API endpoint'leri
├── requirements.txt      # Gerekli bağımlılıklar listesi
└── README.md             # Proje dokümantasyonu (Bu dosya)
```

---

## 🚀 Başlangıç

### Gereksinimler

- Python 3.10 veya üzeri
- pip (Python paket yöneticisi)
- Docker (İsteğe bağlı, konteyner çalıştırmak için)

### 1. Yerel Kurulum (Local Setup)

Projeyi bilgisayarınıza klonlayın veya indirin. Ardından proje ana dizininde aşağıdaki adımları takip edin:

```bash
# Sanal ortam oluşturun (Önerilen)
python -m venv venv

# Sanal ortamı aktifleştirin
# Windows için:
venv\Scripts\activate
# macOS/Linux için:
source venv/bin/activate

# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt
```

### 2. Uygulamayı Çalıştırma

Geliştirme sunucusunu başlatmak için aşağıdaki komutu çalıştırın:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Uygulama varsayılan olarak `http://localhost:8000/redis` adresinde çalışacaktır. API belgelerine erişmek için tarayıcınızdan şu adresleri ziyaret edebilirsiniz:

- **Swagger UI:** `http://localhost:8000/redis/docs`
- **ReDoc:** `http://localhost:8000/redis/redoc`

---

## 🐳 Docker ile Çalıştırma

Projede yer alan `Dockerfile` kullanılarak uygulama kolayca Docker konteynerında ayağa kaldırılabilir.

### İmajı Derleme (Build)

```bash
docker build -t lite-redis .
```

### Konteyneri Çalıştırma (Run)

Konteyneri yerel bilgisayarınızın `8000` portuna bağlayarak arka planda (detached) çalıştırın:

```bash
docker run -d -p 8000:8000 --name lite-redis-container lite-redis
```

Uygulamanın Docker üzerinde düzgün çalıştığını doğrulamak için `http://localhost:8000/redis/docs` adresine gidebilirsiniz.

---

## 📡 API Uç Noktaları (Endpoints)

Tüm endpoint'ler `/redis` ön eki ile başlar. Aşağıda desteklenen API endpoint'lerinin listesi ve örnek istek şablonları bulunmaktadır:

### 1. String Endpoint'leri

- **Anahtar-Değer Ekleme (`SET`)**
  - **Metot:** `POST /redis/set`
  - **Gövde (JSON):**

    ```json
    {
      "key": "name",
      "value": "Dogukan"
    }
    ```

- **Değer Okuma (`GET`)**
  - **Metot:** `GET /redis/get/{key}`
  - **Örnek:** `GET /redis/get/name`
- **Değeri Artırma (`INCR`)**
  - **Metot:** `POST /redis/incr/{key}`
  - **Örnek:** `POST /redis/incr/counter`

### 2. Hash Endpoint'leri

- **Hash Alanı Ekleme (`HSET`)**
  - **Metot:** `POST /redis/hset`
  - **Gövde (JSON):**

    ```json
    {
      "key": "user:100",
      "field": "email",
      "value": "info@example.com"
    }
    ```

- **Hash Alanı Getirme (`HGET`)**
  - **Metot:** `GET /redis/hget/{key}/{field}`
  - **Örnek:** `GET /redis/hget/user:100/email`
- **Tüm Hash İçeriğini Getirme (`HGETALL`)**
  - **Metot:** `GET /redis/hgetall/{key}`
  - **Örnek:** `GET /redis/hgetall/user:100`
- **Hash Alanı Silme (`HDEL`)**
  - **Metot:** `DELETE /redis/hdel/{key}/{field}`
  - **Örnek:** `DELETE /redis/hdel/user:100/email`

### 3. Sorted Set Endpoint'leri

- **Küme Elemanı Ekleme (`ZADD`)**
  - **Metot:** `POST /redis/zadd`
  - **Gövde (JSON):**

    ```json
    {
      "key": "leaderboard",
      "score": 1500.5,
      "member": "player_1"
    }
    ```

- **Skor Sorgulama (`ZSCORE`)**
  - **Metot:** `GET /redis/zscore/{key}/{member}`
  - **Örnek:** `GET /redis/zscore/leaderboard/player_1`
- **Eleman Silme (`ZREM`)**
  - **Metot:** `DELETE /redis/zrem/{key}/{member}`
  - **Örnek:** `DELETE /redis/zrem/leaderboard/player_1`
- **Elemanları Sıralı Getirme (`ZRANGE`)**
  - **Metot:** `GET /redis/zrange/{key}?start=0&stop=-1`
  - **Örnek:** `GET /redis/zrange/leaderboard?start=0&stop=-1`

---

## 🧪 Testler

### Fonksiyonel Unit Testler

Projede tüm veri yapısı davranışlarını ve uç durum hata kontrollerini doğrulamak için `pytest` test paketi mevcuttur. Testleri çalıştırmak için:

```bash
pytest
```

### Asenkron Yük Testi (Load Testing)

`tests/load_test.py` scripti, uygulamanın yüksek eşzamanlı istekler altında nasıl tepki verdiğini ölçer. `httpx` ve `asyncio` kullanarak asenkron olarak binlerce isteği çok kısa sürede gönderir.

**Yük Testini Çalıştırmadan Önce:**

- `tests/load_test.py` dosyasındaki `BASE_URL` değişkeninin test etmek istediğiniz sunucu adresine (örneğin yerel geliştirme için `http://localhost:8000/redis`) yönlendirildiğinden emin olun.
- Ardından scripti çalıştırın:

```bash
python tests/load_test.py
```

Test bittiğinde aşağıdaki gibi bir özet rapor alırsınız:

```text
--- TEST SONUÇLARI ---
Toplam Süre: 2.15 saniye
Başarılı İstek Sayısı: 1000
Başarısız İstek Sayısı: 0
Saniye Başına Düşen İstek (RPS): 465.12
```

---

## 🔮 Gelecek Planları ve İyileştirmeler

- 💾 **Kalıcılık (Persistence):** RDB (snapshotting) veya AOF (Append-Only File) benzeri disk kaydetme mekanizmalarının eklenmesi.
- ⏳ **TTL & Expire:** Anahtarlara belirli bir ömür (Time-To-Live) atayabilme ve süresi dolan anahtarların otomatik silinmesi.
- 🔐 **Yetkilendirme:** API uç noktalarına erişimi korumak için token tabanlı basit bir kimlik doğrulama katmanı.
