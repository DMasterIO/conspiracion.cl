# conspiracion.cl (recreación)

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
| 1 | Código fuente | Clave: fuente |
| 2 | Anagrama | Clave: cordillera |
| 3 | Acertijo | Clave: chile |
| 4 | Consola del navegador | Clave: murmullo |
| 5 | Nombre del archivo de una imagen | Clave: osorno |
| 6 | Cifrado César | Clave: valdivia |
| 7 | Imagen casi invisible (brillo y contraste) | Clave: chiloe |
| 8 | Texto invisible | Clave: cochayuyo |
| 9 | Cambiar la dirección (URL) | Entrar al edificio y cambiar el número en la URL (piso-1 → piso-7) |
| 10 | Morse con audio | Clave: huemul |
| 11 | Base64 | Clave: sopaipilla |
| 12 | Clic en un elemento diminuto de una imagen | Hacer clic en la quinta estrella, la tenue de la Cruz del Sur |
| 13 | Acróstico | Clave: copihue |
| 14 | Escribir una palabra sin recuadro | Escribir «chaito» con el teclado en cualquier parte de la página |
| 15 | Contar elementos en una imagen | Clave: 26 |
| 16 | Archivo robots.txt | Abrir robots.txt cambiando la dirección y seguir hasta bodega-trasera.html |
| 17 | Rebus de emojis | Clave: andes |
| 18 | Scroll largo | Clave: lejania |
| 19 | Linterna (mover el cursor) | Clave: luciernaga |
| 20 | Números por letra (A=1) | Clave: pehuen |
| 21 | Página de error 404 | Clave: vacio |
| 22 | Texto reflejado | Clave: punta arenas |
| 23 | Esperar | Esperar unos 45 segundos en la página |
| 24 | Parámetro en la URL | Agregar ?agente=2004 a la dirección (año en que nació Notpron) |
| 25 | Enlace escondido | Hacer clic en el punto al final de la frase |
| 26 | Anagrama final | Clave: conspiracion |

## Agregar o cambiar niveles
Edita la lista `NIVELES` en `gen/build.py` y ejecuta `python3 -I gen/build.py .` desde la raíz del repo. Regenera todas las páginas con los enlaces encadenados.

---
Recreación hecha con Claude, 2026.
