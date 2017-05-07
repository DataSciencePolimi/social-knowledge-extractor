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

//validation
$("#main-form").on("submit",function(event){

    var $title = $("#title");

    if(!$title.val() || $title.val().length===0){

        $title.parent().addClass("has-danger")
        $title.parent().addClass("has-error")
        $('<div class="help-block">Required </div>').appendTo($title.parent())
        event.preventDefault()
        return false
    }

    var $seed = $("#profs input")
    var $file = $("#input_seeds")

    if(!$file.val()){

        for (var index = 0; index < $seed.length; index++) {
            var element = $seed[index];

            element = $(element)
            if(!element.val()){
                event.preventDefault()
                element.parent().addClass("has-danger")
                element.parent().addClass("has-error")
                $('<div class="help-block">Required </div>').appendTo(element.parent())
                return false
            }
            
        }
    }

    var $selected = $('#selected-expertType li')
    var $fileExpert = $("#input_expert")

    if(!$fileExpert.val()){
        if($selected.length===0){
            var $parent = $('#expertType-parent')
            $parent.addClass("has-danger")
            $parent.addClass("has-error")
            $('<div class="help-block">At least one expert type must be selected </div>').appendTo($parent)
            event.preventDefault()
            return false
        }
    }

    return true

    
})

var preselected = [];

if($("#treeview-searchable").data('preselected') && $("#treeview-searchable").data('preselected').length>0  ){
    preselected = JSON.parse($("#treeview-searchable").data('preselected').split("'").join('"'))
}

var checkSelected = function(node){
    if(preselected.indexOf(node.text)!=-1){
        console.log(node)
        node.state.checked = true
        node.state.expanded = true
    }

    if(node.nodes){
        for (var index = 0; index < node.nodes.length; index++) {
            var element = node.nodes[index];
            checkSelected(element)
        }
    }
}

for (var index = 0; index < data.length; index++) {
    var element = data[index];
    checkSelected(element)
}

var $searchableTree = $('#treeview-searchable').treeview({
    data: data,
    showCheckbox: true
});

$searchableTree.on("nodeChecked",function(event,node){
    var name = node.text;

    var $list = $('#selected-expertType')
    $list.append('<li id="'+name+'">'+name+'</li>')
})

$searchableTree.on("nodeUnchecked",function(event,node){
    var name = node.text;

    var $node = $("#"+name)
    $node.remove()
})

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

//assigning correct label class according to experiment status
var $label=$('.status')
$.each($label,function(k,v){
    var value = $(v).html()

    if(value==="COMPLETED"){
        $(v).removeClass("label-warning")
        $(v).addClass("label-success")
    }
})

//ajax call to retrieve morre candidates in the experiment page
function moreCandidates(){
    var $button = $('#more');

    var page = $button.data('page');
    var experiment = $button.data('experiment');

    var data = {
        page:page,
        experiment:experiment
    }

    $.ajax({
        data:data,
        url:"more",
        success:function(result,code,xhqr){

            result = JSON.parse(result)

            $button.data('page',result.page)

            console.log(result)

            var candidates = result.candidates;

            for (var index = 0; index < candidates.length; index++) {
                var c = candidates[index];
                
                var tableRow = '<tr><td><label><a target="_blank" href="http://www.twitter.com/'+c.handle+'">'+c.handle+'</a></label></td>'
                tableRow+='<td>'+parseFloat(c.score).toFixed(2)+' </td>'
                tableRow+='<td>0</td>'
                tableRow+='<td>0</td>'
                tableRow+='<td><input type="checkbox" name="accepted" value="'+c.handle+'" /></td>'
                tableRow+='</tr>'

                $('#candidates_table').append(tableRow)
            }
        },
        error:function(xhqr,code,error){
            console.log(error)
        }
    })
    
}