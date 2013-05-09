$(function () {
        $('#score_chart').highcharts({
            chart: {
                type: 'spline'
            },
            title: {
                text: 'Your Score Data'
            },
            xAxis: [{
                "type": "datetime",
                "labels": {
                    "formatter": function() {
                     return Highcharts.dateFormat("%b %e", this.value)
                    }                    
                }
            }],
            yAxis: {
                title: {
                    text: 'Score'
                },
                min: min_score
            },
            tooltip: {
                formatter: function() {
                        return '<b>'+ this.series.name +'</b><br/>'+
                        Highcharts.dateFormat('%e. %b', this.x) +': '+ this.y;
                }
            },
            
            series: [{
                name: 'Date',
                // Define the data points. All series have a dummy year
                // of 1970/71 in order to be compared on the same x axis. Note
                // that in JavaScript, months start at 0 for January, 1 for February etc.
                data: nine_score_arr.sort()

            },]
        });
    });
    
