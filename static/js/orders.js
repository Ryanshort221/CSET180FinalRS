const reviewBtn = document.querySelectorAll('.review_btn')
const complaintBtn = document.querySelectorAll('.complaint_btn')
const reviewCloseBtn = document.querySelectorAll('.review_form_close_btn')
const reviewForm = document.querySelectorAll('.review_form')
const complaintCloseBtn = document.querySelectorAll('.complaint_form_close_btn')
const complaintForm = document.querySelectorAll('.complaint_form')


reviewBtn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        reviewForm[index].style.display = 'flex'
    })
})

complaintBtn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        complaintForm[index].style.display = 'flex'
    })
})

reviewCloseBtn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        reviewForm[index].style.display = 'none'
    })
})

complaintCloseBtn.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        complaintForm[index].style.display = 'none'
    })
})