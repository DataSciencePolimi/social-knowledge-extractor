

//assigning correct label class according to experiment status
var $label=$('.status')
$.each($label,function(k,v){
    var value = $(v).html()

    if(value==="COMPLETED"){
        $(v).removeClass("label-warning")
        $(v).addClass("label-success")
    }
})
