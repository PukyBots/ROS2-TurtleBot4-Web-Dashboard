setInterval(() => {

 fetch('/battery')
 .then(r=>r.json())
 .then(data=>{

   document.getElementById(
      'battery'
   ).innerHTML =
      data.battery.toFixed(1)+"%";
 });

},1000);