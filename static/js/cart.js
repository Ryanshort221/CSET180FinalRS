const quantityInputs = document.querySelectorAll('.quantityInputs');
const total = document.querySelector('#cart_total');
const prices = document.querySelectorAll('.cart_price')
updateTotal();
function updateTotal() {
    let totalValue = 0;
    for (let i = 0; i < prices.length; i++) {
        const price = prices[i].innerText.split('$')[1];
        const quantity = quantityInputs[i].value;
        totalValue += price * quantity;
    }
    total.value = totalValue.toFixed(2);
}
quantityInputs.forEach(function(quantityInput) {
    quantityInput.addEventListener('change', updateTotal);
});