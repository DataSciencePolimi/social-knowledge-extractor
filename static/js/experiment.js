//assigning correct label class according to experiment status
var $label=$('.status')
$.each($label,function(k,v){
    var value = $(v).html()

    if(value==="COMPLETED"){
        $(v).removeClass("label-warning")
        $(v).addClass("label-success")
    }
})
function atLeastOne(){
    return $('input[name="accepted"]:checked').length >=1
}

$("#seed_form").on("submit",function(event){

    if(atLeastOne()){
        return true
    }else{
        var alertHtml = ' <div class="alert alert-danger alert-dismissible" role="alert">'
                    +'<button type="button" class="close" data-dismiss="alert" aria-label="Close">'
                        +'<span aria-hidden="true">&times;</span>'
                   +'</button>'
                    +'Select at least one seed'
                +'</div>'

        $("#alert").html(alertHtml)
        event.preventDefault()
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