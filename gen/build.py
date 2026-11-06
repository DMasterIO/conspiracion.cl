#!/usr/bin/env python3
"""Genera las páginas de conspiracion-cl a partir de la lista de niveles.
Uso: python3 -I build.py <directorio_salida>"""
import base64
import html
import random
import sys
import unicodedata
from pathlib import Path

OUT = Path(sys.argv[1])
M32 = 0xFFFFFFFF


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
    if n == 0:
        return "0"
    r = ""
    while n:
        n, m = divmod(n, 36)
        r = d[m] + r
    return r


def clave(s):
    return b36(cyrb53(normalizar(s)))


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


def morse(t):
    return "  ".join(MORSE[c].replace(".", "·").replace("-", "−") for c in t.lower())


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

# ------------------------------------------------------------------ niveles
# tipo "clave": el jugador escribe la respuesta. tipo "enlace": la salida es un enlace oculto.
NIVELES = [
    dict(
        tipo="clave", respuesta="fuente",
        titulo="Nivel 1",
        cuerpo="""
<p>Bienvenido, agente. Lo que ves en pantalla es solo la mitad de la historia.</p>
<p>Todo sitio guarda más de lo que muestra. Aprende a mirar <em>detrás</em> de la página.</p>
<!-- Buen ojo. La clave de este nivel es: fuente -->
""",
        pista="Un clic derecho o Ctrl+U te acercan a lo que buscas.",
    ),
    dict(
        tipo="clave", respuesta="cordillera",
        titulo="Nivel 2 · Anagrama",
        cuerpo=lambda: f"""
<p>Las letras están desordenadas. Ordénalas y obtendrás aquello que recorre el país de norte a sur y que nadie cruza a la ligera.</p>
<div class="enigma">{revolver("cordillera", 11)}</div>
""",
        pista="Se alza al este de Santiago y se ve incluso con smog.",
    ),
    dict(
        tipo="clave", respuesta="chile",
        titulo="Nivel 3 · Acertijo",
        cuerpo="""
<p>Soy más larga que ancha, tan flaca que casi me parto por la cintura.</p>
<p>Al norte me seco, al sur me congelo; el mar me abraza por un lado y los Andes me guardan la espalda por el otro.</p>
<p>Los poetas dicen que soy «larga pétala de mar y vino y nieve». ¿Cómo me llamo?</p>
""",
        pista="Es la clave más corta de todo el juego, y el nombre de este dominio la delata (.cl).",
    ),
    dict(
        tipo="clave", respuesta="valdivia",
        titulo="Nivel 4 · Cifrado",
        cuerpo=lambda: f"""
<p>Un emperador romano mandaba mensajes corriendo cada letra del alfabeto unos pocos lugares. Tres, para ser exactos.</p>
<div class="codigo">{cesar("valdivia", 3)}</div>
<p>Al descifrarlo aparecerá una ciudad del sur, con ríos, lobos marinos y cervecerías.</p>
""",
        pista="La D se esconde detrás de la A. Retrocede tres lugares en cada letra.",
    ),
    dict(
        tipo="clave", respuesta="cochayuyo",
        titulo="Nivel 5 · Lo invisible",
        cuerpo="""
<p>Aquí no hay nada. Revisa bien: ni un solo dato, ni una sola pista, ni una sola alga.</p>
<p><span class="invisible">Sí había algo: la clave de este nivel es cochayuyo.</span></p>
<p>Nada de nada. Sigue buscando.</p>
""",
        pista="No toda la tinta se ve. Prueba seleccionando todo el texto de la página (Ctrl+A).",
    ),
    dict(
        tipo="clave", respuesta="pisco",
        titulo="Nivel 6 · Señales",
        cuerpo=lambda: f"""
<p>Un telegrafista captó esta transmisión. Se repite cada noche desde Elqui.</p>
<div class="codigo morse">{morse("pisco")}</div>
<p>Dos espacios separan las letras. Dinos qué se brinda.</p>
""",
        pista="Los puntos y las rayas del telégrafo: código Morse.",
    ),
    dict(
        tipo="clave", respuesta="sopaipilla",
        titulo="Nivel 7 · Base",
        cuerpo=lambda: f"""
<p>Los ordenadores se llevan mejor con una base que con una receta. Esta clave fue guardada en base sesenta y cuatro.</p>
<div class="codigo">{base64.b64encode(b"sopaipilla").decode()}</div>
<p>Cuando llueve, es la mejor compañera del pebre.</p>
""",
        pista="Busca un decodificador de Base64; no hace falta instalar nada.",
    ),
    dict(
        tipo="clave", respuesta="copihue",
        titulo="Nivel 8 · Poema",
        cuerpo="""
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
        tipo="clave", respuesta="pehuen",
        titulo="Nivel 9 · Números",
        cuerpo=lambda: f"""
<p>Los antiguos del sur guardaban este nombre, y sus piñones alimentaron a un pueblo entero. Hoy está escrito con números.</p>
<div class="codigo">{numeros("pehuen")}</div>
<p>Cada número es una letra. A es el 1.</p>
""",
        pista="A=1, B=2, C=3... El árbol es la araucaria.",
    ),
    dict(
        tipo="enlace", salida="senda",
        titulo="Nivel 10 · Sin formulario",
        cuerpo=lambda dest: f"""
<p>Esta vez no hay recuadro para escribir. Este nivel no se responde: se <em>encuentra</em>.</p>
<p>Los conspiradores jamás ponen un botón que diga «siguiente». Esconden la salida donde ya estás mirando, tan pequeña que se confunde con el final de una frase<a class="punto-oculto" href="{dest}">.</a></p>
<p>Prueba pasar el cursor por cada rincón del texto.</p>
""",
        pista="Todas las frases terminan con algo. ¿Todas?",
    ),
    dict(
        tipo="clave", respuesta="conspiracion",
        titulo="Nivel 11 · Anagrama final",
        cuerpo=lambda: f"""
<p>La última puerta. Ordena las letras y sabrás cómo se llama lo que has estado haciendo todo este tiempo.</p>
<div class="enigma">{revolver("conspiracion", 7)}</div>
<p>Es también el nombre de este sitio.</p>
""",
        pista="Doce letras. Empieza con C y termina en N. Es lo que se teje en las sombras.",
    ),
]

# ------------------------------------------------------------------ plantillas
def pagina(titulo, cuerpo, extra_pie=""):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{html.escape(titulo)} — conspiracion.cl</title>
<link rel="stylesheet" href="css/estilo.css">
</head>
<body>
<main>
{cuerpo}
<p class="pie">conspiracion.cl · recreación fan · inspirado en Notpron {extra_pie}</p>
</main>
<script src="js/juego.js"></script>
</body>
</html>
"""


def archivo_de(k):
    return "inicio.html" if k == 0 else f"{clave(NIVELES[k - 1].get('respuesta') or NIVELES[k - 1]['salida'])}.html"


def pagina_nivel(k):
    n = NIVELES[k]
    fin = k == len(NIVELES) - 1
    llave = n["respuesta"] if n["tipo"] == "clave" else n["salida"]
    siguiente = "fin.html" if fin else archivo_de(k + 1)
    cuerpo = n["cuerpo"]
    if n["tipo"] == "enlace":
        cuerpo = cuerpo(siguiente)
    elif callable(cuerpo):
        cuerpo = cuerpo()
    partes = [f'<h1>{html.escape(n["titulo"])}</h1>', f'<h2>Nivel {k + 1} de {len(NIVELES)}</h2>',
              f'<div class="nivel">{cuerpo}</div>']
    if n["tipo"] == "clave":
        partes.append(f"""<form id="form-clave" data-esperado="{clave(llave)}" data-destino="{siguiente}" autocomplete="off">
<input type="text" id="clave" placeholder="escribe la clave" autofocus aria-label="clave">
<button type="submit">Entrar</button>
<p id="mensaje" role="status"></p>
</form>""")
    partes.append(f'<details><summary>¿Necesitas una pista?</summary><p>{html.escape(n["pista"])}</p></details>')
    return pagina(n["titulo"], "\n".join(partes), extra_pie=f"· nivel {k + 1}/{len(NIVELES)}")


def portada():
    cuerpo = f"""<div class="ojo parpadeo-lento">{OJO}</div>
<h1>conspiracion.cl</h1>
<h2>El juego de misterio chileno</h2>
<div class="nivel">
<p>Este es un juego en línea de misterio que invita a sus seguidores a jugar resolviendo anagramas y acertijos.</p>
<p>Desafía tu ingenio y tu capacidad para navegar, encontrando las pistas y, finalmente, la gran clave que te permite seguir avanzando.</p>
<p>Cada nivel esconde la clave que abre la puerta al siguiente. No hay atajos, no hay cuentas, no hay trampas: solo tú y tu cabeza.</p>
<p><strong>Reglas:</strong> las claves se escriben sin importar mayúsculas ni tildes. Mirar el código fuente de la página está permitido, y a veces es obligatorio.</p>
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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(portada(), encoding="utf-8")
    (OUT / "fin.html").write_text(pagina_fin(), encoding="utf-8")
    for k in range(len(NIVELES)):
        (OUT / archivo_de(k)).write_text(pagina_nivel(k), encoding="utf-8")
    nombres = [archivo_de(k) for k in range(len(NIVELES))]
    assert len(set(nombres)) == len(nombres)
    # verificación de anagramas
    for n in NIVELES:
        if "Anagrama" in n["titulo"]:
            c = n["cuerpo"]()
            resp = n["respuesta"]
            letras = c.split('class="enigma">')[1].split("</div>")[0].replace(" ", "")
            assert sorted(letras.lower()) == sorted(resp), (letras, resp)
            print("anagrama ok:", letras, "->", resp)
    print("páginas:", nombres)


if __name__ == "__main__":
    main()
