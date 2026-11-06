#!/usr/bin/env python3
"""Genera conspiracion.cl (recreación) a partir de la lista de niveles.
Uso: python3 -I build.py <directorio_salida>"""
import base64
import html
import json
import random
import sys
import unicodedata
from pathlib import Path

OUT = Path(sys.argv[1])
M32 = 0xFFFFFFFF


# ------------------------------------------------------------ hash (igual que juego.js)
def normalizar(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return "".join(c for c in s if c.isascii() and c.isalnum())


def imul(a, b):
    return (a * b) & M32


def cyrb53(s, seed=0):
    h1 = (0xDEADBEEF ^ seed) & M32
    h2 = (0x41C6CE57 ^ seed) & M32
    for ch in s:
        c = ord(ch)
        h1 = imul(h1 ^ c, 2654435761)
        h2 = imul(h2 ^ c, 1597334677)
    h1 = imul(h1 ^ (h1 >> 16), 2246822507)
    h1 ^= imul(h2 ^ (h2 >> 13), 3266489909)
    h1 &= M32
    h2 = imul(h2 ^ (h2 >> 16), 2246822507)
    h2 ^= imul(h1 ^ (h1 >> 13), 3266489909)
    h2 &= M32
    return 4294967296 * (2097151 & h2) + h1


def b36(n):
    d = "0123456789abcdefghijklmnopqrstuvwxyz"
    r = ""
    while n:
        n, m = divmod(n, 36)
        r = d[m] + r
    return r or "0"


def clave(s):
    return b36(cyrb53(normalizar(s)))


# ------------------------------------------------------------ utilidades de puzzles
def revolver(palabra, semilla):
    letras = list(palabra.upper())
    rnd = random.Random(semilla)
    for _ in range(100):
        rnd.shuffle(letras)
        if "".join(letras) != palabra.upper():
            break
    return " ".join(letras)


def cesar(texto, n):
    r = ""
    for c in texto.lower():
        r += chr((ord(c) - 97 + n) % 26 + 97) if "a" <= c <= "z" else c
    return r.upper()


MORSE = {"a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.", "g": "--.",
         "h": "....", "i": "..", "j": ".---", "k": "-.-", "l": ".-..", "m": "--", "n": "-.",
         "o": "---", "p": ".--.", "q": "--.-", "r": ".-.", "s": "...", "t": "-", "u": "..-",
         "v": "...-", "w": ".--", "x": "-..-", "y": "-.--", "z": "--.."}


def morse_ascii(t):
    return " ".join(MORSE[c] for c in t.lower())


def numeros(t):
    return " - ".join(str(ord(c) - 96) for c in t.lower())


OJO = r"""
     .-''''''-.
   .'  _    _  '.
  /   (o)  (o)   \
 |        ||       |
  \    '-....-'  /
   '.    ''    .'
     '-......-'
""".strip("\n")


# ------------------------------------------------------------ imágenes (SVG propios)
def svg_osorno():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">
<defs><linearGradient id="c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1d3a"/><stop offset="0.7" stop-color="#d9825b"/><stop offset="1" stop-color="#f2c27b"/></linearGradient></defs>
<rect width="800" height="450" fill="url(#c)"/>
<circle cx="620" cy="110" r="38" fill="#fff3d0" opacity="0.9"/>
<polygon points="40,390 330,170 395,118 460,170 780,390" fill="#2c3e50"/>
<polygon points="300,192 330,170 395,118 460,170 490,196 450,183 418,202 386,180 352,200" fill="#f4f7fa"/>
<polygon points="0,390 160,300 260,360 360,310 520,390" fill="#1f2d3a"/>
<rect x="0" y="385" width="800" height="65" fill="#1b4f72"/>
<polygon points="395,118 430,150 360,150" fill="#fafcff" opacity="0.6"/>
<g fill="#10261b"><polygon points="90,385 105,350 120,385"/><polygon points="120,385 138,340 156,385"/><polygon points="640,385 655,352 670,385"/><polygon points="670,385 688,345 706,385"/></g>
</svg>
"""


def svg_borroso():
    rnd = random.Random(9)
    decoys = []
    for _ in range(14):
        x, y = rnd.randint(20, 880), rnd.randint(20, 240)
        decoys.append(f'<circle cx="{x}" cy="{y}" r="{rnd.randint(8, 40)}" fill="rgb(22,22,22)"/>')
    for _ in range(8):
        decoys.append(
            f'<line x1="{rnd.randint(0, 900)}" y1="{rnd.randint(0, 260)}" x2="{rnd.randint(0, 900)}" y2="{rnd.randint(0, 260)}" stroke="rgb(22,22,22)" stroke-width="4"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 260">'
            '<rect width="900" height="260" fill="rgb(20,20,20)"/>' + "".join(decoys) +
            '<text x="450" y="170" text-anchor="middle" font-family="monospace" font-size="120" '
            'font-weight="bold" fill="rgb(26,26,26)">CHILOE</text></svg>\n')


def svg_edificio():
    rnd = random.Random(21)
    cols, filas, enc = 7, 6, 0
    v = []
    for f in range(filas):
        for c in range(cols):
            on = rnd.random() < 0.55
            enc += on
            v.append(f'<rect x="{40 + c * 38}" y="{40 + f * 40}" width="24" height="28" '
                     f'fill="{"#ffd36b" if on else "#1a2430"}" stroke="#0a0f14"/>')
    svg = ('<svg class="foto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 300" role="img" '
           'aria-label="Edificio de oficinas de noche">'
           '<rect width="330" height="300" fill="#0b1118"/><rect x="25" y="20" width="282" height="272" fill="#2a3644"/>'
           + "".join(v) + '</svg>')
    return svg, enc


def svg_cielo(dest):
    rnd = random.Random(3)
    cruz = [(400, 130, 4.5), (400, 300, 5.5), (330, 205, 3.8), (475, 215, 4.5)]
    quinta = (440, 252)
    est = []
    while len(est) < 70:
        x, y = rnd.uniform(10, 790), rnd.uniform(10, 390)
        if any((x - a) ** 2 + (y - b) ** 2 < 35 ** 2 for a, b, _ in cruz) or (x - quinta[0]) ** 2 + (y - quinta[1]) ** 2 < 40 ** 2:
            continue
        est.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(.6, 1.7):.1f}" fill="#cfe8d8" opacity="{rnd.uniform(.5, 1):.2f}"/>')
    grandes = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff"/>' for x, y, r in cruz)
    return ('<svg class="foto cielo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" role="img" '
            'aria-label="Cielo nocturno del hemisferio sur">'
            '<rect width="800" height="400" fill="#02040a"/>' + "".join(est) + grandes +
            f'<a href="{dest}"><circle cx="{quinta[0]}" cy="{quinta[1]}" r="14" fill="transparent"/>'
            f'<circle cx="{quinta[0]}" cy="{quinta[1]}" r="1.6" fill="#cfe8d8"/></a></svg>')


SVG_PUERTA = """<svg class="puerta" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 260" role="img" aria-label="Una puerta cerrada">
<rect x="40" y="20" width="120" height="220" fill="#1b140d" stroke="#39ff6a"/>
<rect x="55" y="38" width="90" height="75" fill="none" stroke="#1f9c40"/>
<rect x="55" y="128" width="90" height="95" fill="none" stroke="#1f9c40"/>
<circle cx="138" cy="130" r="5" fill="#39ff6a"/><circle cx="100" cy="85" r="6" fill="#39ff6a"/><polygon points="97,88 103,88 105,105 95,105" fill="#39ff6a"/>
</svg>"""


# ------------------------------------------------------------ scripts de niveles
JS_CONSOLA = """
console.log("%cShhh...", "color:#39ff6a;font-size:18px");
console.log("Nadie lee la consola. Por eso se guardan aquí los secretos.");
console.log("La clave de este nivel es: murmullo");
"""

JS_CONTRASTE = """
var im = document.getElementById("borrosa"), b = document.getElementById("brillo"), c = document.getElementById("contraste");
function ajustar() { im.style.filter = "brightness(" + b.value + ") contrast(" + c.value + ")"; }
b.addEventListener("input", ajustar); c.addEventListener("input", ajustar);
"""

JS_MORSE = """
var codigo = "__MORSE__", ctx = null, lamp = document.getElementById("lampara");
document.getElementById("reproducir").addEventListener("click", function () {
  var AC = window.AudioContext || window.webkitAudioContext, osc = null, g = null, u = 0.14, t = 0, base = 0;
  try { if (AC && !ctx) ctx = new AC(); } catch (e) { ctx = null; }
  if (ctx) {
    osc = ctx.createOscillator(); g = ctx.createGain(); osc.frequency.value = 660; g.gain.value = 0;
    osc.connect(g); g.connect(ctx.destination); osc.start(); base = ctx.currentTime + 0.1;
  }
  var ev = [];
  codigo.split("").forEach(function (ch) {
    if (ch === ".") { ev.push([1, 1]); ev.push([0, 1]); }
    else if (ch === "-") { ev.push([1, 3]); ev.push([0, 1]); }
    else if (ch === " ") { ev.push([0, 2]); }
  });
  ev.forEach(function (e) {
    var d = e[1] * u;
    if (e[0]) {
      if (g) { g.gain.setValueAtTime(0.25, base + t); g.gain.setValueAtTime(0, base + t + d); }
      setTimeout(function () { lamp.classList.add("on"); }, t * 1000 + 100);
      setTimeout(function () { lamp.classList.remove("on"); }, (t + d) * 1000 + 100);
    }
    t += d;
  });
  if (osc) osc.stop(base + t + 0.1);
});
"""

JS_TECLADO = """
var buf = "", dest = "__DEST__", est = document.getElementById("estado");
document.addEventListener("keydown", function (ev) {
  if (!ev.key || ev.key.length !== 1) return;
  buf = (buf + ev.key.toLowerCase()).slice(-12);
  if (buf.slice(-6) === "chaito") {
    est.textContent = "La puerta se abre...";
    setTimeout(function () { window.location.href = dest; }, 600);
  }
});
"""

JS_LINTERNA = """
var caja = document.getElementById("linterna"), capa = caja.querySelector(".capa");
function mover(ev) {
  var r = caja.getBoundingClientRect();
  capa.style.setProperty("--x", (ev.clientX - r.left) + "px");
  capa.style.setProperty("--y", (ev.clientY - r.top) + "px");
}
caja.addEventListener("pointermove", mover);
caja.addEventListener("pointerdown", mover);
"""

JS_ESPERA = """
setTimeout(function () { document.getElementById("salida").hidden = false; }, 45000);
"""

JS_AGENTE = """
var v = new URLSearchParams(window.location.search).get("agente");
var e = document.getElementById("estado");
if (v === null) {
  e.textContent = "ACCESO DENEGADO. Se esperaba un parámetro «agente» en la dirección (…?agente=VALOR).";
} else if (Conspiracion.clave(v) === "__HASH__") {
  e.textContent = "Agente reconocido. Adelante.";
  document.getElementById("salida").hidden = false;
} else {
  e.textContent = "Agente desconocido. Esa identificación no figura en los registros.";
}
"""

PISOS = {
    0: "Sótano. Hace frío y huele a humedad. Aquí no hay salida, y tampoco más abajo.",
    1: "Piso 1. Recepción. No hay nadie y el mesón está cubierto de polvo. Aquí no hay salida. Los edificios suelen tener más pisos.",
    2: "Piso 2. Oficinas vacías. Un teléfono suena a lo lejos, pero nadie lo contesta.",
    3: "Piso 3. Archivo. Carpetas con los nombres tachados. Nada útil por aquí.",
    4: "Piso 4. Sala de reuniones. En la pizarra, alguien escribió con letra apurada: «sigue contando».",
    5: "Piso 5. Cocina. El café todavía está tibio. Alguien estuvo aquí hace poco.",
    6: "Piso 6. Una escalera de caracol llena de polvo sube hacia una puerta entreabierta. Falta poco.",
}


# ------------------------------------------------------------ niveles
EDIFICIO_SVG, VENTANAS = svg_edificio()

NIVELES = [
    dict(
        tipo="clave", respuesta="fuente", titulo="Nivel 1", mec="Código fuente",
        cuerpo=lambda d: """
<p>Bienvenido, agente. Lo que ves en pantalla es solo la mitad de la historia.</p>
<p>Todo sitio guarda más de lo que muestra. Aprende a mirar <em>detrás</em> de la página.</p>
<!-- Buen ojo. La clave de este nivel es: fuente -->
""",
        pista="Un clic derecho → «Ver código fuente» (o Ctrl+U) te acerca a lo que buscas.",
    ),
    dict(
        tipo="clave", respuesta="cordillera", titulo="Nivel 2 · Anagrama", mec="Anagrama",
        cuerpo=lambda d: f"""
<p>Las letras están desordenadas. Ordénalas y obtendrás aquello que recorre el país de norte a sur y que nadie cruza a la ligera.</p>
<div class="enigma">{revolver("cordillera", 11)}</div>
""",
        pista="Se alza al este de Santiago y se ve incluso con smog.",
    ),
    dict(
        tipo="clave", respuesta="chile", titulo="Nivel 3 · Acertijo", mec="Acertijo",
        cuerpo=lambda d: """
<p>Soy más larga que ancha, tan flaca que casi me parto por la cintura.</p>
<p>Al norte me seco, al sur me congelo; el mar me abraza por un lado y los Andes me guardan la espalda por el otro.</p>
<p>Los poetas dicen que soy «larga pétala de mar y vino y nieve». ¿Cómo me llamo?</p>
""",
        pista="Es la clave más corta de todo el juego, y el nombre de este dominio la delata (.cl).",
    ),
    dict(
        tipo="clave", respuesta="murmullo", titulo="Nivel 4 · Silencio", mec="Consola del navegador",
        cuerpo=lambda d: """
<p>Algo se está diciendo en esta página en este mismo instante. Tú no lo oyes, pero otros sí.</p>
<p>Los conspiradores no gritan: <em>murmuran</em>.</p>
""",
        script=JS_CONSOLA,
        pista="Abre las herramientas de desarrollador (F12 o Ctrl+Shift+I) y mira la pestaña «Console».",
    ),
    dict(
        tipo="clave", respuesta="osorno", titulo="Nivel 5 · Una foto", mec="Nombre del archivo de una imagen",
        assets={"img/osorno.svg": svg_osorno()},
        cuerpo=lambda d: """
<p>Una imagen dice mucho. Pero esta, además, tiene un nombre.</p>
<img class="foto" src="img/osorno.svg" alt="Una imagen">
<p>Mira lo que ves y, después, mira lo que <em>es</em>.</p>
""",
        pista="Clic derecho sobre la imagen → «Abrir imagen en una pestaña nueva». Fíjate en la dirección.",
    ),
    dict(
        tipo="clave", respuesta="valdivia", titulo="Nivel 6 · Cifrado", mec="Cifrado César",
        cuerpo=lambda d: f"""
<p>Un emperador romano mandaba mensajes corriendo cada letra del alfabeto unos pocos lugares. Tres, para ser exactos.</p>
<div class="codigo">{cesar("valdivia", 3)}</div>
<p>Al descifrarlo aparecerá una ciudad del sur, con ríos, lobos marinos y cervecerías.</p>
""",
        pista="La D se esconde detrás de la A. Retrocede tres lugares en cada letra.",
    ),
    dict(
        tipo="clave", respuesta="chiloe", titulo="Nivel 7 · Penumbra", mec="Imagen casi invisible (brillo y contraste)",
        assets={"img/archivo-borroso.svg": svg_borroso()},
        cuerpo=lambda d: """
<p>Este documento fue tan censurado que casi no queda nada. Casi.</p>
<img id="borrosa" class="foto" src="img/archivo-borroso.svg" alt="Una imagen casi completamente negra">
<p class="control"><label>Brillo <input type="range" id="brillo" min="1" max="8" step="0.1" value="1"></label></p>
<p class="control"><label>Contraste <input type="range" id="contraste" min="1" max="20" step="0.5" value="1"></label></p>
<p>Escribe lo que logres leer.</p>
""",
        script=JS_CONTRASTE,
        pista="Sube primero el brillo hasta 5 o 6 y luego el contraste, de a poco.",
    ),
    dict(
        tipo="clave", respuesta="cochayuyo", titulo="Nivel 8 · Lo invisible", mec="Texto invisible",
        cuerpo=lambda d: """
<p>Aquí no hay nada. Revisa bien: ni un solo dato, ni una sola pista, ni una sola alga.</p>
<p><span class="invisible">Sí había algo: la clave de este nivel es cochayuyo.</span></p>
<p>Nada de nada. Sigue buscando.</p>
""",
        pista="No toda la tinta se ve. Prueba seleccionando todo el texto de la página (Ctrl+A).",
    ),
    dict(
        tipo="libre", llave="escalera", titulo="Nivel 9 · El edificio", mec="Cambiar la dirección (URL)",
        sol="Entrar al edificio y cambiar el número en la URL (piso-1 → piso-7)",
        cuerpo=lambda d: """
<p>En este edificio los pisos no se ven. Se <em>recorren</em>.</p>
<p>Tiene un ascensor muy particular: no tiene botones, solo direcciones.</p>
<p style="text-align:center"><a class="boton" href="piso-1.html">Entrar al edificio</a></p>
""",
        pista="Dentro verás «piso-1.html» en la barra de direcciones. Cambia el número a mano.",
        extras=lambda d: {
            **{f"piso-{n}.html": (f"Piso {n}" if n else "Sótano", f'<div class="nivel"><p>{t}</p></div>') for n, t in PISOS.items()},
            "piso-7.html": ("Azotea", f'<div class="nivel"><p>Azotea. El viento sopla fuerte y el cielo está despejado. Hay una salida.</p>'
                            f'<p style="text-align:center"><a class="boton" href="{d}">Salir</a></p></div>'),
        },
    ),
    dict(
        tipo="clave", respuesta="huemul", titulo="Nivel 10 · Transmisión", mec="Morse con audio",
        cuerpo=lambda d: """
<p>Una señal llega desde la Patagonia cada noche. Escúchala (o mira la luz: si no puedes oír, también parpadea).</p>
<div id="lampara" class="lampara" aria-hidden="true"></div>
<p style="text-align:center"><button type="button" id="reproducir">▶ Reproducir</button></p>
<p>Anota la palabra. Es un ciervo muy escaso que figura en el escudo del país.</p>
""",
        script=JS_MORSE.replace("__MORSE__", morse_ascii("huemul")),
        pista="Punto = pitido corto, raya = pitido largo. Las pausas largas separan letras: es código Morse.",
    ),
    dict(
        tipo="clave", respuesta="sopaipilla", titulo="Nivel 11 · Base", mec="Base64",
        cuerpo=lambda d: f"""
<p>Los ordenadores se llevan mejor con una base que con una receta. Esta clave fue guardada en base sesenta y cuatro.</p>
<div class="codigo">{base64.b64encode(b"sopaipilla").decode()}</div>
<p>Cuando llueve, es la mejor compañera del pebre.</p>
""",
        pista="Busca un decodificador de Base64; no hace falta instalar nada.",
    ),
    dict(
        tipo="libre", llave="cruz", titulo="Nivel 12 · El cielo del sur", mec="Clic en un elemento diminuto de una imagen",
        sol="Hacer clic en la quinta estrella, la tenue de la Cruz del Sur",
        cuerpo=lambda d: svg_cielo(d) + """
<p>El cielo del sur guía a los navegantes con una cruz de cuatro estrellas brillantes. Dicen que tiene una quinta, tan débil que casi no existe.</p>
<p>Este nivel no tiene recuadro: la salida es un astro.</p>
""",
        pista="La quinta estrella está cerca de la cruz. Pasa el cursor hasta que cambie de forma.",
    ),
    dict(
        tipo="clave", respuesta="copihue", titulo="Nivel 13 · Poema", mec="Acróstico",
        cuerpo=lambda d: """
<p>Un poeta anónimo dejó estos versos. Léelos con paciencia: lo importante siempre empieza antes que el resto.</p>
<div class="verso">
<p>Cuelga entre la sombra del bosque austral,<br>
Orna con su rojo la lluvia del sur,<br>
Pétalo a pétalo, campana sin sonido,<br>
Invierno afuera y ella florece igual,<br>
Hilo de enredadera, trepa sin apuro,<br>
Uno la ve y se queda sin palabras,<br>
Es la flor que todo Chile reconoce.</p>
</div>
""",
        pista="Mira la primera letra de cada línea.",
    ),
    dict(
        tipo="libre", llave="chaito", titulo="Nivel 14 · La puerta", mec="Escribir una palabra sin recuadro",
        sol="Escribir «chaito» con el teclado en cualquier parte de la página",
        cuerpo=lambda d: SVG_PUERTA + """
<p>No hay cerradura, ni botón, ni recuadro. Esta puerta escucha.</p>
<p>Se abre con lo último que se dice antes de irse, con cariño y en diminutivo. Seis letras.</p>
<p id="estado" class="parpadeo">▮</p>
""",
        script=JS_TECLADO,
        pista="Haz clic en la página y simplemente escribe la palabra, sin enter.",
    ),
    dict(
        tipo="clave", respuesta=str(VENTANAS), titulo="Nivel 15 · Noche en la ciudad", mec="Contar elementos en una imagen",
        cuerpo=lambda d: EDIFICIO_SVG + """
<p>Un edificio de oficinas a las tres de la madrugada. En algunas oficinas todavía hay alguien trabajando.</p>
<p>¿Cuántas ventanas están encendidas? Escribe el número.</p>
""",
        pista="Son ventanas amarillas. Cuenta con calma, fila por fila.",
    ),
    dict(
        tipo="libre", llave="bodega", titulo="Nivel 16 · Los robots", mec="Archivo robots.txt",
        sol="Abrir robots.txt cambiando la dirección y seguir hasta bodega-trasera.html",
        cuerpo=lambda d: """
<p>Hay un archivo que todos los sitios tienen para hablar con los robots que los visitan. Las personas casi nunca lo leen.</p>
<p>Nadie lo enlaza. Se llega a él cambiando la dirección.</p>
""",
        pista="El archivo se llama robots.txt y vive en la misma carpeta que esta página.",
        archivos={"robots.txt": "# Archivo para robots. Los humanos no deberían leer esto.\n# (Las rutas son relativas a esta carpeta.)\nUser-agent: *\nDisallow: /bodega-trasera.html\n"},
        extras=lambda d: {
            "bodega-trasera.html": ("Bodega trasera",
                                    f'<div class="nivel"><p>Bodega trasera. Cajas apiladas, olor a encierro. Nadie debía llegar hasta aquí.</p>'
                                    f'<p style="text-align:center"><a class="boton" href="{d}">Seguir</a></p></div>')
        },
    ),
    dict(
        tipo="clave", respuesta="andes", titulo="Nivel 17 · Dibujos", mec="Rebus de emojis",
        cuerpo=lambda d: """
<p>Cinco dibujos. Cada uno empieza con una letra. Júntalas en orden.</p>
<div class="enigma">⚓ ☁️ 🎲 🐘 ☀️</div>
<p>Pista de contexto: la palabra es lo que une a este país con sus vecinos.</p>
""",
        pista="Di el nombre de cada dibujo en español y quédate con la inicial: ancla, nube...",
    ),
    dict(
        tipo="clave", respuesta="lejania", titulo="Nivel 18 · Abajo", mec="Scroll largo",
        form_arriba=True,
        cuerpo=lambda d: """
<p>La clave de este nivel está al final de esta página. Muy al final.</p>
<div class="largo"><p>sigue bajando</p><p>sigue bajando</p><p>aún no</p><p>más abajo</p><p>sigue</p></div>
<p class="diminuto">Lo lograste. La clave es: lejania</p>
""",
        pista="La barra de desplazamiento te dice cuánto falta. Usa la tecla Fin si te cansas.",
    ),
    dict(
        tipo="clave", respuesta="luciernaga", titulo="Nivel 19 · La linterna", mec="Linterna (mover el cursor)",
        cuerpo=lambda d: """
<p>Es de noche y no tienes luz. Solo tu linterna, que sigue al cursor (o a tu dedo).</p>
<div id="linterna" class="linterna"><div class="capa">
<span style="left:6%;top:12%">nada por aquí</span>
<span style="left:62%;top:20%">tampoco</span>
<span style="left:14%;top:58%">sigue buscando</span>
<span style="left:55%;top:70%">la clave es: luciernaga</span>
<span style="left:30%;top:86%">frío, frío</span>
</div></div>
""",
        script=JS_LINTERNA,
        pista="Recorre toda la caja negra con el cursor. Hay una frase escondida en cada rincón.",
    ),
    dict(
        tipo="clave", respuesta="pehuen", titulo="Nivel 20 · Números", mec="Números por letra (A=1)",
        cuerpo=lambda d: f"""
<p>Los antiguos del sur guardaban este nombre, y sus piñones alimentaron a un pueblo entero. Hoy está escrito con números.</p>
<div class="codigo">{numeros("pehuen")}</div>
<p>Cada número es una letra. A es el 1.</p>
""",
        pista="A=1, B=2, C=3... El árbol es la araucaria.",
    ),
    dict(
        tipo="clave", respuesta="vacio", titulo="Nivel 21 · La puerta que no existe", mec="Página de error 404",
        cuerpo=lambda d: """
<p>Hay una puerta al final de este pasillo. Dicen que no existe.</p>
<p>Lo que no existe también dice cosas.</p>
<p style="text-align:center"><a class="boton" href="puerta-inexistente.html">Abrir la puerta</a></p>
""",
        pista="Se abre y da error. Mira la pestaña del navegador. (Solo funciona en el sitio publicado, no abriendo el archivo local.)",
    ),
    dict(
        tipo="clave", respuesta="punta arenas", titulo="Nivel 22 · El espejo", mec="Texto reflejado",
        cuerpo=lambda d: """
<p>Algo quedó reflejado en un espejo roto. Ponte frente a él.</p>
<div class="enigma"><span class="espejo">PUNTA ARENAS</span></div>
<p>Escribe lo que dice el reflejo. (Es la ciudad más austral del continente con más de cien mil habitantes.)</p>
""",
        pista="Lee las letras al revés de derecha a izquierda, o ponle un espejo a la pantalla.",
    ),
    dict(
        tipo="libre", llave="espera", titulo="Nivel 23 · Paciencia", mec="Esperar",
        sol="Esperar unos 45 segundos en la página",
        cuerpo=lambda d: f"""
<p>Aquí no ocurre nada. Todavía.</p>
<p class="parpadeo">▮</p>
<p id="salida" hidden style="text-align:center"><a class="boton" href="{d}">Seguir</a></p>
""",
        script=JS_ESPERA,
        pista="Los conspiradores saben esperar. No toques nada y vuelve en un minuto.",
    ),
    dict(
        tipo="libre", llave="agente", titulo="Nivel 24 · Zona restringida", mec="Parámetro en la URL",
        sol="Agregar ?agente=2004 a la dirección (año en que nació Notpron)",
        cuerpo=lambda d: f"""
<p>Solo pasan los agentes autorizados. Tu identificador debe viajar en la dirección.</p>
<p id="estado">Verificando credenciales...</p>
<p id="salida" hidden style="text-align:center"><a class="boton" href="{d}">Pasar</a></p>
""",
        script=JS_AGENTE.replace("__HASH__", clave("2004")),
        pista="Agrega ?agente= al final de la dirección. El valor es el año en que nació el juego que inspiró este sitio (Notpron).",
    ),
    dict(
        tipo="libre", llave="senda", titulo="Nivel 25 · Sin formulario", mec="Enlace escondido",
        sol="Hacer clic en el punto al final de la frase",
        cuerpo=lambda d: f"""
<p>Esta vez no hay recuadro para escribir. Este nivel no se responde: se <em>encuentra</em>.</p>
<p>Los conspiradores jamás ponen un botón que diga «siguiente». Esconden la salida donde ya estás mirando, tan pequeña que se confunde con el final de una frase<a class="punto-oculto" href="{d}">.</a></p>
<p>Prueba pasar el cursor por cada rincón del texto.</p>
""",
        pista="Todas las frases terminan con algo. ¿Todas?",
    ),
    dict(
        tipo="clave", respuesta="conspiracion", titulo="Nivel 26 · Anagrama final", mec="Anagrama final",
        cuerpo=lambda d: f"""
<p>La última puerta. Ordena las letras y sabrás cómo se llama lo que has estado haciendo todo este tiempo.</p>
<div class="enigma">{revolver("conspiracion", 7)}</div>
<p>Es también el nombre de este sitio.</p>
""",
        pista="Doce letras. Empieza con C y termina en N. Es lo que se teje en las sombras.",
    ),
]


# ------------------------------------------------------------ plantillas
def pagina(titulo, cuerpo, pie="", script=""):
    sc = f"<script>{script}</script>\n" if script else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{html.escape(titulo)} — conspiracion.cl</title>
<link rel="stylesheet" href="css/estilo.css">
<link rel="stylesheet" href="css/extra.css">
</head>
<body>
<main>
{cuerpo}
<p class="pie">conspiracion.cl · recreación fan · inspirado en Notpron {pie}</p>
</main>
<script src="js/juego.js"></script>
{sc}</body>
</html>
"""


def llave(n):
    return n["respuesta"] if n["tipo"] == "clave" else n["llave"]


def archivo_de(k):
    return "inicio.html" if k == 0 else f"{clave(llave(NIVELES[k - 1]))}.html"


def siguiente_de(k):
    return "fin.html" if k == len(NIVELES) - 1 else archivo_de(k + 1)


def form_html(n, dest):
    return f"""<form id="form-clave" data-esperado="{clave(n["respuesta"])}" data-destino="{dest}" autocomplete="off">
<input type="text" id="clave" placeholder="escribe la clave" aria-label="clave">
<button type="submit">Entrar</button>
<p id="mensaje" role="status"></p>
</form>"""


def pagina_nivel(k):
    n = NIVELES[k]
    dest = siguiente_de(k)
    cuerpo = n["cuerpo"](dest)
    partes = [f'<h1>{html.escape(n["titulo"])}</h1>', f'<h2>Nivel {k + 1} de {len(NIVELES)}</h2>']
    formulario = form_html(n, dest) if n["tipo"] == "clave" else ""
    if n.get("form_arriba"):
        partes.append(formulario)
    partes.append(f'<div class="nivel">{cuerpo}</div>')
    if not n.get("form_arriba"):
        partes.append(formulario)
    partes.append(f'<details><summary>¿Necesitas una pista?</summary><p>{html.escape(n["pista"])}</p></details>')
    script = n.get("script", "").replace("__DEST__", dest)
    return pagina(n["titulo"], "\n".join(partes), pie=f"· nivel {k + 1}/{len(NIVELES)}", script=script)


def portada():
    cuerpo = f"""<div class="ojo">{OJO}</div>
<h1>conspiracion.cl</h1>
<h2>El juego de misterio chileno</h2>
<div class="nivel">
<p>Este es un juego en línea de misterio que invita a sus seguidores a jugar resolviendo anagramas y acertijos.</p>
<p>Desafía tu ingenio y tu capacidad para navegar, encontrando las pistas y, finalmente, la gran clave que te permite seguir avanzando.</p>
<p>Hay {len(NIVELES)} niveles. Cada uno esconde la clave, o la dirección, que abre la puerta al siguiente. No hay cuentas, no hay trampas: solo tú y tu cabeza.</p>
<p><strong>Reglas:</strong> las claves se escriben sin importar mayúsculas ni tildes. Mirar el código fuente, abrir las imágenes, revisar la barra de direcciones y la consola del navegador está permitido; a veces es obligatorio. Casi nada es lo que parece.</p>
</div>
<p style="text-align:center"><a class="boton" href="inicio.html">Comenzar</a></p>"""
    return pagina("Inicio", cuerpo)


def pagina_fin():
    cuerpo = """<h1>Fin del camino</h1>
<h2>Has llegado hasta el final</h2>
<div class="nivel">
<p>Felicitaciones. Resolviste todos los niveles y, con ello, ya sabes cómo piensa quien arma una conspiración.</p>
<p>Si llegaste hasta aquí sin ayuda, perteneces a un grupo muy reducido de gente paciente y curiosa.</p>
<p>Ahora te toca a ti: diseña un nivel, esconde una clave y pásasela a alguien.</p>
</div>
<p style="text-align:center"><a class="boton" href="index.html">Volver al inicio</a></p>"""
    return pagina("Fin", cuerpo)


def pagina_404(css):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>vacío — Error 404</title>
<style>{css}</style>
</head>
<body>
<main>
<h1>Error 404</h1>
<h2>No hay nada aquí</h2>
<div class="nivel"><p>Lo que buscabas no existe, o ya no existe, o nunca existió.</p>
<p>Esto es lo que queda cuando todo se ha ido.</p></div>
<p class="pie">conspiracion.cl · recreación fan</p>
</main>
</body>
</html>
"""


def leeme():
    filas = "\n".join(
        f"| {i + 1} | {n['mec']} | {n.get('sol') or ('Clave: ' + n['respuesta'])} |" for i, n in enumerate(NIVELES))
    return f"""# conspiracion.cl (recreación)

Juego de misterio estático (HTML + CSS + JS, sin backend), al estilo de Notpron.

**Jugar:** abre `index.html` en el navegador, o sube la carpeta a cualquier hosting estático (GitHub Pages, Netlify, etc.).
El nivel 21 usa la página de error 404, por lo que solo funciona en un hosting que sirva `404.html` (como GitHub Pages), no abriendo el archivo local.

## Cómo funciona
- Cada nivel es un archivo `.html`. El nombre del archivo del nivel siguiente es un hash de la clave del nivel actual.
- `js/juego.js` normaliza lo que escribes (sin mayúsculas ni tildes), calcula el hash y, si coincide, te lleva al siguiente nivel.
- Algunos niveles no usan recuadro: la salida es un enlace escondido, un cambio de dirección, un parámetro en la URL, una palabra escrita con el teclado o esperar.
- No hay servidor ni base de datos. Las claves no están en texto plano, pero no es seguridad real: alguien que sepa de programación puede saltarse niveles.

## Spoilers (solo para el creador)
| Nivel | Mecánica | Solución |
|---|---|---|
{filas}

## Agregar o cambiar niveles
Edita la lista `NIVELES` en `gen/build.py` y ejecuta `python3 -I gen/build.py .` desde la raíz del repo. Regenera todas las páginas con los enlaces encadenados.

---
Recreación hecha con Claude, 2026.
"""


def main():
    # limpiar salida anterior
    for p in OUT.glob("*.html"):
        p.unlink()
    for p in (OUT / "img").glob("*") if (OUT / "img").exists() else []:
        p.unlink()
    (OUT / "robots.txt").unlink(missing_ok=True)
    (OUT / "img").mkdir(parents=True, exist_ok=True)

    (OUT / "index.html").write_text(portada(), encoding="utf-8")
    (OUT / "fin.html").write_text(pagina_fin(), encoding="utf-8")
    css = (OUT / "css" / "estilo.css").read_text(encoding="utf-8") + (OUT / "css" / "extra.css").read_text(encoding="utf-8")
    (OUT / "404.html").write_text(pagina_404(css), encoding="utf-8")

    nombres = []
    for k, n in enumerate(NIVELES):
        nombres.append(archivo_de(k))
        (OUT / archivo_de(k)).write_text(pagina_nivel(k), encoding="utf-8")
        for ruta, contenido in n.get("assets", {}).items():
            (OUT / ruta).write_text(contenido, encoding="utf-8")
        for ruta, contenido in n.get("archivos", {}).items():
            (OUT / ruta).write_text(contenido, encoding="utf-8")
        if "extras" in n:
            for nombre, (titulo, cuerpo) in n["extras"](siguiente_de(k)).items():
                (OUT / nombre).write_text(pagina(titulo, f"<h1>{html.escape(titulo)}</h1>\n{cuerpo}"), encoding="utf-8")
    assert len(set(nombres)) == len(nombres)
    claves = [normalizar(llave(n)) for n in NIVELES]
    assert len(set(claves)) == len(claves), "claves repetidas"

    for n in NIVELES:
        if n["titulo"].split("·")[-1].strip() == "Anagrama" or "Anagrama final" in n["titulo"]:
            c = n["cuerpo"]("")
            letras = c.split('class="enigma">')[1].split("</div>")[0].replace(" ", "")
            assert sorted(letras.lower()) == sorted(n["respuesta"]), (letras, n["respuesta"])
            print("anagrama ok:", letras, "->", n["respuesta"])
    (OUT / "LEEME.md").write_text(leeme(), encoding="utf-8")
    print("ventanas encendidas:", VENTANAS)
    print("niveles:", len(NIVELES))

    ruta = [{"archivo": archivo_de(k), "dest": siguiente_de(k), "tipo": n["tipo"], "llave": llave(n),
             "respuesta": n.get("respuesta")} for k, n in enumerate(NIVELES)]
    Path("/tmp/ruta.json").write_text(json.dumps(ruta), encoding="utf-8")


if __name__ == "__main__":
    main()
