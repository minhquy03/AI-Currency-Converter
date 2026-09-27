from flask import Flask, render_template, request, jsonify
import requests
import os
from google import genai

app = Flask(__name__)

# Gemini API
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():

    try:
        data = request.get_json()

        amount = float(data["amount"])
        from_currency = data["from_currency"]
        to_currency = data["to_currency"]

        if amount <= 0:
            return jsonify({
                "error": "Amount must be greater than 0."
            }), 400

        # Get exchange rate
        url = f"https://open.er-api.com/v6/latest/{from_currency}"

        response = requests.get(url, timeout=10)
        exchange_data = response.json()

        if exchange_data.get("result") != "success":
            return jsonify({
                "error": "Could not get exchange rate."
            }), 500

        rates = exchange_data["rates"]

        if to_currency not in rates:
            return jsonify({
                "error": "Currency is not supported."
            }), 400

        rate = rates[to_currency]

        converted_amount = amount * rate


        # Send result to Gemini
        prompt = f"""
You are an AI Currency Converter assistant.

The user wants to convert:

Amount: {amount}
From: {from_currency}
To: {to_currency}

Current exchange rate:
1 {from_currency} = {rate} {to_currency}

Calculated result:
{converted_amount} {to_currency}

Give a short and clear answer.
Mention that the result is approximate.
Do not invent another exchange rate.
"""

        ai_response = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt
        )

        ai_text = ai_response.output_text


        return jsonify({
            "success": True,
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "converted_amount": converted_amount,
            "ai_message": ai_text
        })


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )