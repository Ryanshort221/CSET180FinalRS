adminChatForm = document.querySelectorAll('.admin_chat')
adminCloseBtn = document.querySelectorAll('.admin_chat_close_btn')
adminChatBtn = document.querySelectorAll('.admin_chat_btn')
vendorChatForm = document.querySelectorAll('.vendor_chat')
vendorCloseBtn = document.querySelectorAll('.vendor_chat_close_btn')
vendorChatBtn = document.querySelectorAll('.vendor_chat_btn')

adminChatBtn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        adminChatForm[index].style.display = 'flex'
    })
})

vendorChatBtn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        vendorChatForm[index].style.display = 'flex'
    })
})

adminCloseBtn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        adminChatForm[index].style.display = 'none'
    })
})

vendorCloseBtn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        vendorChatForm[index].style.display = 'none'
    })
})