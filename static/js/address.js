const addAddressBtn = document.querySelector('.add_address_profile')
const addressCloseBtn = document.querySelector('#address_close_btn')
const addAddressForm = document.querySelector('.add_address_form')
addAddressBtn.addEventListener('click', () => {
    addAddressForm.style.display = 'block'
})

addressCloseBtn.addEventListener('click', () => {
    addAddressForm.style.display = 'none'
})

const UpdateAddressBtn = document.querySelectorAll('.update_address_btn')
const UpdateAddressForm = document.querySelectorAll('.update_address_form')
const modal = document.querySelectorAll('.modal')
const closeModal = document.querySelectorAll('.close_modal')
UpdateAddressBtn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        modal[index].showModal()
    })
})

closeModal.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        modal[index].close()
    })
})