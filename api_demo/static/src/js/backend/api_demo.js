var get_category = ()=>$("datalist[id=radioCategory] option[value='" + $("input[list=radioCategory]").val() + "']").data('id');
var get_sub_category = ()=>$("datalist[id=radioSubCategory] option[value='" + $("input[list=radioSubCategory]").val() + "']").data('id');
var get_marketplace = ()=>$("datalist[id=radioMarket] option[value='" + $("input[list=radioMarket]").val() + "']").data('id');
var get_category_data_list = ()=>$("datalist[id=radioCategory] option[value='" + $("input[list=radioCategory]").val() + "']").data();
var getProductName = ()=>$("#productName").val();

var _submit = (e)=>{
    let category = get_category();
    let sub_category = get_sub_category();
    if (!category || !sub_category ) {
        return alert('Please Fill all the Selection');
    }
    let settings = {
        "url": ['/catalogue/category/data', sub_category].join('/'),
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "jsonrpc": "2.0"
        }),
    };

    $.ajax(settings).done(function(response) {
        let result = [];
        $.each(response.result, (index,element)=>{
            result.push({
                "type": "br"
            })
            _allowed_values = element?.allowed_values ? element.allowed_values : [];
            if (element.type === 'boolean') {
                result.push({
                    "type": "checkbox",
                    "caption": element.name,
                    "name": element.code
                });
            } else if (element.type === 'integer') {
                result.push({
                    "type": "number",
                    "caption": element.name,
                    "name": element.code
                })
            } else if (element.type === 'float') {
                result.push({
                    "type": "number",
                    "caption": element.name,
                    "name": element.code,
                    "step": 0.01
                })
            } else if (element.type === 'char') {
                result.push({
                    "type": "text",
                    "name": element.code,
                    "caption": element.name,
                    "name": element.code
                })

            } else if (element.type === 'selection') {
                result.push({
                    "type": "select",
                    "caption": element.name,
                    "name": element.code,
                    "options": _allowed_values.values.reduce((a,v)=>({
                        ...a,
                        [v]: v
                    }), {})
                })

            } else if (element.type === 'html') {
                result.push({
                    "type": "textarea",
                    "caption": element.name,
                    "name": element.code
                })
            } else if (element.type === 'datetime') {
                result.push({
                    "type": "datetime",
                    "caption": element.name,
                    "name": element.code
                })
            } else if (element.type === 'text') {
                result.push({
                    "type": "text",
                    "caption": element.name,
                    "name": element.code
                })
            }
        }
        );
        result.push({
            "type": "br"
        })
        result.push({
            "type": "submit",
            "value": "Upload"
        })
        $.fn.dynamicFields(result);
    });
}
;

var dform = ()=>{
    $(document).ready(function() {

        // Defining  dynamicFields
        $.fn.dynamicFields = function(result) {
            $('#dynamicForm').empty();
            $("#dynamicForm").dform({
                "html": result
            });
            $('#dynamicForm label').siblings().css('margin', '10px');
        }

        $.dform.addType("datetime", function(options) {
            return $("<input>").dform('attr', options).attr({
                "type": "datetime-local"
            });
        });
    });

}

dform();

$('#sendCatalogue').on('click', _submit);

$('#dynamicForm').submit(function() {
    // get all the inputs into an array.
    var $inputs = $('#dynamicForm :input').not(':input[type=submit]');

    let sub_category = get_sub_category();
    var jsonDict = {}
    $inputs.each(function() {
        jsonDict[this.name] = $(this).val();
    });
    var values = {
        'productName': getProductName(),
        'jsonData': jsonDict,
        'category': sub_category,
    };
        let settings = {
        "url": '/catalogue/store/product',
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify({
            "jsonrpc": "2.0",
            "params": values
        }),
    };

    $.ajax(settings)
});

let all_sub_category = $('datalist[id=radioSubCategory] option');

$("input[list=radioCategory]").on('input', function() {
    var val = get_category_data_list() ? get_category_data_list()['subCategory'] : false;
    $('datalist[id=radioSubCategory]').empty();
    $.each(all_sub_category, function(element) {
        $('datalist[id=radioSubCategory]').append(all_sub_category[element]);
    });
    _options = $('datalist[id=radioSubCategory] option').filter(function() {
        return val ? val.includes(this.value): false;
    });
    $('datalist[id=radioSubCategory]').empty();
    $('input[list=radioSubCategory]').val('');
    $.each(_options, function(element) {
        $('datalist[id=radioSubCategory]').append(_options[element]);
    });
});

$('.removeClick').on('click', function(e){
    $(this).siblings('input').val('');
})
