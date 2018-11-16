function previewFile(currObject) {
  var preview = document.getElementById(currObject.name + 'Preview');
  var file    = document.getElementsByName(currObject.name)[0].files[0];
  var reader  = new FileReader();

  reader.onloadend = function () {
    preview.src = reader.result;
  }

  if (file) {
    reader.readAsDataURL(file);
    var id = currObject.name.replace("image", "");
    document.getElementById('cropme' + id).disabled = false;
    document.getElementById('tooltip' + id).dataset['originalTitle'] = "Crop the image";
  } else {
    preview.src = "";
  }
}

var $modal = $('#modal');
var cropper;
var avatar;
var name;
    function cropMe(currObject) {
      name = currObject.id.replace("cropme", "");
      avatar = document.getElementById('image' + name + 'Preview');
      var image = document.getElementById('image');
      var input = document.getElementById('image' + name);
      var files = input.files;
      var done = function (url) {
        image.src = url;
        $modal.modal('show');
      };
      var reader;
      var file;
      var url;

      if (files && files.length > 0) {
        file = files[0];

        if (URL) {
          done(URL.createObjectURL(file));
        } else if (FileReader) {
          reader = new FileReader();
          reader.onload = function (e) {
            done(reader.result);
          };
          reader.readAsDataURL(file);
        }
      }
    };
    window.addEventListener('DOMContentLoaded', function () {
        var cropmenows = document.getElementsByName('cropmenow');
        var len = cropmenows.length;
        for (var i = 0; i < len; i++) {
            cropmenows[i].disabled = true;
        }
        $('[data-toggle="tooltip"]').tooltip({
            trigger : 'hover'
        });

        $modal.on('shown.bs.modal', function () {
          cropper = new Cropper(image, {
            //aspectRatio: 1,
            //autoCropArea: 1,
            viewMode: 2,
            minCropBoxWidth: 50,
            minCropBoxHeight: 50,
          });
          // Enable zoom in button
          $(".js-zoom-in").click(function () {
            cropper.zoom(0.1);
          });

          // Enable zoom out button
          $(".js-zoom-out").click(function () {
            cropper.zoom(-0.1);
          });
        }).on('hidden.bs.modal', function () {
          cropper.destroy();
          cropper = null;
        });

        document.getElementById('crop').addEventListener('click', function () {
          var initialAvatarURL;
          var canvas;

          $modal.modal('hide');

          if (cropper) {
            canvas = cropper.getCroppedCanvas({
              width: 160,
              height: 160,
          });

            initialAvatarURL = avatar.src;
            avatar.src = canvas.toDataURL();
            var data = cropper.getData(true);
            document.getElementById('inputX' + name).value = data['x'];
            document.getElementById('inputY' + name).value = data['y'];
            document.getElementById('inputWidth' + name).value = data['width'];
            document.getElementById('inputHeight' + name).value = data['height'];
          }
        });
    });
