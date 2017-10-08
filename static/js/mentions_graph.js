var $label = $('.status')
$.each($label, function (k, v) {
    var value = $(v).html()

    if (value === "COMPLETED") {
        $(v).removeClass("label-warning")
        $(v).addClass("label-success")
    }
})

var experimentId = $("#graph").data("id");

$.ajax({
    url: "mentions_graph_data?experiment=" + experimentId
})
    .done(function (data) {
        console.log(data)
        var cy = window.cy = cytoscape({
            container: document.getElementById("graph"),
            layout:{
                name:"cose",
                fit:true
            },
            style: [ // the stylesheet for the graph
                {
                    selector: 'node[type="seed"]',
                    style: {
                        'background-color': 'red',
                        'label': 'data(id)'
                    }
                },
                {
                    selector: 'node[type="hub"]',
                    style: {
                        'background-color': 'blue',
                        'label': 'data(id)'
                    }
                },
                {
                    selector: 'node[type="candidate"]',
                    style: {
                        'background-color': 'green',
                        'background-opacity':'data(score)',
                        'label': 'data(id)'
                    }
                },

                {
                    selector: 'edge[type="me"]',
                    style: {
                        'width': 1,
                        'line-color': 'black',
                        'mid-target-arrow-color': 'black',
                        'mid-target-arrow-shape': 'triangle'
                    }
                },

                {
                    selector: 'edge[type="co"]',
                    style: {
                        'width': 1,
                        'line-color': 'black',
                        'line-style': 'dashed'
                    }
                }
            ],
            elements: data
        })

      

    })