

function postgraph(width, height){
  const svgNode = document.getElementsByTagName("svg")[0]

  const doctype = '<?xml version="1.0" standalone="no"?>'
               + '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">';
  // serialise the graph svg
  const source = (new XMLSerializer()).serializeToString(svgNode);
  // convert to Blob
  const blob = new Blob([ doctype + source], { type: 'image/svg+xml' });
  const imageURL = window.URL.createObjectURL(blob);
  const img = new Image();

  img.onload = async function(){
    let canvas = d3.select('body').append('canvas').node();
    canvas.width = width;
    canvas.height = height;

    let ctx = canvas.getContext('2d');

    // draw image on canvas
    ctx.drawImage(img, 0, 0, width, height);

    let glContextAttributes = { preserveDrawingBuffer: true };
    let gl = canvas.getContext("experimental-webgl", glContextAttributes);


    let imgData = await canvas.toDataURL("image/png");
    canvas.remove();
    // ajax call to send canvas(base64) url to server.
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf)
        }
      }
    })
    let postData = $('form').serializeArray()
    postData.push({name: "image", value: imgData})
    $.ajax({
        type: "POST",
        url: url,
        data: postData,
        success: function () {
          window.location.href = redirectUrl;
        }
    });
  }
  img.src =  imageURL;
}
