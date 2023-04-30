const add_form_btn = document.getElementById('add_form_btn');
const add_item_form = document.querySelector('.add_item_form');
const add_close_btn = document.querySelector('#add_close_btn')
add_form_btn.addEventListener('click', () => {
    add_item_form.classList.remove('add_form_hidden');
    add_item_form.classList.add('add_form_visible');
    console.log('hi')
});
add_close_btn.addEventListener('click', () => {
    add_item_form.classList.remove('add_form_visible');
    add_item_form.classList.add('add_form_hidden');
});
const update_form_btn = document.getElementById('update_form_btn');
const update_item_form = document.querySelector('.update_item_form');
const update_close_btn = document.querySelector('#update_close_btn')
update_form_btn.addEventListener('click', () => {
    update_item_form.classList.remove('update_form_hidden');
    update_item_form.classList.add('update_form_visible');
});
update_close_btn.addEventListener('click', () => {
    update_item_form.classList.remove('update_form_visible');
    update_item_form.classList.add('update_form_hidden');
});
const add_variant_form = document.querySelectorAll('.add_variant_form')
const add_variant_btn = document.querySelectorAll('.add_variant_btn')
const add_variant_close_btn = document.querySelectorAll('.add_variant_close_btn')
add_variant_btn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        add_variant_form[index].classList.remove('add_variant_form_hidden');
        add_variant_form[index].classList.add('add_variant_form_visible');
    });
});
add_variant_close_btn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        add_variant_form[index].classList.remove('add_variant_form_visible');
        add_variant_form[index].classList.add('add_variant_form_hidden');
    });
});
const update_variant_form = document.querySelectorAll('.update_variant_form')
const update_variant_btn = document.querySelectorAll('.update_variant_btn')
const update_variant_close_btn = document.querySelectorAll('.update_variant_close_btn')
update_variant_btn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        update_variant_form[index].classList.remove('update_variant_form_hidden');
        update_variant_form[index].classList.add('update_variant_form_visible');
    });
});
update_variant_close_btn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        update_variant_form[index].classList.remove('update_variant_form_visible');
        update_variant_form[index].classList.add('update_variant_form_hidden');
    });
});
