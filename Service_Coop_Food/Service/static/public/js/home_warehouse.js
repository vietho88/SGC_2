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
            "className": "align-middle",
        },
        {
            "targets": 13, // your case first column
            "className": "align-middle",
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
                if (data.has_report == 1) {
                    return "<a href='/bill/report_warehouse/"+data.id_cus+"/"+data.group+"/1' target='_blank'>" + data.report_number + "</a>"
                } else {
                    return ""
                }
            },
            "class": "details-control align-middle",
            "orderable": false,
            "defaultContent": ""
        },
        {"data": "tax_number"},
        {"data": "city_name"},
        {"data": "date_group_bill"},
        {"data": "upload_date"},
        {"data": "last_change_date"},
        {"data": "status_bill__symbol"},
        {"data": "status_other"},
        {"data": "vendor_number"},
        {
            "data": "sum_po",
            "render" : function (data) {
                return Number(data).toLocaleString();
            }
        },
        {"data": "po_number"},
        {"data": "reciever_number"},
        {"data": "type_product"},
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
    $('#input_date_from, #input_date_to, #input_date_export_thong_ke, #input_date_from_change_status').datepicker({
        todayBtn: "linked",
        language: "vi",
    })

    if(($('#select_cus_home').val())){
        $('.table-bill-warehouse').DataTable({
            "processing": true,
            "serverSide": true,
            "searching": false,
            "lengthChange": true,
            "pageLength": PAGE_LENGTH_DATATABLE,
            "ordering": false,
            'language': SETTING_DATATABLE_LAN,
            'ajax': {
                type: "GET",
                url: "/ajax/datatable/home/warehouse",
                data : function(d){
                    d.list_cus_search = $('#select_cus_home').val()
                    d.date_from = $('#input_date_from').val()
                    d.date_to = $('#input_date_to').val()
                }
            },
            "columns": SETTING_DATATABLE_COLUMN,
            "columnDefs": SETTING_DEF_COL,
        })
    }
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
            "ordering": false,
            'language': SETTING_DATATABLE_LAN,
            'ajax': {
                type: "GET",
                url: "/ajax/datatable/home/warehouse",
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
    $('#inputBillNumber ,#inputReportNumber, #inputTaxNumber, #inputVendorNumber, #inputReceiverNumber, #inputPONumber ').keyup($.debounce(500, function () {
        if(!$('#select_cus_home').val()) {
            return false;
        }
        check = $('.btn-search-advance').hasClass('collapsed')
        if (check){
            check = 'false';
        }
        else {
            check = 'true';
        }
        if ($('#select_status_home').val() == '' || $('#select_cus_home').val() == '') {
            alert("Bạn chưa chọn chi nhánh hoặc trạng thái hóa đơn !!!")
            return false;
        }

        $('.table-bill-warehouse').DataTable().destroy()
        $('.table-bill-warehouse').DataTable({
            "processing": true,
            "serverSide": true,
            "searching": false,
            "lengthChange": true,
            "pageLength": PAGE_LENGTH_DATATABLE,
            "ordering": false,
            'language': SETTING_DATATABLE_LAN,
            'ajax': {
                type: "GET",
                url: "/ajax/datatable/home/warehouse",
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

    //////Search nâng cao ///////
    $('.select-type-product, .select-type-report, .select-qa').change($.debounce(500, function () {
        if (!$('#select_cus_home').val()) {
            return false;
        }
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

        $('.table-bill-warehouse').DataTable().destroy()
        $('.table-bill-warehouse').DataTable({
            "processing": true,
            "serverSide": true,
            "searching": false,
            "lengthChange": true,
            "pageLength": PAGE_LENGTH_DATATABLE,
            "ordering": false,
            'language': SETTING_DATATABLE_LAN,
            'ajax': {
                type: "GET",
                url: "/ajax/datatable/home/warehouse",
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

})

///Functuon search nâng cao
function search_advanced() {
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
            "ordering": false,
            'language': SETTING_DATATABLE_LAN,
            'ajax': {
                type: "GET",
                url: "/ajax/datatable/home/warehouse",
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
                    d.check_seach_advance = check
                }
            },
            "columns": SETTING_DATATABLE_COLUMN,
            "columnDefs": SETTING_DEF_COL,
        })
}