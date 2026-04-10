# NDAMaps SDK for Python

Official Python SDK for NDAMaps — Vietnam's national digital map platform API.

No external dependencies except `httpx`. Fully typed.

## Usage

```python
from ndamaps import NDAMapsClient

client = NDAMapsClient(api_key="YOUR_API_KEY")

results = client.places.autocomplete(input="Hồ Hoàn Kiếm")
print(results)
```
