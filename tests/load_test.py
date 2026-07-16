import asyncio
import httpx
import time
import random

# Kendi sanal makinenizin dış IP adresini ve portunu yazın
BASE_URL = "http://<IP-Adresi>/redis"

async def send_single_request(client, task_id):
    """Sunucuya rastgele bir SET ve ardından GET isteği gönderir."""
    # Rastgele veriler üretiyoruz
    key = f"user_{random.randint(1, 1000)}"
    value = f"score_{random.randint(10, 100)}"
    
    try:
        # 1. SET İsteği
        set_payload = {"key": key, "value": value}
        # httpx ile asenkron post isteği atıyoruz
        set_response = await client.post(f"{BASE_URL}/set", json=set_payload)
        
        # 2. GET İsteği
        get_response = await client.get(f"{BASE_URL}/get/{key}")
        
        # Eğer her iki istek de başarılıysa True dönüyoruz
        if set_response.status_code == 200 and get_response.status_code == 200:
            return True
    except Exception as e:
        print(f"Hata oluştu (Task {task_id}): {e}")
    return False

async def start_load_test(total_requests):
    """Belirtilen sayıdaki isteği eşzamanlı olarak sunucuya gönderir."""
    print(f"Yük testi başlıyor: {total_requests} adet eşzamanlı istek gönderilecek...")
    start_time = time.time()
    
    # Tek bir asenkron istemci oturumu açıyoruz (performans için önemlidir)
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Görev listemizi oluşturuyoruz
        tasks = [send_single_request(client, i) for i in range(total_requests)]
        
        # Tüm görevleri aynı anda (eşzamanlı) başlatıyoruz
        results = await asyncio.gather(*tasks)
        
    end_time = time.time()
    total_time = end_time - start_time
    
    # Sonuçları analiz ediyoruz
    success_count = sum(1 for r in results if r is True)
    failed_count = total_requests - success_count
    
    print("\n--- TEST SONUÇLARI ---")
    print(f"Toplam Süre: {total_time:.2f} saniye")
    print(f"Başarılı İstek Sayısı: {success_count}")
    print(f"Başarısız İstek Sayısı: {failed_count}")
    print(f"Saniye Başına Düşen İstek (RPS): {total_requests / total_time:.2f}")

# Testi çalıştırıyoruz
if __name__ == "__main__":
    # İlk aşamada 200 eşzamanlı istek ile test edelim
    asyncio.run(start_load_test(1000))