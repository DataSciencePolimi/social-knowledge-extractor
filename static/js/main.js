// disable form submission by pressing enter
$("#main-form").bind("keypress", function (e) {
    if (e.keyCode == 13) {
        return false;
    }
});

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
        //expands all the results
        revealResults: true
    };
    var results = $searchableTree.treeview('search', [pattern, options]);

    console.log(results)

    var output = '<p>' + results.length + ' matches found</p>';
    $.each(results, function (index, result) {
        output += '<p>- ' + result.text + '</p>';
    });
    $('#search-output').html(output);

    if(results.length>0){
        // scroll to the first id
        var scrollToId = results[0].nodeId

        var $node = $($searchableTree).find("li[data-nodeid="+scrollToId+"]")

        var offset = $node[0].offsetTop;

        $searchableTree[0].scrollTop = offset - 70 //magic number yeah
    }

};

$('#search-button').on('click', search);

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