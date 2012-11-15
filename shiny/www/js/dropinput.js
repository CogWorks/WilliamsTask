$(document).on("drop", "div.dropinput", function(evt) {
  var files = evt.target.files || evt.dataTransfer.files;
  for (var i = 0, f; f = files[i]; i++) {  
    console.log(f);
  }
  evt.stopPropagation();
  evt.preventDefault();
});