


$( document ).ready(function() {
	$(".origine")
  .keyup(function() {
    var value = $( this ).val();
    console.log(value)
    $(".newtext").val( value );
  })
  .keyup();


  function passData() {
	var name = document.getElementById("pass_data").value;
	var dataString = 'data_to_be_pass=' + name;
	if (name == '') {
		alert("Please Enter the Anything");
	} else {
		
	// AJAX code to submit form.
	$.ajax({
		type: "POST",
		url: "pass-data.php",
		data: dataString,
		cache: false,
		success: function(data) {
	$("#message").html(data);
	$("p").addClass("alert alert-success");
	},
	error: function(err) {
	alert(err);
	}
	});
	}
	return false;
}
});

