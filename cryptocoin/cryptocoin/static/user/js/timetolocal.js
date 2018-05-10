window.addEventListener('DOMContentLoaded', function () {
    var monthNames = ["January", "February", "March","April", "May", "June", "July","August", "September", "October","November", "December"];

    var allDates = document.getElementsByClassName('fixed-date');
    var len = allDates.length;
    for (var i = 0; i < len; i++) {
        var date = new Date(allDates[i].innerText + ' UTC');
        allDates[i].innerText = monthNames[date.getMonth()] + ' ' + date.getDate() + ', ' + date.getFullYear() + ', ' + date.getHours() + ':' + ('0' + date.getMinutes()).slice(-2) + ':' + ('0' + date.getSeconds()).slice(-2);
    }
});
