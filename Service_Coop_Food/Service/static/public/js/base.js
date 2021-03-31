function alertSwalTopRight(icon, message) {
    swal.fire({
        position: 'top-end',
        icon: icon,
        title: message,
        showConfirmButton: false,
        timer: 150000,
        customClass: 'custom-sweetalert-right',
        imageWidth: 400,
        imageHeight: 400,
        timer : 2000,
    });
}

function alertConfirm( icon,text){
    Swal.fire({
        title: 'Bạn có chắc chắn?',
        text: text,
        icon: icon,
        showCancelButton: true,
        confirmButtonColor: '#17a2b8',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Có , Tôi muốn!',
        cancelButtonText: 'Hủy',
        timer : 2000,
    }).then((result) => {
        return result.isConfirmed;
    });
}