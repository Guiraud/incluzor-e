$(document).ready(function(){

  // Fair un appel vers le serveur pour 
  $(function(){
    $("#pass_data").autocomplete({
      source: function( request, response ) {
        $.ajax({
          url: "http://api.incluzor.fr:5005/mots/index",
          dataType: "json",
          data: {
            q: request.term
          },
          success: function( data ) {
            // les 10 premiers resultats pour que la liste soit pas trop longue
            response(data.slice(0, 10));
          }
        });
      },
      minLength: 1,
      select: function( event, ui ) {
      },
      open: function() {
        $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
      },
      close: function() {
        $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
      }
    });
  });

  // Convertir le mot en inclusive
  $('#incluzor_mot_form').on("submit", function () {

      // Loading screen
      $("#loading_dial").show();
      $("#resultats").hide();
      $("#resultat_erreurs").hide();
     
      for (var i = 0; i < 3; i++) {
        $('#resultat_mot_0'+i).hide();
      }

      // Le mot a convertir
      var inputText = $("#pass_data").val();

      // Faire un appel API
      $.ajax({
          type: "GET",
          url: "http://api.incluzor.fr:5005/mots/inclusive",
          data: {
              masc: inputText,
          },
          success: function(data) {
              // Debug 
              console.log(data);

              // Loading finished
              $("#loading_dial").hide();

              // Si aucun résultat
              if(data.erreur != null)
              {
                  $("#resultat_erreurs").show();
                  $("#mot_resultat_erreur").text(data.erreur)
              }

              // Si on a des resultats, ajouter les resultats au output
              if(data.inclusives != null)
              {
                  for (var i = 0; i < data.inclusives["feminines"].length; i++) {
                      
                      var fem = data.inclusives["feminines"][i]
                      var fem_sing = fem["singulier"];
                      
                      var rating = ""
                      for (var j = 0; j < 5; j++) {
                          if (j < fem["rating"] * 5)
                          {
                              rating = rating  + "★"
                          }
                          else
                          {
                              rating = rating  + "☆"
                          }
                      }

                      $('#resultat_mot_0'+i).text(fem_sing + " " + rating);
                      $('#resultat_mot_0'+i).show();
                  }
                  $("#resultats_liste").show();
              }
          },
          error: function(xhr, status, err) {
              console.log(xhr);
              $("#loading_dial").hide();
              $("#resultat_erreurs").show();
              $("#mot_resultat_erreur").text(status + " : " + xhr.responseText);
          }
      });
      return false;
  });

});
