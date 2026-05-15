
// ================= PRODUCTS =================
const products = [
  {name: "Mobile", img: "images/mobile.jpg"},
  {name: "T-Shirt", img: "images/tshirt.jpg"},
  {name: "Laptop", img: "images/laptop.jpg"},
  {name: "Shoes", img: "images/shoes.jpg"},
  {name: "TV", img: "images/tv.jpg"},
  {name: "Perfume", img: "images/beauty.jpg"}
];

const container = document.getElementById("products");

// ================= RENDER PRODUCTS =================
if(container){
  products.forEach((p, i) => {
    let card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
      <img src="${p.img}" alt="${p.name}">
      <h3>${p.name}</h3>

      <textarea id="r${i}" placeholder="Write review..."></textarea>

      <button type="button"
        onclick="submitReview('${p.name}','r${i}','res${i}', event)">
        Submit
      </button>

      <div id="res${i}" class="result"></div>
    `;

    container.appendChild(card);
  });
}

// ================= SUBMIT REVIEW =================
 function submitReview(product, rid, resid, event) {

  if(event) event.preventDefault();

  let review = document.getElementById(rid).value;

  if(review.trim() === ""){
    alert("⚠️ Please write review");
    return;
  }

  let resultBox = document.getElementById(resid);

  resultBox.innerHTML = `
    <p style="color:blue;">
      Checking review...
    </p>
  `;

  fetch("https://ai-based-fake-review-detection.onrender.com/predict", {

    method: "POST",

    headers: {
      "Content-Type": "application/json"
    },

    body: JSON.stringify({
      review,
      product
    })

  })

  .then(res => res.json())

  .then(data => {

    let finalResult =
      data.final == 1
      ? "Fake ❌"
      : "Genuine ✅";

    resultBox.innerHTML = `

      <div style="
        background:#f4f8ff;
        padding:12px;
        border-radius:10px;
        margin-top:10px;
      ">

        <h3>${finalResult}</h3>

        <p>
          <b>Confidence:</b>
          ${data.confidence}%
        </p>

        <p>
          <b>Reason:</b>
          ${data.reason}
        </p>

        <small>
          LR: ${data.lr}
          |
          RF: ${data.rf}
          |
          XGB: ${data.xgb}
        </small>

      </div>

    `;

    // clear textarea
    document.getElementById(rid).value = "";

    // auto remove after 20 sec
    setTimeout(() => {
      resultBox.innerHTML = "";
    }, 20000);

  })

  .catch(err => {

    console.log(err);

    resultBox.innerHTML = `
      <p style="color:red;">
        ❌ Server Error
      </p>
    `;
  });
}

// ================= LOGIN =================
function login() {
  fetch("https://ai-based-fake-review-detection.onrender.com/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      username: document.getElementById("u").value,
      password: document.getElementById("p").value
    })
  })
  .then(res => res.json())
  .then(data => {
    if(data.success){
      alert("Login Success ✅");
      window.location.href = "index.html";
    } else {
      alert("Invalid Login ❌");
    }
  });
}

// ================= REGISTER =================
function register() {
  fetch("https://ai-based-fake-review-detection.onrender.com/register", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      username: document.getElementById("u").value,
      password: document.getElementById("p").value
    })
  })
  .then(res => res.json())
  .then(data => {
    if(data.msg){
      alert("Registered Successfully ✅");
      window.location.href = "login.html";
    }
  });
}

// ================= ADMIN DATA =================
function loadData(){
  fetch("https://ai-based-fake-review-detection.onrender.com/reviews")
   
  .then(r => r.json())
  .then(data => {

    let t = document.getElementById("t");
    if(!t) return;

    t.innerHTML = "";

    data.forEach(r => {
      let label = r.final == 1 ? "Fake ❌" : "Genuine ✅";

      t.innerHTML += `
        <tr>
          <td>${r.product}</td>
          <td>${r.review}</td>
          <td>${label}</td>
        </tr>
      `;
    });

  });
}

// auto load admin page
window.onload = function(){
  if(document.getElementById("t")){
    loadData();
  }
};

// ================= SEARCH =================
function searchProduct(){
  let val = document.getElementById("search").value.toLowerCase();
  let cards = document.querySelectorAll(".card");

  cards.forEach(card => {
    let name = card.querySelector("h3").innerText.toLowerCase();
    card.style.display = name.includes(val) ? "block" : "none";
  });
}

// ================= DARK MODE =================
function toggleDark(){
  document.body.classList.toggle("dark");
}

// ================= LOGOUT =================
function logout(){
  window.location.href = "login.html";
}