var paymentForm = document.getElementById("paymentForm");
paymentForm.addEventListener("submit", payWithPaystack, false);
function payWithPaystack() {
  var handler = PaystackPop.setup({
    key: "pk_test_de78e21b337d08ee9cc2313099b0ae7d274219a8",
    email: "tochukwucollinsonu@gmail.com",
    amount: 200 * 100,
    currency: "NGN",
    callback: function (response) {
      var reference = response.reference;
      paystackCallback(reference);
    },
    onClose: function () {
      alert("Transaction was not completed, window closed.");
    },
  });
  handler.openIframe();
}

async function paystackCallback(reference) {
  const res = await fetch(
    `${window.location.origin}/paystack-payment-callback/${reference}`
  );
  const data = await res.json();

  if (data.status) {
    alert("Payment successful");
  } else {
    alert("Payment failed");
  }
}
