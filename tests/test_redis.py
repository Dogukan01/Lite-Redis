from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

def test_string_set_and_get():
    # 1. Adım: "/set" endpoint'ine bir POST isteği atıyoruz.
    # Gönderdiğimiz JSON verisini 'json=' parametresiyle veriyoruz.
    response = client.post("/set", json={"key": "ad", "value": "Dogukan"})
    
    # İddia 1: Sunucunun bize HTTP 200 (Başarılı) koduyla döndüğünü iddia ediyoruz.
    assert response.status_code == 200
    
    # İddia 2: Dönen JSON cevabının {"status": "OK"} olduğunu iddia ediyoruz.
    assert response.json() == {"status": "OK"}

    # 2. Adım: Yazdığımız bu "ad" anahtarını okumak için "/get/ad" endpoint'ine GET isteği atıyoruz.
    get_response = client.get("/get/ad")
    
    # İddia 3: Okuma işleminin de başarılı (200 OK) olduğunu iddia ediyoruz.
    assert get_response.status_code == 200
    
    # İddia 4: Dönen değerin gerçekten "Dogukan" olduğunu iddia ediyoruz.
    assert get_response.json()["value"] == "Dogukan"

def test_hashmap_operations():
    # 1. Adım: "user:1" anahtarına "isim": "Ahmet" alanını ekle
    response1 = client.post("/hset", json={"key": "user:1", "field": "isim", "value": "Ahmet"})
    assert response1.status_code == 200
    assert response1.json() == {"status": 1} # Yeni eklendiği için 1 dönmeli

    # 2. Adım: Aynı anahtara "yas": "25" alanını ekle
    response2 = client.post("/hset", json={"key": "user:1", "field": "yas", "value": "25"})
    assert response2.status_code == 200

    # 3. Adım: Tüm hash içeriğini çekip kontrol et
    get_all_response = client.get("/hgetall/user:1")
    assert get_all_response.status_code == 200
    
    # İddia: Dönen verinin tam olarak bu sözlük olduğunu iddia ediyoruz
    assert get_all_response.json() == {"isim": "Ahmet", "yas": "25"}

def test_wrong_type_error_handling():
    # 1. Adım: "test_key" adında düz bir string oluşturuyoruz
    client.post("/set", json={"key": "test_key", "value": "merhaba"})

    # 2. Adım: String olan bu anahtara gidip hset (Hashmap) işlemi yapmaya çalışıyoruz!
    response = client.post("/hset", json={"key": "test_key", "field": "alan", "value": "deger"})
    
    # İddia 1: Sunucunun bunu reddedip HTTP 400 (Bad Request) dönmesi gerektiğini iddia ediyoruz.
    assert response.status_code == 400
    
    # İddia 2: Dönen hata mesajının içinde bizim database.py'de yazdığımız "WRONGTYPE" ifadesinin geçtiğini iddia ediyoruz.
    assert "WRONGTYPE" in response.json()["detail"]

def test_sorted_set():
    # 1. Adım: İlk üyeyi ekle
    response = client.post("/zadd", json={"key": "test_zset_key", "score": 12, "member": "Ali"})
    assert response.status_code == 200
    assert response.json() == {"status": 1}

    # 2. Adım: ZSCORE ile skoru doğrula
    get_response = client.get("/zscore/test_zset_key/Ali")
    assert get_response.status_code == 200
    assert get_response.json() == {"key": "test_zset_key", "member": "Ali", "score": 12.0}

    # 3. Adım: Sıralamayı test etmek için farklı skorlara sahip yeni üyeler ekle
    client.post("/zadd", json={"key": "test_zset_key", "score": 5.5, "member": "Veli"})
    client.post("/zadd", json={"key": "test_zset_key", "score": 20.0, "member": "Ayse"})

    # 4. Adım: ZRANGE ile sıralı listeyi çek (Küçük skordan büyük skora sıralı olmalı: Veli (5.5) -> Ali (12.0) -> Ayse (20.0))
    range_response = client.get("/zrange/test_zset_key?start=0&stop=-1")
    assert range_response.status_code == 200
    assert range_response.json()["members"] == ["Veli", "Ali", "Ayse"]

    # 5. Adım: ZREM ile bir üyeyi sil
    rem_response = client.delete("/zrem/test_zset_key/Veli")
    assert rem_response.status_code == 200
    assert rem_response.json() == {"status": 1}

    # 6. Adım: Silinen üyenin silindiğini ve listenin güncellendiğini doğrula
    range_response_after = client.get("/zrange/test_zset_key?start=0&stop=-1")
    assert range_response_after.json()["members"] == ["Ali", "Ayse"]

    # 7. Adım: Silinen üyenin skorunu sorgula (None dönmeli)
    score_after = client.get("/zscore/test_zset_key/Veli")
    assert score_after.json()["score"] is None