
function addCommas(nStr)
{
  nStr += '';
  x = nStr.split('.');
  x1 = x[0];
  x2 = x.length > 1 ? '.' + x[1] : '';
  var rgx = /(\d+)(\d{3})/;
  while (rgx.test(x1)) {
    x1 = x1.replace(rgx, '$1' + ',' + '$2');
  }
  return x1 + x2;
}

 $.ajax({
    url: "https://vivid-inferno-7935.firebaseIO.com/metrics/ga.json",
    context: document.body,
    success: function(data){
      
      var sessions = data[0];
      var increment = data[1];
      var goal = data[2];
      var day = data[3];
      var time = data[4];

      e = document.getElementById('goal');
      e.innerHTML = addCommas(goal);

      e = document.getElementById('day')
      e.innerHTML = day;
      
      e = document.getElementById('time')
      e.innerHTML = time;

      e = document.getElementById('sessions');
      e.innerHTML = addCommas(sessions);

       window.setInterval(function(){
        sessions = sessions + increment;

        element = document.getElementById('sessions')
        element.innerHTML = addCommas(parseInt(sessions));
       }, 1000);
    }
});
 