# Guia de Contribucion

## Proceso de Code Review

### 1. Crear una rama

Crea una rama desde `main` con un nombre descriptivo:

```bash
git checkout main
git pull origin main
git checkout -b feature/descripcion-del-cambio
```

Convenciones de nombres para ramas:
- `feature/` — nuevas funcionalidades
- `fix/` — correcciones de bugs
- `style/` — cambios visuales o de CSS
- `docs/` — documentacion

### 2. Hacer commits claros

Escribe mensajes de commit descriptivos:

```
Agregar selector de cantidad para items de catering
Corregir layout de impresion en dispositivos moviles
```

### 3. Abrir un Pull Request

- Abre un PR hacia la rama `main`
- Completa la plantilla del PR con toda la informacion requerida
- Asigna al menos un revisor

### 4. Revision del codigo

El revisor debe verificar:

- **Funcionalidad**: Los cambios hacen lo que se espera
- **Compatibilidad**: Funciona en movil, tablet y desktop
- **Impresion**: La vista de impresion no se rompe
- **Rendimiento**: No se agregan dependencias innecesarias
- **Seguridad**: No se expone informacion sensible
- **Legibilidad**: El codigo es claro y facil de entender

### 5. Comentarios y aprobacion

- Si hay cambios requeridos, el autor los corrige y solicita re-review
- Se necesita al menos **1 aprobacion** para hacer merge
- El autor del PR es responsable de hacer merge despues de la aprobacion

## Estandares de codigo

### HTML
- Usar indentacion de 2 espacios
- Atributos en minusculas
- Cerrar todos los tags

### CSS
- Preferir clases descriptivas (`.delivery-header` en vez de `.dh`)
- Usar variables CSS para colores y fuentes recurrentes
- Mantener los media queries agrupados al final

### JavaScript
- Usar `const` y `let`, nunca `var`
- Nombres de funciones descriptivos en camelCase
- Evitar codigo inline en el HTML cuando sea posible

## Pruebas manuales

Antes de abrir un PR, verifica:

1. Abrir `index.html` en el navegador
2. Llenar todos los campos del formulario
3. Verificar que el codigo de barras y QR se generen
4. Probar la funcion de impresion (Ctrl+P)
5. Verificar en vista movil (DevTools responsive)
