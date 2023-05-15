total = 0;
prices = document.getElementsByClassName("order_summary_price");
for (var i = 0; i < prices.length; i++) {
    total += parseFloat(prices[i].innerHTML.split(": ")[1]);
}
document.getElementsByClassName("total")[0].value += total.toFixed(2);
document.getElementsByClassName("total")[1].innerHTML += "Total: $ " + total.toFixed(2);