// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ready(function() {
	window.item_code = $('[itemscope] [itemprop="productID"]').text().trim();
	var qty = 0;

	frappe.call({
		type: "POST",
		method: "erpnext.shopping_cart.product.get_product_info",
		args: {
			item_code: get_item_code()
		},
		callback: function(r) {
			$(".item-cart").toggleClass("hide", (!!!r.message.price));
			if(r.message && r.message.price) {
				$(".item-price")
					.html(r.message.price.formatted_price + " {{ _("per") }} " + r.message.uom);
				if ((r.message.net_weight > 0) && (r.message.weight_uom != null)) {
				   $(".item-price-unit")
				      .html("CHF " + (r.message.price.price_list_rate / r.message.net_weight).toFixed(2) + "/" + r.message.weight_uom);
				   $(".item-price-volume")
				      .html("Gebinde: " + r.message.net_weight + " " + r.message.weight_uom);
				}

				if(r.message.in_stock==0) {
					if(r.message.is_stock_item==0) {
						var qty_display = "{{ "Bestellbar" }}";
						$(".item-stock").html("<div style='color: green'>\
							<i class='fa fa-check'></i> "+qty_display+"</div>");
					} else {
						$(".item-stock").html("<div style='color: red'> <i class='fa fa-close'></i> {{ _("Not in stock") }}</div>");
						$(".item-cart").toggleClass("hide");
					}
				}
				else if(r.message.in_stock==1) {
					var qty_display = "{{ _("In stock") }}";
					if (r.message.show_stock_qty) {
						qty_display += " ("+r.message.stock_qty+")";
					}
					$(".item-stock").html("<div style='color: green'>\
						<i class='fa fa-check'></i> "+qty_display+"</div>");
				}

				if(r.message.qty) {
					qty = r.message.qty;
					toggle_update_cart(r.message.qty);
				} else {
					toggle_update_cart(0);
				}
			}
		}
	});

	$("#item-add-to-cart button").on("click", function() {
		var c = "";
		if (document.getElementById('tint') !== null) {
			c = document.getElementById('tint').value;
			if (c == "") {
				window.alert("Bitte eine Tönung eingeben.");
				document.getElementById('tint').focus();
				return;
			}
		}
		var quantity = 1;
		var qtyInput = document.getElementById('cart-qty').value;
		if (!isNaN(qtyInput)) {
			quantity = parseInt(qtyInput);
		}

		frappe.call({
			type: "POST",
			method: "erpnext.shopping_cart.cart.update_cart",
			args: {
				item_code: get_item_code(),
				qty: quantity,
				color: c
			},
			callback: function(r) {
				if(!r.exc) {
					toggle_update_cart(1);
					qty = 1;
				}
			},
			btn: this
		})
	});

	$("[itemscope] .item-view-attribute .form-control").on("change", function() {
		try {
			var item_code = encodeURIComponent(get_item_code());

		} catch(e) {
			// unable to find variant
			// then chose the closest available one

			var attribute = $(this).attr("data-attribute");
			var attribute_value = $(this).val()
			var item_code = find_closest_match(attribute, attribute_value);

			if (!item_code) {
				frappe.msgprint(__("Cannot find a matching Item. Please select some other value for {0}.", [attribute]))
				throw e;
			}
		}

		// prevent self-postback 
		if (window.location.search == ("?variant=" + item_code)) {
			return;
		} 

		window.location.href = window.location.pathname + "?variant=" + item_code;
	});

	$("#cart-btn-more").on('click', function() {
		var val = document.getElementById('cart-qty').value;
		if (isNaN(val)) {
			val = 1;
		}
		else {
			val = parseInt(val) + 1;
		}
		document.getElementById('cart-qty').value = val;
	});

	$("#cart-btn-less").on('click', function() {
		var val = document.getElementById('cart-qty').value;
		if (isNaN(val)) {
			val = 1;
		}
		else {
			val = parseInt(val) - 1;
			if (val < 1) { val = 1; };
		}
		document.getElementById('cart-qty').value = val;
	});
});

var toggle_update_cart = function(qty) {
	$("#item-add-to-cart").toggle(qty ? false : true);
	$("#item-update-cart")
		.toggle(qty ? true : false)
		.find("input").val(qty);
}

function get_item_code() {
	var variant_info = window.variant_info;
	if(variant_info) {
		var attributes = get_selected_attributes();
		var no_of_attributes = Object.keys(attributes).length;

		for(var i in variant_info) {
			var variant = variant_info[i];

			if (variant.attributes.length < no_of_attributes) {
				// the case when variant has less attributes than template
				continue;
			}

			var match = true;
			for(var j in variant.attributes) {
				if(attributes[variant.attributes[j].attribute]
					!= variant.attributes[j].attribute_value
				) {
					match = false;
					break;
				}
			}
			if(match) {
				return variant.name;
			}
		}
		throw "Unable to match variant";
	} else {
		return window.item_code;
	}
}

function find_closest_match(selected_attribute, selected_attribute_value) {
	// find the closest match keeping the selected attribute in focus and get the item code

	var attributes = get_selected_attributes();

	var previous_match_score = 0;
	var previous_no_of_attributes = 0;
	var matched;

	var variant_info = window.variant_info;
	for(var i in variant_info) {
		var variant = variant_info[i];
		var match_score = 0;
		var has_selected_attribute = false;

		for(var j in variant.attributes) {
			if(attributes[variant.attributes[j].attribute]===variant.attributes[j].attribute_value) {
				match_score = match_score + 1;

				if (variant.attributes[j].attribute==selected_attribute && variant.attributes[j].attribute_value==selected_attribute_value) {
					has_selected_attribute = true;
				}
			}
		}

		if (has_selected_attribute
			&& ((match_score > previous_match_score) || (match_score==previous_match_score && previous_no_of_attributes < variant.attributes.length))) {
			previous_match_score = match_score;
			matched = variant;
			previous_no_of_attributes = variant.attributes.length;


		}
	}

	if (matched) {
		for (var j in matched.attributes) {
			var attr = matched.attributes[j];
			$('[itemscope]')
				.find(repl('.item-view-attribute .form-control[data-attribute="%(attribute)s"]', attr))
				.val(attr.attribute_value);
		}

		return matched.name;
	}
}

function get_selected_attributes() {
	var attributes = {};
	$('[itemscope]').find(".item-view-attribute .form-control").each(function() {
		attributes[$(this).attr('data-attribute')] = $(this).val();
	});
	return attributes;
}
