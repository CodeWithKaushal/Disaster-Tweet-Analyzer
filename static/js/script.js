$('.rating .fa-star').click(function() {
    $('.rating .active-rating').removeClass('active-rating');
    $(this).toggleClass('active-rating');
});
