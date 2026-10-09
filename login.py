"""Ayudas para localizar y completar el formulario de ingreso."""
import os

from selenium.webdriver.common.by import By

from logging_utils import log


def completar_login(driver, nombre: str) -> bool:
    """Completa email y contraseña desde variables de entorno.

    Requiere BOCA_EMAIL y BOCA_PASSWORD definidos en la misma terminal desde
    la que se ejecuta Python. No envía el formulario ni presiona Enter.
    """
    email_configurado = os.getenv("BOCA_EMAIL")
    password_configurada = os.getenv("BOCA_PASSWORD")
    if not email_configurado or not password_configurada:
        log(
            f"⚠️ {nombre}: faltan BOCA_EMAIL o BOCA_PASSWORD; "
            "se omite el autocompletado."
        )
        return False

    try:
        log(f"🔑 {nombre}: buscando campos de ingreso...")
        campo_email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        campo_password = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

        campo_email.clear()
        campo_password.clear()
        campo_email.send_keys(email_configurado)
        campo_password.send_keys(password_configurada)

        log(f"✅ {nombre}: campos completados; revisá la página antes de continuar.")
        return True
    except Exception as exc:
        log(f"❌ {nombre}: no se pudieron completar los campos: {exc}")
        return False
