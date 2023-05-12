const showLogin = document.querySelector('.login_btn_landing')
const modal = document.querySelector('.modal1')
const closeModal = document.querySelector('.close_btn')

showLogin.addEventListener('click', () => {
    modal.showModal()
})

closeModal.addEventListener('click', () => {
    modal.close()
})