$("#submit-form").on("click", function (e) {
    e.preventDefault();
    console.log($('.node-checked'));
    $('.node-checked').each(function (index) {
        $("#main-form").append('<input style="display:none" type="checkbox" name="check-box' + index + '" value="' + $(this).text() + '" checked> ' + $(this).text() + '');
    });
    $("#main-form").submit();
});

var $searchableTree = $('#treeview-searchable').treeview({
    data: data,
    showCheckbox: true
});
var search = function (e) {
    var pattern = $('#input-search').val();
    var options = {
        ignoreCase: true,
        exactMatch: false,
        revealResults: false
    };
    var results = $searchableTree.treeview('search', [pattern, options]);

    // Check/uncheck/toggle nodes
    var findExpandibleNodess = function () {
        return $searchableTree.treeview('search', [pattern, {ignoreCase: false, exactMatch: true}]);
    };
    $('.expand-node').prop('disabled', !(findExpandibleNodess().length >= 1));


    var output = '<p>' + results.length + ' matches found</p>';
    $.each(results, function (index, result) {
        output += '<p>- ' + result.text + '</p>';
    });
    $('#search-output').html(output);

};
$('#input-search').on('keyup', search);

$(document).ready(function () {
    var next = 1;
    $(".add-more").click(function (e) {
        var number_fields = $('.dynamic-input').length + 1;
        console.log(number_fields);
        e.preventDefault();
        next = next + 1;
        var adding = '<div class="row dynamic-input" id="field' + next + '" style="margin-bottom: 5px"><div class="col-md-10"><input autocomplete="off" class="form-control" id="input-field' + next + '" name="prof' + next + '" type="text" placeholder="Twitter username ' + next + '" aria-describedby="sizing-addon2" data-items="8"/></div></div>';
        var removeBtn = '<div class="col-md-2" id="remove_col' + next + '"><button id="remove' + (next - 1) + '" class="btn btn-danger remove-me" >-</button></div></div></div>';

        $("#field" + (next - 1)).after(adding);

        $("#field" + (next)).append($("#add_col"));
        if (number_fields >= 20) {
            $("#add_col").hide();
        }

        $("#field" + (next - 1)).append(removeBtn);

        $('.remove-me').click(function (e) {
            e.preventDefault();
            var fieldNum = this.id.match(/\d+/);
            var fieldID = "#field" + fieldNum;
            $(this).remove();
            $(fieldID).remove();

            console.log($('.dynamic-input').length + 1);
            if ($('.dynamic-input').length + 1 <= 20) {
                $("#add_col").show();
            }
        });

    });
});

function toggler(divId, e) {
    e.preventDefault();
    $("#" + divId).toggle();
    if ($("#" + "arr_" + divId).attr("class") == 'fa fa-arrow-up')
        $("#" + "arr_" + divId).attr('class', 'fa fa-arrow-down');
    else
        $("#" + "arr_" + divId).attr('class', 'fa fa-arrow-up');
}