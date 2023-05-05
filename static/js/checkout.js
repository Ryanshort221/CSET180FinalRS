total = 0;
prices = document.getElementsByClassName("order_summary_price");
for (var i = 0; i < prices.length; i++) {
    total += parseFloat(prices[i].innerHTML.split(": ")[1]);
}
document.getElementsByClassName("total")[0].innerHTML += "Total: $ " + total.toFixed(2);

const defaultAddressForm = document.querySelector('.shipping_checkout_form');
const newAddressForm = document.querySelector('.new_address_shipping_form');
const defaultForm = document.querySelector('.shipping_checkout_form');
const newForm = document.querySelector('.new_address_shipping_form');
const showDefaultBtn = document.querySelector('#show_default_shipping');
const showNewBtn = document.querySelector('#show_new_shipping');


showDefaultBtn.addEventListener('click', () => {
    event.preventDefault();
    defaultForm.classList.add('shipping_checkout_form_visible');
    defaultForm.classList.remove('shipping_checkout_form_hidden');
    newForm.classList.add('new_address_shipping_form_hidden');
    newForm.classList.remove('new_address_shipping_form_visible');
});

showNewBtn.addEventListener('click', () => {
    event.preventDefault();
    defaultForm.classList.add('shipping_checkout_form_hidden');
    defaultForm.classList.remove('shipping_checkout_form_visible');
    newForm.classList.add('new_address_shipping_form_visible');
    newForm.classList.remove('new_address_shipping_form_hidden');
});

