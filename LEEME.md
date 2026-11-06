# conspiracion.cl (recreación)

Juego de misterio estático (HTML + CSS + JS, sin backend), al estilo de Notpron.

**Jugar:** abre `index.html` en el navegador, o sube la carpeta a cualquier hosting estático (GitHub Pages, Netlify, etc.).

## Cómo funciona
- Cada nivel es un archivo `.html`. El nombre del archivo del nivel siguiente es un hash de la respuesta del nivel actual.
- `js/juego.js` normaliza lo que escribes (sin mayúsculas ni tildes), calcula el hash y, si coincide, te lleva al siguiente nivel.
- No hay servidor ni base de datos. Las claves no están en texto plano, pero no es seguridad real: alguien que sepa de programación puede saltarse niveles.

## Spoilers (solo para el creador)
| Nivel | Tipo | Clave |
|---|---|---|
| 1 | Código fuente | fuente |
| 2 | Anagrama | cordillera |
| 3 | Acertijo | chile |
| 4 | César +3 | valdivia |
| 5 | Texto invisible | cochayuyo |
| 6 | Morse | pisco |
| 7 | Base64 | sopaipilla |
| 8 | Acróstico | copihue |
| 9 | A1Z26 | pehuen |
| 10 | Enlace oculto (el punto al final de la frase) | — |
| 11 | Anagrama final | conspiracion |

## Agregar o cambiar niveles
Edita la lista `NIVELES` en `gen/build.py` y ejecuta `python3 build.py <carpeta_salida>`. Regenera todas las páginas con los enlaces encadenados.

---
Recreación hecha con Claude, 2026.
