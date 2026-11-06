/* conspiracion.cl (recreación) — lógica del cliente, sin backend.
   La clave de cada nivel se normaliza, se hashea y, si coincide,
   se salta a la página del siguiente nivel (su nombre de archivo es ese hash). */
(function () {
  "use strict";

  function normalizar(s) {
    return String(s)
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]/g, "");
  }

  // cyrb53 (hash no criptográfico; basta para que las claves no se lean a simple vista)
  function cyrb53(str, seed) {
    seed = seed || 0;
    var h1 = 0xdeadbeef ^ seed, h2 = 0x41c6ce57 ^ seed;
    for (var i = 0, ch; i < str.length; i++) {
      ch = str.charCodeAt(i);
      h1 = Math.imul(h1 ^ ch, 2654435761);
      h2 = Math.imul(h2 ^ ch, 1597334677);
    }
    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
    h1 ^= Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
    h2 ^= Math.imul(h1 ^ (h1 >>> 13), 3266489909);
    return 4294967296 * (2097151 & h2) + (h1 >>> 0);
  }

  function clave(s) {
    return cyrb53(normalizar(s)).toString(36);
  }

  window.Conspiracion = { normalizar: normalizar, clave: clave };

  var form = document.getElementById("form-clave");
  if (!form) return;

  var esperado = form.getAttribute("data-esperado"); // hash de la respuesta correcta
  var destino = form.getAttribute("data-destino");   // archivo del siguiente nivel
  var input = document.getElementById("clave");
  var msg = document.getElementById("mensaje");

  // cursor listo en el recuadro apenas carga el nivel
  try { input.focus({ preventScroll: true }); } catch (e) { input.focus(); }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var intento = clave(input.value);
    if (input.value.trim() === "") return;
    if (intento === esperado) {
      msg.className = "ok";
      msg.textContent = "Correcto. Accediendo...";
      setTimeout(function () { window.location.href = destino; }, 450);
    } else {
      msg.className = "mal";
      msg.textContent = "Esa no es la clave.";
      form.classList.remove("sacudir");
      void form.offsetWidth;
      form.classList.add("sacudir");
      input.select();
    }
  });
})();
