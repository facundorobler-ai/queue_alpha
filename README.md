# Boca Socios Monitor — estructura modular

Esta carpeta separa el programa en módulos para que cada parte se pueda probar y mantener de forma independiente.

## Archivos

- `main.py`: inicia el programa y coordina los componentes.
- `config.py`: URL e intervalos configurables.
- `state.py`: estado compartido entre hilos.
- `logging_utils.py`: mensajes en consola y archivo de log.
- `browsers.py`: creación de Chrome, incógnito y Edge.
- `queue_logic.py`: lectura del texto de página, estados e historial de tiempos.
- `monitor.py`: chequeo periódico y ranking.
- `notifications.py`: alertas sonoras/locales y notificaciones opcionales por Telegram.
- `telegram_get_chat_id.py`: obtiene el identificador de chat después de enviar `/start` al bot.
- `telegram_test.py`: envía un mensaje de prueba antes de usar el monitor.
- `login.py`: completa los campos si existen las variables de entorno `BOCA_EMAIL` y `BOCA_PASSWORD`.

## Ejecutar desde CMD con el entorno virtual

Desde la carpeta del proyecto:

```bat
call venv\Scripts\activate.bat
set "BOCA_CANTIDAD_POR_TIPO=1"
set "BOCA_EMAIL=tu_correo"
set "BOCA_PASSWORD=tu_contraseña"
python main.py
```

Cambiá `venv` por el nombre real de tu carpeta de entorno virtual. Los `set` afectan solamente esa ventana de CMD. Para iniciar con otro número de navegadores podés cambiar `BOCA_CANTIDAD_POR_TIPO`; para la primera prueba recomendamos `1` para minimizar consumo de recursos y confirmar que todo funcione.

Si Selenium no está instalado en el entorno virtual:

```bat
python -m pip install -r requirements.txt
```

## Seguridad de credenciales

No escribas credenciales reales en `config.py` ni las compartas en capturas o repositorios. Las variables de entorno reducen la exposición accidental, aunque no protegen frente a otros procesos o usuarios con acceso a la misma sesión. Como la contraseña apareció en el archivo original que compartiste, cambiála si era una contraseña real.

## Alcance actual

Esta etapa organiza el código. No agrega la integración de Telegram ni envía el formulario de login automáticamente. `login.py` solamente rellena los campos, igual que el programa original. Confirmá visualmente la página antes de continuar y respetá las condiciones del sitio.

## Configurar y probar Telegram (opcional)

1. En Telegram, hablá con `@BotFather`, ejecutá `/newbot` y guardá el token en privado. No lo envíes a nadie ni lo publiques en capturas.
2. En la misma ventana de CMD donde usás el entorno virtual, definí el token (reemplazá el valor de ejemplo):

```bat
set "BOCA_TELEGRAM_BOT_TOKEN=PEGAR_TOKEN_AQUI"
```

3. Abrí el chat de tu nuevo bot y enviá `/start`. Luego, en esa misma ventana de CMD, ejecutá:

```bat
python telegram_get_chat_id.py
```

4. Copiá el chat ID de tu conversación personal y configurá la variable: 

```bat
set "BOCA_TELEGRAM_CHAT_ID=PEGAR_CHAT_ID_AQUI"
python telegram_test.py
```

5. Si llega el mensaje de prueba, iniciá el monitor normalmente con `python main.py`, conservando las variables en esa misma ventana. Cuando el monitor detecte que un navegador vio la fila y luego llegó a una página de ingreso, enviará una notificación. No envía mensajes por cada lectura de minutos.

Si `telegram_get_chat_id.py` muestra `URLError`, esta versión informa el motivo de conexión sin mostrar el token. Las variables configuradas con `set` duran solo mientras esa ventana de CMD siga abierta. El token y el chat ID no se guardan en los archivos del proyecto. La integración agrega la dependencia `truststore` para que Python use el almacén nativo de certificados del sistema. Esto es útil si `curl.exe` conecta mediante Schannel, pero Python falla con `CERTIFICATE_VERIFY_FAILED`. La validación TLS permanece activada. Si Telegram no está configurado, el programa sigue funcionando con alertas locales.


## Corrección de certificados HTTPS en Windows

Si `telegram_get_chat_id.py` informa `CERTIFICATE_VERIFY_FAILED` y `curl.exe` se conecta sin error TLS, actualizá las dependencias desde la misma terminal y entorno virtual:

```bat
python -m pip install -r requirements.txt
```

Luego volvé a ejecutar `python telegram_get_chat_id.py`. El proyecto usa `truststore` para aprovechar el almacén de certificados de Windows; no desactiva la verificación TLS. Esta solución requiere Python 3.10 o posterior.
