"""测试DashScope Embedding API是否可用"""
import os
import requests

# 从环境变量读取配置
api_key = os.getenv("EMBED_API_KEY", "sk-7520138625834635ab4ecdc8aa2ea43e")
base_url = os.getenv("EMBED_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
model_name = os.getenv("EMBED_MODEL_NAME", "text-embedding-v3")

print(f"🔍 测试配置:")
print(f"  API Key: {api_key[:20]}...")
print(f"  Base URL: {base_url}")
print(f"  Model: {model_name}")
print()

# 测试REST API
url = base_url.rstrip("/") + "/embeddings"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
payload = {"model": model_name, "input": ["test"]}

print("🚀 测试API调用...")
try:
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"  Status Code: {resp.status_code}")

    if resp.status_code >= 400:
        print(f"  ❌ API调用失败")
        print(f"  Response: {resp.text}")
    else:
        data = resp.json()
        print(f"  ✅ API调用成功")
        print(f"  Response: {data}")
except Exception as e:
    print(f"  ❌ 连接失败: {e}")
