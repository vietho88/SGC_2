$(document).ready(function () {
    var PAGE_LENGTH_DATATABLE = 100;
    var SETTING_DATATABLE_LAN = {
        'paginate': {
            "first": "Trang đầu",
            "last": "Trang cuối",
            "next": "Trang sau",
            "previous": "Trang trước"
        },
        'info': "Hiển thị _START_ đến _END_ của _TOTAL_ dòng",
        "infoEmpty":      "Hiển thị 0 đến 0 của 0 dòng",
        'processing': "Đang xử lí, vui lòng đợi !!! ",
        'zeroRecords': "Không có bộ hóa đơn cần tìm kiếm.",
        "lengthMenu": "Hiển thị _MENU_ dòng",
    }

    var SETTING_DEF_COL = [
        {
            "targets": 0, // your case first column
            "className": "align-middle",
        },
        {
            "targets": 1,
            "className": "align-middle",
        },
        {
            "targets": 2, // your case first column
            "className": "align-middle",
        },
        {
            "targets": 3, // your case first column
            "className": "align-middle",
        },
        {
            "targets": 4, // your case first column
            "className": "align-middle",
        },
        {
            "targets": 5,
            "className": "align-middle",
        },
        {
            "targets": 6, // your case first column
            "className": "align-middle",
        }, {
            "targets": 7, // your case first column
            "className": "align-middle",
        },
        {
            "targets": 8,
            "className": "align-middle",
        },
        {
            "targets": 9, // your case first column
            "className": "align-middle",
        },
        {
            "targets": 10, // your case first column
            "className": "align-middle",
        },
        {
            "targets": 11,
            "className": "align-middle",
        },
        {
            "targets": 12, // your case first column
            "className": "align-middle col-max-width",
        },
        {
            "targets": 13, // your case first column
            "className": "align-middle col-max-width",
        },
        {
            "targets": 14, // your case first column
            "className": "align-middle",
        },
        {
            "targets": 15, // your case first column
            "className": "align-middle",
        },
        {
            "targets": 16, // your case first column
            "className": "align-middle",
        }
    ]

    var SETTING_DATATABLE_COLUMN = [
        {
            "data": "group",
            "sName": "Index",
            "render": function (data, type, row, meta) {
                return meta.row + meta.settings._iDisplayStart + 1; // This contains the row index
            }
        },
        {
            // "data": "symbol"
            "data": {group: "group", symbol: "symbol", id_cus : 'id_cus'},
            "render": function (data) {
                return '<a href="/detail/' + data.id_cus + '/' + data.group + '/0" target="blank">' + data.symbol + '</a>' // This contains the row index
            }
        },
        {
            "data": null,
            "render": function (data) {
                if (data.has_report == 1 && data.report_number != 0) {
                    return "<a href='/bill/report/" + data.id_cus + "/" + data.group + "/1' target='_blank'>" + data.report_number + "</a>"
                } else {
                    if(data.status_bill__symbol == 'S - Hóa đơn bị lập biên bản'){
                        return "<a href='/bill/report/"+data.id_cus+"/"+data.group+"/1' target='_blank'>000000</a>"
                    }else {
                        return ""
                    }
                }
            },
            "defaultContent": ""
        },
        {
            data: 'tax_number',
            render: $.fn.dataTable.render.text()
        },{
            data: 'city_name',
            render: $.fn.dataTable.render.text()
        },{
            data: 'date_group_bill',
            render: $.fn.dataTable.render.text()
        },{
            data: 'upload_date',
            render: $.fn.dataTable.render.text()
        },{
            data: 'last_change_date',
            render: $.fn.dataTable.render.text()
        },{"data": "status_bill__symbol"},
        {
            data: 'status_other',
            render: $.fn.dataTable.render.text()
        },{
            data: 'vendor_number',
            render: $.fn.dataTable.render.text()
        },

        {
            "data": "sum_po",
            "render" : function (data) {
                if (data == '[QA]'){
                    return '[QA]'
                }
                else if (data != '' && data != 0){
                    return parseFloat(data).toLocaleString();
                }
                else{
                    return  ''
                }

            }
        },
        {
            data: 'po_number',
            render: $.fn.dataTable.render.text()
        },
        {
            data: 'reciever_number',
            render: $.fn.dataTable.render.text()
        },
        {
            data: 'type_product',
            render: $.fn.dataTable.render.text()
        },
        {
            "data": "is_qa",
            "render": function (data) {
                if (data == 1) {
                    return "<i class='fas fa-check'></i>"
                } else {
                    return ""
                }
            },
        },
        {
            "data": "is_hddt",
            "render": function (data) {
                if (data == 1) {
                    return "<i class='fas fa-check'></i>"
                } else {
                    return ""
                }
            },
        }
    ]
    $('#input_date_from, #input_date_to, #input_date_export_thong_ke, #input_date_from_change_status, #input_date_print_pom').datepicker({
        todayBtn: "linked",
        language: "vi",
        autoclose : true
    })

    $('.table-bill').DataTable({
        "processing": true,
        "serverSide": true,
        "searching": false,
        "lengthChange": true,
        "pageLength": PAGE_LENGTH_DATATABLE,
        "ordering": true,
        'language': SETTING_DATATABLE_LAN,
        'ajax': {
            type: "GET",
            url: "/ajax/datatable/home",
            data : function(d){
                d.list_status_search = $('#select_status_home').val()
                d.list_cus_search = $('#select_cus_home').val()
                d.date_from = $('#input_date_from').val()
                d.date_to = $('#input_date_to').val()
            }
        },
        "columns": SETTING_DATATABLE_COLUMN,
        "columnDefs": SETTING_DEF_COL,
})

    ////Search bình thường////
    $('.btn-search-home').on('click', function () {
        if ($('#select_status_home').val() == '' || $('#select_cus_home').val() == '') {
            alert("Bạn chưa chọn chi nhánh hoặc trạng thái hóa đơn !!!")
            return false
        }

        $('.table-bill').DataTable().destroy()
        $('.table-bill').DataTable({
            "processing": true,
            "serverSide": true,
            "searching": false,
            "lengthChange": true,
            "pageLength": PAGE_LENGTH_DATATABLE,
            "ordering": true,
            'language': SETTING_DATATABLE_LAN,
            'ajax': {
                type: "GET",
                url: "/ajax/datatable/home",
                data: function (d) {
                    d.list_status_search = $('#select_status_home').val()
                    d.list_cus_search = $('#select_cus_home').val()
                    d.date_from = $('#input_date_from').val()
                    d.date_to = $('#input_date_to').val()
                }
            },
            "columns": SETTING_DATATABLE_COLUMN,
            "columnDefs": SETTING_DEF_COL,

        })
    })


    //////Search nâng cao ///////
    $('#inputBillNumber ,#inputReportNumber, #inputTaxNumber, #inputVendorNumber, #inputReceiverNumber, #inputPONumber, #inputCityName ').keyup($.debounce(500, function () {
        check = $('.btn-search-advance').hasClass('collapsed')
        if (check){
            check = 'false'
        }
        else {
            check = 'true'
        }
        if ($('#select_status_home').val() == '' || $('#select_cus_home').val() == '') {
            alert("Bạn chưa chọn chi nhánh hoặc trạng thái hóa đơn !!!")
            return false
        }

        $('.table-bill').DataTable().destroy()
        $('.table-bill').DataTable({
            "processing": true,
            "serverSide": true,
            "searching": false,
            "lengthChange": true,
            "pageLength": PAGE_LENGTH_DATATABLE,
            "ordering": true,
            'language': SETTING_DATATABLE_LAN,
            'ajax': {
                type: "GET",
                url: "/ajax/datatable/home",
                data: function (d) {
                    d.list_status_search = $('#select_status_home').val()
                    d.list_cus_search = $('#select_cus_home').val()
                    d.date_from = $('#input_date_from').val()
                    d.date_to = $('#input_date_to').val()
                    d.bill_number_search = $('#inputBillNumber').val()
                    d.report_number_search = $('#inputReportNumber').val()
                    d.report_company_search = $('#inputCityName').val()
                    d.tax_number_search = $('#inputTaxNumber').val()
                    d.vendor_number_search = $('#inputVendorNumber').val()
                    d.receiver_number_search = $('#inputReceiverNumber').val()
                    d.date_to = $('#input_date_to').val()
                    d.type_product = $('.select-type-product').val()
                    d.type_report = $('.select-type-report').val()
                    d.type_qa = $('.select-qa').val()
                    d.po_number = $('#inputPONumber').val()
                    d.check_seach_advance = check
                }
            },
            "columns": SETTING_DATATABLE_COLUMN,
            "columnDefs": SETTING_DEF_COL,

        })
    }));

    //////Search nâng cao ///////
    $('.select-type-product, .select-type-report, .select-qa').change($.debounce(500, function () {
        check = $('.btn-search-advance').hasClass('collapsed')
        if (check){
            check = 'false'
        }
        else {
            check = 'true'
        }
        if ($('#select_status_home').val() == '' || $('#select_cus_home').val() == '') {
            alert("Bạn chưa chọn chi nhánh hoặc trạng thái hóa đơn !!!")
            return false
        }

        $('.table-bill').DataTable().destroy()
        $('.table-bill').DataTable({
            "processing": true,
            "serverSide": true,
            "searching": false,
            "lengthChange": true,
            "pageLength": PAGE_LENGTH_DATATABLE,
            "ordering": true,
            'language': SETTING_DATATABLE_LAN,
            'ajax': {
                type: "GET",
                url: "/ajax/datatable/home",
                data: function (d) {
                    d.list_status_search = $('#select_status_home').val()
                    d.list_cus_search = $('#select_cus_home').val()
                    d.date_from = $('#input_date_from').val()
                    d.date_to = $('#input_date_to').val()
                    d.bill_number_search = $('#inputBillNumber').val()
                    d.report_number_search = $('#inputReportNumber').val()
                    d.tax_number_search = $('#inputTaxNumber').val()
                    d.vendor_number_search = $('#inputVendorNumber').val()
                    d.receiver_number_search = $('#inputReceiverNumber').val()
                    d.date_to = $('#input_date_to').val()
                    d.type_product = $('.select-type-product').val()
                    d.type_report = $('.select-type-report').val()
                    d.type_qa = $('.select-qa').val()
                    d.po_number = $('#inputPONumber').val()
                    d.check_seach_advance = check
                }
            },
            "columns": SETTING_DATATABLE_COLUMN,
            "columnDefs": SETTING_DEF_COL,

        })
    }));

    ///Find ngành hàng chuyển hàng loạt
    $('#select_status_home_change_status').change(function () {
        if(!$('#select_status_home_change_status').val().length){
            return false
        }
        $.ajax({
            url : '/ajax/home/get_batch_type_change_many_status',
            type : 'get',
            data : {
                list_status : $('#select_status_home_change_status').val(),
                cus : $('#select_cus_home_change_status').val(),
                date: $('#input_date_from_change_status').val(),
                message : 'find_type_product'
            },
            success : function (data) {
                if (data.message == 'success' && data.type_products.length > 0){
                    html_type = ''
                    data.type_products.forEach(function (element) {
                        html_type += "<option value='" + element[0] + "'> " + element[1] + "</option>"
                    })
                    $('#select_product_home_change_status').html(html_type)
                    $('#select_product_home_change_status').selectpicker('refresh')
                }
                else{
                    html_type = ''
                    $('#select_product_home_change_status').html(html_type)
                    $('#select_product_home_change_status').selectpicker('refresh')
                     html_batch = ''
                    $('#select_dot_home_change_status').html(html_batch)
                    $('#select_dot_home_change_status').selectpicker('refresh')
                    alertSwalTopRight('info', 'Không có bộ hóa đơn cần tìm kiếm')
                }
                $('.table-change-many-status tbody ').html('')

            },
            error : function (data) {
            }
        })
    })

    ///Find đợt chuyển hàng loạt
    $('#select_product_home_change_status').change(function () {
        if(!$('#select_product_home_change_status').val().length){
            return false
        }
        $.ajax({
            url : '/ajax/home/get_batch_type_change_many_status',
            type : 'get',
            data : {
                list_status : $('#select_status_home_change_status').val(),
                cus : $('#select_cus_home_change_status').val(),
                type_product : $('#select_product_home_change_status').val(),
                date: $('#input_date_from_change_status').val(),
                message : 'find_batch'
            },
            success : function (data) {
                if (data.message == 'success' && data.batch_ends.length > 0){
                    html_batch = ''
                    data.batch_ends.forEach(function (element) {
                        html_batch += "<option value='" + element[0] + "'> Đợt " + element[0] + "</option>"
                    })
                    $('#select_dot_home_change_status').html(html_batch)
                    $('#select_dot_home_change_status').selectpicker('refresh')
                }
                else{
                    html_batch = ''
                    $('#select_dot_home_change_status').html(html_batch)
                    $('#select_dot_home_change_status').selectpicker('refresh')
                    alertSwalTopRight('info', 'Không có bộ hóa đơn cần tìm kiếm')
                }
                $('.table-change-many-status tbody ').html('')
            },
            error : function (data) {
            }
        })
    })

    // get all group bill to chuyển trạng thái hàng loạt
    $(".btn-search-change-many-status").on("click", function () {
        if(!$('#select_product_home_change_status').val().length || !$('#select_dot_home_change_status').val().length){
            alertSwalTopRight('info', 'Bạn chưa chọn ngành hàng hoặc đợt !!')
            return false
        }
        $.ajax({
            url : '/ajax/home/get_bill_change_many_status',
            type : 'get',
            data : {
                status_find : $('#select_status_home_change_status').val(),
                cus_find : $('#select_cus_home_change_status').val(),
                type_product_find : $('#select_product_home_change_status').val(),
                batch_end_find : $('#select_dot_home_change_status').val(),
                date: $('#input_date_from_change_status').val(),
            },
            success : function (data) {
                if (data.message == 'success' && data.group_bills.length > 0){
                    html_table = ''
                    html_select_new_status = ''
                    data.list_per_change.forEach(function (element) {
                        html_select_new_status += "<option value='" + element + "'> Chuyển sang  " + element + "</option>"
                    })
                    data.group_bills.forEach(function (e, index) {
                        var sum_po = (e.sum_po == '[QA]') ? 'QA' : (e.sum_po == '') ? '' : parseFloat(e.sum_po).toLocaleString()
                        html_table += '<tr role="row" class="odd">\n' +
                            '                                        <td class="text-center align-middle"> <input type="checkbox"> <input type="hidden" value="'+e.group+'"> </td>\n' +
                            '                                        <td class="text-center align-middle">'+(Number(index)+1)+'</td>\n' +
                            '                                        <td class="text-center align-middle">'+e.symbol+'</td>\n' +
                            '                                        <td class="text-center align-middle">'+e.tax_number+'</td>\n' +
                            '                                        <td class="align-middle">'+e.city_name+'</td>\n' +
                            '                                        <td class="text-center align-middle">'+e.date_group_bill+'</td>\n' +
                            '                                        <td class="text-center align-middle">'+ sum_po +'</td>\n' +
                            '                                        <td class="text-center align-middle">'+e.vendor_number+'</td>\n' +
                            '                                        <td class="text-center align-middle">'+ ((e.is_qa == '1') ? (true, "<i class=\"fas fa-check  \"></i>") : "") +'</td>\n' +
                            '                                    </tr>'
                    })
                    $(".table-change-many-status").DataTable().destroy()
                    $("#id_cus_change_many").val($('#select_cus_home_change_status').val())
                    $('.table-change-many-status tbody ').html(html_table)
                    $('.select-change-status-many').html(html_select_new_status)
                    $(".table-change-many-status").DataTable({
                        searching : true,
                        ordering : false,
                        pageLength : 100,
                        paging : false,
                        language: {
                            paginate: {
                                "first": "Trang đầu",
                                "last": "Trang cuối",
                                "next": "Trang trước",
                                "previous": "Trang sau"
                            },
                            info: "Hiển thị _START_ đến _END_ của _TOTAL_ dòng",
                            processing:     "Đang xử lí, vui lòng đợi !!! ",
                            zeroRecords:    "Không có bộ hóa đơn cần tìm kiếm.",
                            search : "Tìm kiếm"
                        }
                    })
                }
                else{
                    html_batch = ''
                    $('#select_dot_home_change_status').html(html_batch)
                    $('#select_dot_home_change_status').selectpicker('refresh')
                }
            },
            error : function (data) {
            }
        })


    })


    $(".btn-export-report-excel").on('click', function () {
        message = $(this).data('message')
        console.log(message)
        if(message == 'export_excel' &&  $('#select_type_product').val().length == 0){
            alert('Bạn chưa chon ngành hàng !!')
            return false
        }
        check_expand = $('.btn-search-advance').hasClass('collapsed')
        if (check_expand){
            check_expand = 'false'
        }
        
        else {
            check_expand = 'true'
        }
        console.log(check_expand)
        $.ajax({
            url : '/ajax/home/export_excel_report',
            type : 'get',
            data : {
                list_status_search : $('#select_status_home').val(),
                list_cus_search : $('#select_cus_home').val(),
                date_from : $('#input_date_from').val(),
                date_to : $('#input_date_to').val(),
                check_seach_advance : check_expand,
                message : message
            },
            success : function (data) {
                if(message == 'get_type_product'){
                    if(data.message == 'success'){
                        window.location.href = data.current_full_url + '&dowload=oke'
                    }else{
                         Swal.fire({
                            position: 'top-end',
                            icon: 'info',
                            title: 'Không có hóa đơn để tải xuống!',
                            showConfirmButton: false,
                            timer: 1500,
                            customClass: 'custom-sweetalert-right'
                        })
                    }
                }
                else{
                    path_dowload = data.path_dowload
                }

            },
            error : function (data) {
                // swal.alert({
                //     title : 'Đã xảy ra lỗi , vui lòng thử lại sau'
                // })
            }
        })
    })

    $('.btn-export-thong-ke').on('click', function () {

        $('#modal_export_thong_ke').modal('show')
        $('.alert-no-bill-thong-ke').html('')
        $('.show_export_statistical').css('display','none')
    })

    $('.btn-search-bill-thong-ke').on( 'click', function () {
        $('.alert-no-bill-thong-ke').html('')
        $.ajax({
            url : '/ajax/home/export_statistical',
            type : 'get',
            data : {
                list_status : $('#select_status_thong_ke').val(),
                cus : $('#select_cus_thong_ke').val(),
                date: $('#input_date_export_thong_ke').val(),
                ket_thuc_dot : $('#input_date_from').val(),
                message : 'get_data'
            },
            success : function (data) {
                if (data.list_type_product.length) {
                    html_type = ''
                    html_dot = ''
                    data.list_type_product.forEach(function (element) {
                        html_type += "<option value='" + element[0] + "'> " + element[1] + "</option>"
                    })
                    data.list_dot.forEach(function (element) {
                        html_dot += "<option value='" + element[0] + "'> Đợt " + element[0] + "</option>"
                    })
                    $('#select_type_product_thong_ke').html(html_type)
                    $('#select_dot_thongke').html(html_dot)
                    $('#select_type_product_thong_ke').selectpicker('refresh')
                    $('#select_dot_thongke').selectpicker('refresh')
                    $('.alert-no-bill-thong-ke').html('Đã tìm xong , vui lòng chọn ngành hàng và đợt cần xuất bên dưới để xuất thống kê !')
                    $('.show_export_statistical').css('display','block')
                } else {
                    html_type = ''
                    html_dot = ''
                    $('#select_type_product_thong_ke').html(html_type)
                    $('#select_dot_thongke').html(html_dot)
                    $('#select_type_product_thong_ke').selectpicker('refresh')
                    $('#select_dot_thongke').selectpicker('refresh')
                    $('.alert-no-bill-thong-ke').html('Không có hóa đơn ở ngày '+$('#input_date_export_thong_ke').val()+'(Chi nhánh '+ $('#select_cus_thong_ke option:selected').text() +')!!')
                }
            },
            error : function (data) {
                // swal.alert({
                //     title : 'Đã xảy ra lỗi , vui lòng thử lại sau'
                // })
            }
        })
    })

    $('#input-check-all-change-many-status').change(function () {
        console.log("bấn")
        if($(this).is(':checked')){
            $('.table-change-many-status input[type="checkbox"]').prop('checked', true)
        }
        else{
            $('.table-change-many-status input[type="checkbox"]').prop('checked', false)
        }

    })

    //Submit change many
    $('.btn-submit-change-many').click(function () {
        if(!$('.table-change-many-status tbody input[type="checkbox"]:checked').length){
            alertSwalTopRight('info', 'Bạn chưa chọn bộ hóa đơn nào cả !!')
            return false
        }
        Swal.fire({
                    title: 'Bạn có chắc chắn?',
                    text: 'Chuyển tất cả các hóa đơn đã chọn sang trạng thái '+ $('.select-change-status-many').val() +'!!',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#17a2b8',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Có, chắc chắn!',
        }).then((result) => {
            var list_group = []
            if (result.isConfirmed) {
                $('.table-change-many-status tbody input[type="checkbox"]:checked').each(function (i) {
                    console.log($(this).closest('td').find('input[type="hidden"]').val())
                    list_group.push($(this).closest('td').find('input[type="hidden"]').val())
                    console.log(list_group)
                })
                var form_data = new FormData(document.getElementById('form_change_many_status'))
                form_data.append('groups', list_group)
                $.ajax({
                    url : "/ajax/home/change_many_status",
                    type : 'POST',
                    data: form_data,
                    contentType : false,
                    processData : false,
                    success: function (data) {
                        if(data.message == 'success'){
                            swal.fire({
                                icon : 'success',
                                title : 'Kết quả',
                                html : 'Thành công : '+ data.list_success.length +' <br>' +
                                       'Thất bại vì bộ còn QA : '+ data.list_fail_because_qa.length +' <br>' +
                                        'Thất bại vì bộ còn chưa đủ dữ liệu cần thiết : '+ data.list_fail_because_data.length +' <br>'

                            })
                            $('.table-change-many-status tbody tr ').each(function (i) {
                                group = $(this).find('td:first input[type="hidden"]').val()
                                group_find_index = "'" + group + "'"
                                if (data.list_success.indexOf(group_find_index) != -1){
                                    $(this).remove()
                                }
                            })
                            // $('.table-change-many-status tbody ').html('')
                            // $('.btn-search-change-many-status').click()
                        }
                    },
                    error: function (data) {

                    }
                })
            }
        })
    })

    //reset modal
    $('#modal_change_more_status').on('hidden.bs.modal', function (e) {
        reset_all_change_many_status()
    })

    //reset all chon lai ngay hoac chi nhanh
    $('#input_date_from_change_status, #select_cus_home_change_status').on('change',function () {
        reset_all_change_many_status()
    })
    $('#select_dot_home_change_status').on('change',function () {
        $('.table-change-many-status tbody ').html('')
    })


    //find nganh hang
    $('#select_cus_home_print_pom, #input_date_print_pom').on('change', function () {
       reset_all_print_pom()
    })

    $('#select_type_print_pom').on('change', $.debounce(500 , function () {
        $.ajax({
            url : '/ajax/home/print_pdf_pom',
            type : 'get',
            data : {
                cus : $('#select_cus_home_print_pom').val(),
                date: $('#input_date_print_pom').val(),
                type: $('#select_type_print_pom').val(),
                message : 'get_type_product'
            },
            success : function (data) {
                if (data.list_type_product.length) {
                    html_type = ''
                    html_dot = ''
                    data.list_type_product.forEach(function (element) {
                        html_type += "<option value='" + element[0] + "'> " + element[1] + "</option>"
                    })
                    $('#select_product_homeprint_pom').html(html_type)
                    $('#select_product_homeprint_pom').selectpicker('refresh')
                     $('#select_dot_home_print_pom').html(html_dot)
                    $('#select_dot_home_print_pom').selectpicker('refresh')

                } else {
                    html_type = ''
                    html_dot = ''
                    $('#select_product_homeprint_pom').html(html_type)
                    $('#select_product_homeprint_pom').selectpicker('refresh')
                    $('#select_dot_home_print_pom').html(html_dot)
                    $('#select_dot_home_print_pom').selectpicker('refresh')
                    alertSwalTopRight('info', 'Không có ngành hàng thuộc loại chứng từ này!!')
                }
            },
            error : function (data) {
            }
        })
    }))

    $('#select_product_homeprint_pom').on('change',  $.debounce(500 , function () {
        $.ajax({
            url : '/ajax/home/print_pdf_pom',
            type : 'get',
            data : {
                cus : $('#select_cus_home_print_pom').val(),
                date: $('#input_date_print_pom').val(),
                type: $('#select_type_print_pom').val(),
                list_product: $('#select_product_homeprint_pom').val(),
                message : 'get_end_batch'
            },
            success : function (data) {
                if (data.list_end_batch.length) {
                    html_type = ''
                    data.list_end_batch.forEach(function (element) {
                        console.log(element)
                        html_type += "<option value='" + element + "'> Đợt  " + element + "</option>"
                    })
                    $('#select_dot_home_print_pom').html(html_type)
                    $('#select_dot_home_print_pom').selectpicker('refresh')
                } else {
                    html_type = ''
                    $('#select_dot_home_print_pom').html(html_type)
                    $('#select_dot_home_print_pom').selectpicker('refresh')
                    alertSwalTopRight('info', 'Không có đợt thuộc loại chứng từ !!')
                }
                $('.table-print-pom tbody ').html('')
            },
            error : function (data) {
            }
        })
    }))

    $('#select_dot_home_print_pom').change(()=>{
        $('.table-print-pom tbody ').html('')
    })

    $('#input-check-all-print-pom').change(function () {
        if($(this).is(':checked')){
            $('.table-print-pom input[type="checkbox"]').prop('checked', true)
            $('.table-print-pom input[name="input_id_print\[\]"]').removeAttr('disabled', 'disabled')
        }
        else{
            $('.table-print-pom input[type="checkbox"]').prop('checked', false)
            $('.table-print-pom input[name="input_id_print\[\]"]').attr('disabled', 'disabled')
        }

    })

    $('.table-print-pom tbody ').on('change', 'input[type="checkbox"]', function () {
        if ($(this).is(':checked')) {
            $(this).parent().children('input[name="input_id_print\[\]"]').removeAttr('disabled', 'disabled')
        } else {
            $(this).parent().children('input[name="input_id_print\[\]"]').attr('disabled', 'disabled')
        }
    })

    $(".btn-search-data-print-pom").on("click", function () {
        // if (!$('#select_product_homeprint_pom').val().length) {
        //     alertSwalTopRight('info', 'Bạn chưa chọn đủ điều kiện tìm kiếm  !!')
        //     return false
        // }
        $.ajax({
            url: '/ajax/home/print_pdf_pom',
            type: 'get',
            data: {
                cus : $('#select_cus_home_print_pom').val(),
                date: $('#input_date_print_pom').val(),
                message: 'get_data',
                type: $('#select_type_print_pom').val(),
                list_product: $('#select_product_homeprint_pom').val(),
                list_end_batch: $('#select_dot_home_print_pom').val(),
            },
            success: function (data) {
                if (data.message == 'success' && data.data.length > 0) {
                    html_table = ''
                    data.data.forEach(function (e, index) {
                        html_table += '<tr role="row" class="odd">\n' +
                            '                                        <td class="text-center align-middle"> <input type="checkbox"> <input disabled="disableds" name="input_id_print[]" type="hidden" value="' + e.group + '"> </td>\n' +
                            '                                        <td class="text-center align-middle">' + (Number(index) + 1) + '</td>\n' +
                            '                                        <td class="text-center align-middle">' + e.bill_number + '</td>\n' +
                            '                                        <td class="text-center align-middle">' + e.reciever_number + '</td>\n' +
                            '                                        <td class="text-center align-middle">' + e.type_product + '</td>\n' +
                            '                                        <td class="text-center align-middle"> Đợt ' + e.end_batch + '</td>\n' +
                            '                                    </tr>'
                    })
                    $(".table-print-pom").DataTable().destroy()
                    $('.table-print-pom tbody ').html(html_table)
                    $(".table-print-pom").DataTable({
                        searching: true,
                        ordering: false,
                        pageLength: 100,
                        paging: false,
                        language: {
                            paginate: {
                                "first": "Trang đầu",
                                "last": "Trang cuối",
                                "next": "Trang trước",
                                "previous": "Trang sau"
                            },
                            info: "Hiển thị _START_ đến _END_ của _TOTAL_ dòng",
                            processing: "Đang xử lí, vui lòng đợi !!! ",
                            zeroRecords: "Không có bộ hóa đơn cần tìm kiếm.",
                            search: "Tìm kiếm"
                        }
                    })
                } else {
                    $('.table-print-pom tbody ').html('')
                    alertSwalTopRight('info', 'Không có hóa đơn được tìm thấy')
                }
            },
            error: function (data) {
            }
        })


    })

    $("#btn-print-pom").on('click', function () {
        if (!$('.table-print-pom tbody input[type="checkbox"]:checked').length) {
            alertSwalTopRight('info', 'Bạn chưa chọn hóa đơn nào cả !!')
            return false
        }
        let form_data = new FormData(document.getElementById('form_print_pom'))
        form_data.append('id_cus', $('#select_cus_home_print_pom').val())
        form_data.append('message', 'print')
        $.ajax({
            url: "/ajax/home/print_pdf_pom",
            type: 'post',
            data: form_data,
            processData: false,
            contentType: false,
            success: function (data) {
                if (data.message == 'oke') {
                    window.open('/media/pdf_merge/' + data.data, '_blank')
                } else {
                    alertSwalTopRight('info', 'Không có pdf để xuất !!')
                }
            },
            error: function (data) {
            }
        })
    })
})

//Function reset all wwhen change-many-status
function reset_all_change_many_status() {
        html_type = ''
        html_dot = ''
        $('#select_product_home_change_status').html(html_type)
        $('#select_dot_home_change_status').html(html_dot)
        $('#select_product_home_change_status').selectpicker('refresh')
        $('#select_dot_home_change_status').selectpicker('refresh')
        $('#select_status_home_change_status').val('')
        $('#select_status_home_change_status').selectpicker('refresh')
        $('.table-change-many-status tbody ').html('')
}

//Function reset all wwhen change-many-status
function reset_all_print_pom() {
        $('#select_type_print_pom').val('1')
        $('#select_type_print_pom').selectpicker('refresh')
        $('#select_product_homeprint_pom').html('')
        $('#select_product_homeprint_pom').selectpicker('refresh')
        $('#select_dot_home_print_pom').html('')
        $('#select_dot_home_print_pom').selectpicker('refresh')
        $('.table-print-pom tbody ').html('')
}