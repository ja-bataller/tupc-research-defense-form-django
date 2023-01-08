let canvas = document.querySelector("#main_pad");
let form = document.querySelector(".signature-pad-form");
let submit_btn = document.querySelector(".submit-button");
let clearButton = document.querySelector(".clear-button");

let ctx = canvas.getContext("2d");
let writingMode = false;

const handlePointerDown = (event) => {
  writingMode = true;
  ctx.beginPath();
  const [positionX, positionY] = getCursorPosition(event);
  ctx.moveTo(positionX, positionY);
};

const handlePointerUp = () => {
  writingMode = false;
};

const handlePointerMove = (event) => {
  if (!writingMode) return;
  const [positionX, positionY] = getCursorPosition(event);
  ctx.lineTo(positionX, positionY);
  ctx.stroke();
};

const getCursorPosition = (event) => {
  positionX = event.clientX - event.target.getBoundingClientRect().x;
  positionY = event.clientY - event.target.getBoundingClientRect().y;
  return [positionX, positionY];
};

canvas.addEventListener("pointerdown", handlePointerDown, {
  passive: true,
});
canvas.addEventListener("pointerup", handlePointerUp, {
  passive: true,
});
canvas.addEventListener("pointermove", handlePointerMove, {
  passive: true,
});

//variables
let painting = false;

//functions
function startPosition(e) {
  painting = true;
  draw(e);
}

function endPosition() {
  painting = false;
  ctx.beginPath();
}

function draw(e) {
  if (!painting) {
    return;
  }
  e.preventDefault();
  e.stopPropagation();
}

//event listeners
canvas.addEventListener("mousedown", startPosition);
canvas.addEventListener("touchstart", startPosition);
canvas.addEventListener("mouseup", endPosition);
canvas.addEventListener("touchend", endPosition);
canvas.addEventListener("mousemove", draw);
canvas.addEventListener(
  "touchmove",
  function (e) {
    var touch = e.touches[0];
    var mouseEvent = new MouseEvent("mousemove", {
      clientX: touch.clientX,
      clientY: touch.clientY,
    });
    draw(mouseEvent);
  },
  false
);

ctx.lineWidth = 3;
ctx.lineJoin = ctx.lineCap = "round";

submit_btn.addEventListener("click", function (event) {
  event.preventDefault();
  const imageURL = canvas.toDataURL();
  console.log(imageURL);

  if (imageURL == document.getElementById("hidden_pad").toDataURL()) {
    Swal.fire("Invalid", "Please input your Signature.", "error");
    // setTimeout(function () {
    //   window.location.replace("{% url 'panel-title-defense-day' student_username %}");
    // }, 4000);
  } else {
    if (document.getElementById("signature_agreement_checkbox").checked) {
      document.getElementById("signature_url").value = imageURL;
      clearPad();
      document.getElementById("signatureForm").submit();
    } else {
      Swal.fire("Uh-oh", "Please kindly read and check the agreement if you wish to proceed. Thank you.", "error");
    }
  }

  // const image = document.createElement('img');
  // image.src = imageURL;
  // image.height = canvas.height;
  // image.width = canvas.width;
  // image.style.display = 'block';
  // form.appendChild(image);
  // document.getElementById("download").href=imageURL;
  // document.getElementById('download').click();
});

const clearPad = () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
};

clearButton.addEventListener("click", (event) => {
  event.preventDefault();
  clearPad();
});
