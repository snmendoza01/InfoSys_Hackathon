from pyinspirehep.client import Client

client = Client()

# Fetch up to 50 most‐relevant hits for papers mentioning "holography" by Witten:
resp = client.get_data(q="author:Witten AND title:holography", size=50)

print(f"Total matches: {resp['hits']['total']['value']}")
for hit in resp['hits']['hits']:
    title = hit['metadata']['titles'][0]['title']
    print(" •", title)