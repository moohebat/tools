function search() {


	$('#status').text('loading...');

	var endpoint = $('#endpoint').val();

	var term = $('#term').val();
	var size = "1000";
	var page = $('#page').val();
	var from = (parseInt(page) - 1) * size;
	var to = (parseInt(page)) * size;

	var query = {
		"query" : {
			"term" : {
				"masterbrain" : term
			}
		}, 
		"size" : size,
		"from" : from
	};

	$.ajax({
		url: endpoint + "/product_hk,product_sg,product_my,product_ph,product_th,product_vn,product_id/_search",
		type: "POST",
		dataType: "json",
		data: JSON.stringify(query),

		success: function(response) {

			$('#results').empty();

			$.each(response.hits.hits, function(index, value) {

				var image = value._source.images[0].s3Url;
				var store = value._source.store.name;
				var masterbrain = value._source.masterbrain;

				var product = `<div class="product"><img src="${image}"><b>${store}</b> - ${masterbrain}</div>`;

				$('#results').append(product);
			});

			$('#status').text('#' + response.hits.total.toLocaleString() + ' (' + from.toLocaleString() + ' - ' + to.toLocaleString() + ')');
		},

		error: function () {
			$('#status').text('error');
		}
	});
}

function next () {
	var page = $('#page').val();
	page = parseInt(page) + 1;
	$('#page').val(page);

	search();
}


function prev () {
	var page = $('#page').val();
	page = parseInt(page) - 1;
	$('#page').val(page);

	search();
}
