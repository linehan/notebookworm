
function ajax(url, options) 
{
        var data    = options.data   || "";
        var method  = options.method || "POST";
        var success = options.success;
        var failure = options.failure;

        var xhr = new XMLHttpRequest();

        xhr.open("POST", url, true);

        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        xhr.onreadystatechange = function() {
                if (xhr.readyState == 4) {
                        if (xhr.status !== 200) {
                                console.log("["+xhr.status+"]"+xhr.responseText);
                                if (typeof failure === "function") {
                                        success(xhr.responseText, xhr);
                                }
                        } else {
                                console.log("["+xhr.status+"]");
                                if (typeof success === "function") {
                                        success(xhr.responseText, xhr);
                                }
                        }
                }
        };
            
        xhr.send(data);

        return xhr;
}


var searchbox     = document.getElementById("searchbox");
var searchbutton  = document.getElementById("searchbutton");
var searchresults = document.getElementById("searchresults");
var caseinfo      = document.getElementById("caseinfo");

searchbutton.addEventListener("click", search_fn);
searchbox.addEventListener("keypress", function(event) {
        if (event.keyCode === 13) {
                search_fn();
        }
});

var GOT = {};

var noneselected = true;

var MyChart = new Chart(document.getElementById("histogram"), {
	type: 'bar',
	data: {
		labels: [],//["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
		datasets: [{
		    label: 'Number of occurrences',
		    data: [],
	 	    backgroundColor:[]
		}]
	},
	options: {
		responsive:true,
                onClick: function(event, legenditem) {
                        chart_item = MyChart.getElementsAtEvent(event);

                        console.log("hey");

                        if (chart_item.length !== 0) {
                                var index = chart_item[0]._index;
                                if (index in GOT) {
                                        bgc = MyChart.data.datasets[0].backgroundColor[index];

                                        if (noneselected == true) {
                                                $("#searchresults tr[data-text-id]").hide();
                                        }
                                       
                                        if (bgc == "#0000ff") {
                                                MyChart.data.datasets[0].backgroundColor[index] = "#ff0000";
                                                $("#searchresults [data-text-id='"+GOT[index].id+"']").hide();
                                        } else {
                                                MyChart.data.datasets[0].backgroundColor[index] = "#0000ff";
                                                $("#searchresults [data-text-id='"+GOT[index].id+"']").show();
                                        }

                                        for (i=0; i<250; i++) {
                                                if (MyChart.data.datasets[0].backgroundColor[i] == "#ff0000") {
                                                        noneselected = true;
                                                } else {
                                                        noneselected = false;
                                                        break;
                                                }
                                        }

                                        if (noneselected) {
                                                $("#searchresults tr[data-text-id]").show();
                                        }

                                        MyChart.update();
                                }
                        }
                },
                hover: {
                        onHover : function(chart_item) {
                                if (chart_item.length !== 0) {
                                        var index = chart_item[0]._index;
                                        if (index in GOT) {
                                                caseinfo.innerHTML = GOT[index].country;
                                        }
                                }
                        },
                },
	}
});

var ByYear = new Chart(document.getElementById("histogram2"), {
	type: 'bar',
	data: {
		labels: [],
		datasets: [{
		    label: 'Number of occurrences',
		    data: [],
	 	    backgroundColor:[]
		}]
	},

	options: {
		responsive:true,
                hover: {
                        onHover : function(chart_item) {
                                if (chart_item.length !== 0) {
                                        var index = chart_item[0]._index;
                                        console.log(index);
                                }
                        },
                },
	}
});

for (var i=0; i<237; i++) {
	ByYear.data.labels.push(1780+i);
	ByYear.data.datasets[0].data.push(0);
	ByYear.data.datasets[0].backgroundColor.push("#ff0000");
}

for (var i=0; i<624; i++) {
	MyChart.data.labels.push(i);
	MyChart.data.datasets[0].data.push(0);
	MyChart.data.datasets[0].backgroundColor.push("#ff0000");
}

MyChart.update();
ByYear.update();


function show_results(json)
{
        var str = "<span class='search-results-info'>Displaying <b>"+json.results.length+"</b> out of <b>"+json.total_matches+"</b> results for '"+json.search_query+"'</span>";
			
	str += "<table><tr><th>id</th><th>ngram</th><th>frequency</th></tr>";

        GOT = {};

	MyChart.data.datasets[0].data = [];
	for (var i=0; i<624; i++) {
		MyChart.data.datasets[0].data.push(0);
	}

	ByYear.data.datasets[0].data = [];
	for (var i=0; i<237; i++) {
		ByYear.data.datasets[0].data.push(0);
	}

        for (i=0; i<json.results.length; i++) {
                /* 
                 * WARNING: As of September 2016, breaking up these lines
                 * will cause over half a second of slowdown in the time
                 * it takes to put these results on screen, due to how slow
                 * string concatenation is in JS. Just let it be a long line.
                 */
                str += "<tr data-text-id='"+json.results[i].text_id+"'><td>"+json.results[i].text_id+"</td><td>"+json.results[i].gram+"</td><td>"+json.results[i].freq+"</td></tr>";

                if (!(json.results[i].text_id in GOT)) {
                        GOT[json.results[i].text_id] = {
                                "id":json.results[i].text_id,
                                "country": json.results[i].text_country,
                                "year": json.results[i].text_year,
                                "gram": [json.results[i]],
                        };
                } else {
                        GOT[json.results[i].text_id].gram.push(json.results[i]);
                }

		MyChart.data.datasets[0].data[json.results[i].text_id] += parseInt(json.results[i].freq);
		ByYear.data.datasets[0].data[json.results[i].text_year - 1780] += parseInt(json.results[i].freq);
        }

        str += "</table>";

        searchresults.innerHTML = str;

	MyChart.update();
	ByYear.update();
}

var search_req = null;

function search_fn()
{
        var search = searchbox.value;
        var n = document.getElementById("selectn").value;
                        
        if (search_req != null) {
                search_req.abort();
        }

        search_req = ajax("/beta/constitutions/server.php", {
                "data":"search="+search+"&n="+n,
                "method":"POST",
                "success":function(data, xhr) {
                        show_results(JSON.parse(data));
                },
        });
}


