from coinbase import jwt_generator
import http.client

api_key = ""
api_secret = ""

def main():
    jwt_token = jwt_generator.build_ws_jwt(api_key, api_secret)
    print(f"export JWT={jwt_token}")



conn = http.client.HTTPSConnection("api.coinbase.com")
payload = ''
headers = {
  'Content-Type': 'application/json'
}
conn.request("GET", "/api/v3/brokerage/accounts", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

if __name__ == "__main__":
    main()
