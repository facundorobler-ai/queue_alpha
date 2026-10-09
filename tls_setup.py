"""Configura Python para verificar HTTPS usando el almacén de certificados del sistema.

En Windows, esto hace que Python utilice el almacén de confianza nativo, como
lo hace Schannel en curl.exe. No desactiva la validación de certificados.
"""
import truststore

truststore.inject_into_ssl()
