

function getBrand () {
	var brand = $('#brand').val();
	return brand.replace(/(^[\/\s]+)|([\/\s]+$)/g, '');
}

function getCategory () {
	var category = $('#category').val();
	return category.replace(/(^[\/\s]+)|([\/\s]+$)/g, '');
}

function getBrandCategory() {
	var url = "";
	if (brand) {
		if (category) {
			url = brand + "/" + category;
		} else {
			url = brand
		}
	} else {
		url = category;
	}
	return url;
}


function getRelatedBrands(result) {
// might be different for categories and brands
}


function getLowestPrice (result) {
	return result.aggregations.min_price.value.toFixed(2);
}

function getHighestPrice (result) {
	return result.aggregations.max_price.value.toFixed(2);
}

function getMaxDiscount (result) {

}

function getSubCategories (result) {
// might be different for categories and brands
}

function getColours (result) {

}

function getTopSellers (result) {

}


function search() {
	$('#status').text('loading...');

	var endpoint = $('#endpoint').val();
	var index = "product_" + $('#cc').val();

	var query = {
	    "size": 0,
	    "query" : {
	        "bool" : {
	            "must" : [
	                {
	                    "term" : {
	                        "brand.url" : getBrand()
	                    }
	                },
	                {
	                    "term" : {
	                        "category.url.raw" : getCategory()
	                    }
	                }
	            ]
	        }
	    },
	    "aggs" : {
	        "min_price": {
	          "min": {
	            "field": "price.sale"
	          }
	        },
	        "max_price": {
	          "max": {
	            "field": "price.sale"
	          }
	        }
	    }
	};

	$.ajax({
		url: endpoint + "/" + index + "/_search",
		type: "POST",
		dataType: "json",
		data: JSON.stringify(query),

		success: function(response) {

			$('#results').empty();

			console.log(response);
			parse(response);

			$('#status').text('finished');
		},

		error: function () {
			$('#status').text('error');
		}
	});
}

function parse(results) {

	var input = $('#input').val();

	input = replace(input, "[BRAND]", getBrand());
	input = replace(input, "[BRAND CATEGORY]", getBrandCategory());
	input = replace(input, "[CATEGORY]", getCategory());
	input = replace(input, "[HIGHEST PRICE]", getHighestPrice(results));
	input = replace(input, "[LOWEST PRICE]", getLowestPrice(results));

	$('#output').append(input);
}

function replace(string, keyword, value) {
	if (!value) {
		value = keyword;
	}
	return string.replace(keyword, "<b>" + value + "</b>");
}