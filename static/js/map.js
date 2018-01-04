$(function(){

	$('#addBtn').click(function() {
		// console.log(places);
		// var name = places[0].name 
        // var formatted_address = places[0].formatted_address
        // var icon = places[0].icon
        // var ph_domestic = places[0].formatted_phone_number
        // var ph_intl = places[0].international_phone_number
        // var website = places[0].website
        // var latitude = places[0].geometry.location.lat()
        // var longitude = places[0].geometry.location.lng()
        // console.log({{ id }})

      	$.ajax({
			url: '/' + id_current_user + '/addLocation',
			// places is from Search Box
			data: { 
				name: places[0].name,
				formatted_address: places[0].formatted_address,
				icon: places[0].icon,
				ph_domestic: places[0].formatted_phone_number,
				ph_intl: places[0].international_phone_number,
				website: places[0].website,
				latitude: places[0].geometry.location.lat(),
				longitude: places[0].geometry.location.lng()
			},
			type: 'POST',
			success: function(response){
				console.log(response)
				console.log("yes from ajax"); // more simple
			},
			error: function(error){
				console.log(error);
			}
		});
    });

});


