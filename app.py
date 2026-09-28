from flask import Flask, render_template, request, jsonify
import requests
import os
from google import genai
from google.genai import types

app = Flask(__name__)


# ==========================================
# Gemini API
# ==========================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("WARNING: GEMINI_API_KEY is not set.")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=15000
    )
)


# ==========================================
# Home page
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# Currency conversion
# ==========================================

@app.route("/convert", methods=["POST"])
def convert():

    try:
        # ----------------------------------
        # 1. Get data from browser
        # ----------------------------------

        data = request.get_json()

        amount = float(data["amount"])
        from_currency = data["from_currency"]
        to_currency = data["to_currency"]

        # ----------------------------------
        # 2. Validate amount
        # ----------------------------------

        if amount <= 0:
            return jsonify({
                "error": "Amount must be greater than 0."
            }), 400

        # ----------------------------------
        # 3. Get exchange rate
        # ----------------------------------

        url = f"https://open.er-api.com/v6/latest/{from_currency}"

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        exchange_data = response.json()

        if exchange_data.get("result") != "success":
            return jsonify({
                "error": "Could not get exchange rate."
            }), 500

        rates = exchange_data.get("rates", {})

        if to_currency not in rates:
            return jsonify({
                "error": "Currency is not supported."
            }), 400

        # ----------------------------------
        # 4. Calculate conversion
        # ----------------------------------

        rate = rates[to_currency]

        converted_amount = amount * rate

        # ----------------------------------
        # 5. Prepare AI prompt
        # ----------------------------------

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

Give a very short and clear explanation.
Mention that the result is approximate.
Do not create or change the exchange rate.
Use only the provided calculation.
"""

        # ----------------------------------
        # 6. Ask Gemini for AI explanation
        # ----------------------------------

        try:

            ai_response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=100
                )
            )

            ai_text = ai_response.text

            if not ai_text:
                ai_text = (
                    "The conversion was calculated successfully, "
                    "but no AI explanation was returned."
                )

        except Exception as ai_error:

            print("Gemini API error:", ai_error)

            ai_text = (
                "The AI service is temporarily unavailable. "
                "The currency conversion is still calculated "
                "using the current exchange rate."
            )

        # ----------------------------------
        # 7. Return result to browser
        # ----------------------------------

        return jsonify({
            "success": True,
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "converted_amount": converted_amount,
            "ai_message": ai_text
        })

    except requests.exceptions.RequestException as e:

        print("Exchange rate API error:", e)

        return jsonify({
            "error": "Could not connect to the exchange rate service."
        }), 500

    except ValueError:

        return jsonify({
            "error": "Please enter a valid amount."
        }), 400

    except Exception as e:

        print("Server error:", e)

        return jsonify({
            "error": "An unexpected server error occurred."
        }), 500


# ==========================================
# Run Flask
# ==========================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )