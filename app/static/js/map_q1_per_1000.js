// // Play controls stuff
// // http://codepen.io/superpikar/pen/zJsgH
// var state = 'stop';

// function buttonBackPress() {
//     console.log("button back invoked.");
// }

// function buttonForwardPress(map) {
// 	// incomplete
// 	chosen_year = (parseInt(chosen_year) + 1).toString();
// 	change_year(first_run=false);
// }

// function buttonPlayPress() {
//     if(state=='stop'){
//       state='play';
//       var button = d3.select("#button_play").classed('btn-success', true); 
//       button.select("i").attr('class', "fa fa-pause");  
//     }
//     else if(state=='play' || state=='resume'){
//       state = 'pause';
//       d3.select("#button_play i").attr('class', "fa fa-play"); 
//     }
//     else if(state=='pause'){
//       state = 'resume';
//       d3.select("#button_play i").attr('class', "fa fa-pause");        
//     }
//     console.log("button play pressed, play was "+state);
// }

// function buttonStopPress(){
//     state = 'stop';
//     var button = d3.select("#button_play").classed('btn-success', false);
//     button.select("i").attr('class', "fa fa-play");
//     console.log("button stop invoked.");    
// }


// functions

function change_year (first_run) {
    year_history.push(chosen_year) // for some reason can't move this to the click callback. oh well

    if (first_run == true) {
	    map.addSource('blocks', {
	        type: 'geojson',
	        data: data
	    });  

	    var source = new mapboxgl.GeoJSONSource({
	        data: {type: 'FeatureCollection', features: []}
	    });

	    map.addSource('blocks-hover', source);

	    map.addLayer({
	        'id': 'blocks-hover',
	        'source': 'blocks-hover',
	        'type': 'line',
	        'paint': {
	            'line-color': '#f00',
	            'line-width': 2,
	            'line-blur': 2
	        }
	    }, 'waterway-label');

	    map.on('mousemove', function(e) {
	        var features = map.queryRenderedFeatures(e.point, { layers: [chosen_year] });
	        map.getCanvas().style.cursor = (features.length) ? 'default' : '';
	        if (features.length) {
	            var feature = features[0];
	            source.setData({type: 'FeatureCollection', features: [feature]}); 
	            infoEl.innerHTML = getInfoHTML(feature.properties);
	        } else {
	            source.setData({type: 'FeatureCollection', features: []});
	            infoEl.innerHTML = '';
	        }
	    });    
	 } 
	else {
    	map.removeLayer(year_history[year_history.length - 2])	    
	}	

    var min_max_num_total_issues = get_min_max_num_total_issues(data);
    map.addLayer({
        'id': chosen_year,
        'type': 'fill',
        'source': 'blocks',
        'source-layer': 'blocks',
        'paint': {
            'fill-opacity': 0.5,
            'fill-color': {
                property: 'total_issues_' + chosen_year + '_per_1000',
                stops: [[min_max_num_total_issues[0], '#fff'], [min_max_num_total_issues[1], '#f00']]
            }
        }
    }, 'waterway-label');    

    var breakpoints = make_breakpoints(min_max_num_total_issues)
    $( "#grp_0" ).html( breakpoints[0] )
    $( "#grp_1" ).html( breakpoints[1] )
    $( "#grp_2" ).html( breakpoints[2] )
    $( "#grp_3" ).html( breakpoints[3] )
    $( "#grp_4" ).html( breakpoints[4] )
    $( "#grp_5" ).html( breakpoints[5] )
}


function make_breakpoints (start_end) {
    var ans = []

    for (i = 0; i < 6; i++) {
        var num = Math.round((start_end[1] - start_end[0]) / 5 * i + start_end[0])
        ans.push(num)
    }    

    return ans
}


function get_min_max_num_total_issues (data) {
    var total_num_issues = [];
    for (var i in data.features) {
        var num_issues = data.features[i]['properties']['total_issues_' + chosen_year + '_per_1000'];
        if (num_issues == 5394) {
            console.log(data.features[i]['properties'])
        }
        total_num_issues.push(num_issues);
    }

    total_num_issues = total_num_issues.filter(Boolean) // bc 2011 has some NaNs

    for (var _ in [1,2,3,4]) { // removing top 4
        var max = Math.max.apply(null, total_num_issues); // get the max of the array
        total_num_issues.splice(total_num_issues.indexOf(max), 1); // remove max from the array        
    } 
        
    var secondMax = Math.max.apply(null, total_num_issues);
    var ans = [Math.min.apply(null, total_num_issues), secondMax];

    return ans;
}


function get_properties_from_data_dict (tract_and_block_group) {
	for (var i in data.features) {
		var properties = data.features[i].properties;
		if (properties['tract_and_block_group'] == tract_and_block_group) {
			return properties
		} 
	}
}


function getInfoHTML(properties_orig) {
	var tract_and_block_group = properties_orig['tract_and_block_group']
	var properties = get_properties_from_data_dict(tract_and_block_group)

    var container = document.createElement('div');
    container.className = 'pad2 keyline-top';

    var title = document.createElement('h3');
    title.className = 'block space-bottom0';
    title.textContent = 'tract & block group: ' + properties['tract_and_block_group'];

    var income = document.createElement('div');
    // income.innerHTML = '<b>' + properties['total_issues_' + chosen_year] + '</b>'+ ' total issues';
    income.innerHTML = '<b>' + properties['total_issues_' + chosen_year + '_per_1000'] + '</b>'+ ' total issues per 1000';

    var population = document.createElement('div');
    // population.innerHTML = format_top_issues(properties['issues_by_year']);
    population.innerHTML = format_top_issues(properties['issues_by_year_per_1000']);


    container.appendChild(title);
    container.appendChild(income);
    container.appendChild(population);

    return container.outerHTML;
}


function format_top_issues(issues_dict) {
    var string_result = "";

    try {
        var values = Object.entries(issues_dict[chosen_year]);
        values.sort(function(a,b){
            return b[1] - a[1];
        });                
    }
    catch (TypeError) {
        return 0
    }

    for (var i in values) {
        var kv = values[i];
        k = kv[0]
        v = kv[1]
        string_result += '<b>' + v + '</b>' + ' ' + k + '<br>'
    }

    return string_result;
}


// Alex stuff
var chosen_year = "2015";
var data;
var year_history = [];

$.when(
    $.getJSON("get-q1-top-types", function(json) {
        data = json
    })
).done(function () {

})


$("#year").click(function () {
	chosen_year = this.value;
	change_year(first_run=false);
});


// mapbox stuff
mapboxgl.accessToken = 'pk.eyJ1IjoiZXhhbXBsZXMiLCJhIjoiY2lqbmp1MzNhMDBud3VvbHhqbjY1cnV2cCJ9.uGJJU2wgtXzcBNc62vY4_A';
var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/light-v8',
    zoom: 12,
    center: [-71.062621, 42.327706]
});

var infoEl = document.getElementById('info');

map.on('load', function() {
	change_year(first_run=true)
});