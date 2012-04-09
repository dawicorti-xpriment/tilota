$(document).ready( function () {
    var gameId = -1;
    $.ajax({
      url: '/api/tilota/game/',
      success: function(data) {
        if (data.objects.length == 0) {
            $.ajax({
                type: 'POST',
                url: '/api/tilota/game/',
                data: '{"info":1}',
                contentType:"application/json; charset=utf-8",
                dataType: 'json',
                success: function(){
                    $.ajax({
                        url: '/api/tilota/game',
                        success: function(data) {
                            gameId = data.objects[0].id;
                        }
                    })
                },
                failure: function() {
                    console.log('failed to post');
                }
            })
        } else {
            gameId = data.objects[0].id;
        }
        //$('#consoleDisplay').html(data.objects);
      },
      failure: function() {
            console.log('ça marche pas');
      }
    });

$("#sendInstructionForm").submit( function(e) {
        $.ajax({
            type: 'POST',
            url: '/api/tilota/game-history/',
            data: '{"request":"'+$('#cmd').val()+'", "game":'+gameId+'}',
            contentType:"application/json; charset=utf-8",
            dataType: 'json',
            success: function(data) {
                $.ajax({
                    url: '/api/tilota/game-history/',
                    success: function(data) {
                        console.log($('#cmd').html());
                        //var text = "";
                        //for(i = 0; i<data.objects.length;i++) {
                        //    text = text+data.objects[i].text+" ";
                        //}

                        $('#consoleDisplay').html(data.objects[data.objects.length-1].text);
                    }
                })

            },
            failure: function() {
                console.log('ça marche pas');
            }
        });
        return (false);
    })

})
