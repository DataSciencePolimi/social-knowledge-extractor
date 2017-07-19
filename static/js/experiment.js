//assigning correct label class according to experiment status
var $label = $(".status");
$.each($label, function(k, v) {
  var value = $(v).html();

  if (value === "COMPLETED") {
    $(v).removeClass("label-warning");
    $(v).addClass("label-success");
  }
});

var experimentId = $("#data").data("id");
var array;

console.log(experimentId);
$.ajax({
  url: "mentions_distribution?experiment=" + experimentId
}).done(function(data) {
  console.log(data);
  array = data;
  Highcharts.chart("mentions-chart", {
    chart: {
      type: "column"
    },
    title: {
      text: "Types mentioned by the seeds"
    },
    xAxis: {
      type: "category",
      labels: {
        rotation: -45,
        style: {
          fontSize: "13px",
          fontFamily: "Verdana, sans-serif"
        }
      }
    },
    yAxis: {
      min: 0,
      title: {
        text: "Number of mentions"
      }
    },
    legend: {
      enabled: false
    },
    tooltip: {
      pointFormat: "Number of mentions: <b>{point.y}</b>"
    },
    plotOptions: {
      series: {
        cursor: "pointer",
        point: {
          events: {
            click: function() {
              getMentionsByType(this.name);
            }
          }
        }
      }
    },
    series: [
      {
        name: "Mention Types",
        data: data.map(function(x) {
          return [x._id.split("/").pop(), x.count];
        }),
        dataLabels: {
          enabled: true,
          rotation: -90,
          color: "#FFFFFF",
          align: "right",
          y: 10, // 10 pixels down from the top
          style: {
            fontSize: "13px",
            fontFamily: "Verdana, sans-serif"
          }
        }
      }
    ]
  });

  $(".highcharts-xaxis-labels text").click(function() {
    getMentionsByType(this.textContent);
  });
});

function atLeastOne() {
  return $('input[name="accepted"]:checked').length >= 1;
}

$("#seed_form").on("submit", function(event) {
  if (atLeastOne()) {
    return true;
  } else {
    var alertHtml =
      ' <div class="alert alert-danger alert-dismissible" role="alert">' +
      '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
      '<span aria-hidden="true">&times;</span>' +
      "</button>" +
      "Select at least one seed" +
      "</div>";

    $("#alert").html(alertHtml);
    event.preventDefault();
  }
});

//ajax call to retrieve morre candidates in the experiment page
function moreCandidates() {
  var $button = $("#more");

  var page = $button.data("page");
  var experiment = $button.data("experiment");

  var data = {
    page: page,
    experiment: experiment
  };

  $.ajax({
    data: data,
    url: "more",
    success: function(result, code, xhqr) {
      result = JSON.parse(result);

      $button.data("page", result.page);

      console.log(result);

      var candidates = result.candidates;

      for (var index = 0; index < candidates.length; index++) {
        var c = candidates[index];

        var tableRow =
          '<tr><td><label><a target="_blank" href="http://www.twitter.com/' +
          c.handle +
          '">' +
          c.handle +
          "</a></label></td>";
        tableRow += "<td>" + parseFloat(c.score).toFixed(2) + " </td>";
        tableRow += "<td>0</td>";
        tableRow += "<td>0</td>";
        tableRow +=
          '<td><input type="checkbox" name="accepted" value="' +
          c.handle +
          '" /></td>';
        tableRow += "</tr>";

        $("#candidates_table").append(tableRow);
      }
    },
    error: function(xhqr, code, error) {
      console.log(error);
    }
  });
}

//highcharts-xaxis-labels
function getMentionsByType(type) {
  var path = "mentions_by_type";
  $('#mentions-table tbody').remove()
  var data = {
    type: type,
    experiment: experimentId
  };

  $.ajax({
    data: data,
    url: path,
    success: function(result) {

      for (var index = 0; index < result.length; index++) {
        var c = result[index];

        console.log(c);
        var tableRow = "<tr><td>" + c._id + " </td>";
        tableRow += '<td><a href="'+c.uri+'">'+c.title+'</a></td>';
        tableRow += "</tr>";

        $("#mentions-table").append(tableRow);
      }
    }
  });
}
