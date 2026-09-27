const amountInput = document.getElementById("amount");

amountInput.addEventListener("input", function () {
    let value = this.value.replace(/,/g, "");

    if (value === "") {
        this.value = "";
        return;
    }

    // Chỉ cho phép nhập số
    value = value.replace(/\D/g, "");

    // Thêm dấu phẩy mỗi 3 chữ số
    this.value = Number(value).toLocaleString("en-US");
});

async function convertCurrency() {

    const amount =
        document.getElementById("amount").value.replace(/,/g, "");

    const fromCurrency =
        document.getElementById("from_currency").value;

    const toCurrency =
        document.getElementById("to_currency").value;

    const result =
        document.getElementById("result");


    if (!amount || amount <= 0) {

        result.innerHTML =
            "Please enter a valid amount.";

        return;
    }


    result.innerHTML =
        "🤖 AI is processing your conversion...";


    try {

        const response = await fetch("/convert", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                amount: amount,

                from_currency: fromCurrency,

                to_currency: toCurrency

            })

        });


        const data = await response.json();


        if (!response.ok) {

            result.innerHTML =
                "Error: " + data.error;

            return;
        }


        result.innerHTML = `

            <div class="conversion">

                <h3>
                    ${Number(data.amount).toLocaleString()}
                    ${data.from_currency}

                    ≈

                    ${Number(data.converted_amount)
                        .toLocaleString(
                            undefined,
                            {
                                maximumFractionDigits: 2
                            }
                        )}
                    ${data.to_currency}
                </h3>

                <p>
                    <strong>Exchange rate:</strong><br>
                    1 ${data.from_currency}
                    =
                    ${data.rate}
                    ${data.to_currency}
                </p>

                <hr>

                <p>
                    <strong>AI:</strong><br>
                    ${data.ai_message.replace(/\n/g, "<br>")}
                </p>

            </div>

        `;

    }

    catch (error) {

        result.innerHTML =
            "Could not connect to the server.";

        console.error(error);

    }

}