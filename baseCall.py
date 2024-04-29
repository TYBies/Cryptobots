from coinbase import jwt_generator
import http.client
import json

api_key = "organizations/405bb81c-6b52-4ccd-b163-74c5d576336a/apiKeys/fa6dd76a-2998-4803-984c-7b22fe4c8a06"
api_secret = "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIOXH+suZw2KkU2W41tghkgT7pZPfyf0+wLx/VnGltwLvoAoGCCqGSM49\nAwEHoUQDQgAECI6tMgO/nolOA9Sco4uaOVPhHO1NW+gpcixcMsgDqqtlOiGOF5/R\nc7krmgeQBFlm8JIcKjkp8xDknIlUTgWzjw==\n-----END EC PRIVATE KEY-----\n"

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
