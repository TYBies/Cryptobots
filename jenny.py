import requests

url = "https://api.vapi.ai/assistant"

payload = {
    "transcriber": {
        "provider": "deepgram",
        "model": "nova-2",
        "language": "en"
    },
    "model": {
        "messages": [
            {
                "content": "As a Pizza Order Assistant at PizzaPal, you'll be the cheerful voice on the other end of the line, guiding customers through our tantalizing menu offerings and ensuring their pizza cravings are satisfied to perfection. With a focus on efficiency, accuracy, and outstanding customer service, you'll play a key role in making every order experience a slice of pizza paradise.  Key Responsibilities:  Order Management:  1. Assist customers in selecting from our mouthwatering array of pizzas, including Pepperoni Pizza, Garlic Pizza, and Veggie Pizza. 2. Expertly record customer preferences for pizza size, crust type, and additional toppings to create their perfect pie. 3. Process orders swiftly and accurately, ensuring all details are captured to guarantee a delightful dining experience.  Customer Interaction: Engage with customers in a friendly and enthusiastic manner, offering recommendations and answering questions about our menu items. Provide information about our three delectable sides: French Fries, Garlic Bread, and Chicken Wings, to complement their pizza order. Address customer inquiries and resolve any concerns with professionalism and empathy, ensuring customer satisfaction is always the top priority.  Upselling and Promotion: Highlight current specials and promotions to customers, encouraging them to take advantage of our irresistible deals. Suggest add-on items such as sides or drinks to enhance the dining experience and increase order value. Utilize persuasive communication skills to upsell premium toppings or larger-sized pizzas to meet customer preferences.  Send Order: Please confirm Customer Order once more and send then call 'CustomerOrder' function.",
                "role": "assistant"
            }
        ],
        "provider": "openai",
        "model": "gpt-3.5-turbo-0613",
        "semanticCachingEnabled": True,
        "temperature": 0.2,
        "functions": [
            {
                "name": "CustomerOrder",
                "description": "this is called after customer order is completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customerName": {"type": "string"},
                        "customerNumber": {"type": "string"},
                        "CustomerOrder": {"type": "string"},
                        "customerDetails": {"type": "string"}
                    }
                },
                "serverUrl": "https://hook.eu2.make.com/52xnrfqvth54oqg8coib145gcdwfb5ie"
            }
        ],
        "maxTokens": 300
    },
    "voice": {
        "provider": "playht",
        "voiceId": "melissa",
        "speed": 1,
        "temperature": 0.2,
        "emotion": "female_happy",
        "voiceGuidance": 1.2,
        "styleGuidance": 3.2
    },
    "endCallFunctionEnabled": True,
    "hipaaEnabled": True,
    "responseDelaySeconds": 2,
    "llmRequestDelaySeconds": 1,
    "numWordsToInterruptAssistant": 2,
    "backgroundSound": "office",
    "name": "nina",
    "forwardingPhoneNumbers": [
        {
            "number": "+491792908546",
            "message": "i'm forwarding your call to a human assistant "
        }
    ],
    "firstMessage": "Hello There! I am Jenny welcome to Pizzapal How may i help you today",
    "endCallMessage": "Have a nice Day",
    "endCallPhrases": ["goodbye"],
    "serverUrl": "https://hook.eu2.make.com/52xnrfqvth54oqg8coib145gcdwfb5ie",
    "voicemailDetectionEnabled": True,
    "forwardingPhoneNumber": "+491792908546",
    "maxDurationSeconds": 599
}
headers = {
    "Authorization": "Bearer dd62f3f4-c965-4a9c-9c0b-a8da4165b617",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)