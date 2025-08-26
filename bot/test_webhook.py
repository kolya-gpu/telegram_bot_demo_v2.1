#!/usr/bin/env python3
"""
Тестовый скрипт для проверки webhook endpoints
"""

import asyncio
import aiohttp
import json

async def test_webhook_endpoints():
    """Тестирует все webhook endpoints"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Тестируем webhook endpoints...")
        
        # Тест 1: Корневой endpoint
        print("\n1️⃣ Тестируем корневой endpoint (/)")
        try:
            async with session.get(f"{base_url}/") as response:
                print(f"   Статус: {response.status}")
                text = await response.text()
                print(f"   Ответ: {text}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Тест 2: Health endpoint
        print("\n2️⃣ Тестируем health endpoint (/health)")
        try:
            async with session.get(f"{base_url}/health") as response:
                print(f"   Статус: {response.status}")
                data = await response.json()
                print(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Тест 3: Webhook endpoint (GET)
        print("\n3️⃣ Тестируем webhook endpoint GET (/webhook)")
        try:
            async with session.get(f"{base_url}/webhook") as response:
                print(f"   Статус: {response.status}")
                if response.status == 405:
                    print(f"   ✅ Ожидаемый ответ: Method Not Allowed (GET не поддерживается)")
                else:
                    text = await response.text()
                    print(f"   Ответ: {text}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Тест 4: Webhook endpoint (POST)
        print("\n4️⃣ Тестируем webhook endpoint POST (/webhook)")
        test_data = {
            "test": "data",
            "message": "Это тестовый webhook запрос",
            "timestamp": "2025-01-27T12:00:00Z"
        }
        
        try:
            async with session.post(
                f"{base_url}/webhook",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"   Статус: {response.status}")
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    except:
                        text = await response.text()
                        print(f"   Ответ: {text}")
                else:
                    print(f"   Ответ: {response.status} - {response.reason}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Тест 5: Webhook endpoint (PUT)
        print("\n5️⃣ Тестируем webhook endpoint PUT (/webhook)")
        try:
            async with session.put(f"{base_url}/webhook") as response:
                print(f"   Статус: {response.status}")
                if response.status == 405:
                    print(f"   ✅ Ожидаемый ответ: Method Not Allowed (PUT не поддерживается)")
                else:
                    text = await response.text()
                    print(f"   Ответ: {text}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print("\n✅ Тестирование завершено!")
        print("\n📝 Ожидаемые результаты:")
        print("   - /: 200 OK")
        print("   - /health: 200 OK с JSON")
        print("   - /webhook GET: 405 Method Not Allowed")
        print("   - /webhook POST: 200 OK (если это Telegram webhook)")
        print("   - /webhook PUT: 405 Method Not Allowed")

if __name__ == "__main__":
    print("🚀 Запуск тестирования webhook endpoints...")
    print("⚠️  Убедитесь, что бот запущен на localhost:8000")
    print("=" * 50)
    
    asyncio.run(test_webhook_endpoints())
