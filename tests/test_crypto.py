import base64
import os
import subprocess
from pathlib import Path

import pytest
from cryptography.exceptions import InvalidTag

from crypto import cifrado, firma, passwords


# --- AES-256-GCM ---
def test_cifrar_y_descifrar():
    assert cifrado.descifrar(cifrado.cifrar("hola ñandú", "x"), "x") == "hola ñandú"


def test_dos_cifrados_del_mismo_texto_son_distintos():
    assert cifrado.cifrar("igual", "x") != cifrado.cifrar("igual", "x")   # nonce aleatorio


def test_texto_cifrado_no_contiene_el_original():
    assert "secreto-visible" not in cifrado.cifrar("secreto-visible", "x")


def test_contexto_distinto_no_descifra():
    token = cifrado.cifrar("dato", "usuarios.correo")
    with pytest.raises(InvalidTag):
        cifrado.descifrar(token, "historial.nota")


def test_valor_alterado_no_descifra():
    crudo = bytearray(base64.b64decode(cifrado.cifrar("dato", "x")))
    crudo[-1] ^= 1
    with pytest.raises(InvalidTag):
        cifrado.descifrar(base64.b64encode(bytes(crudo)).decode(), "x")


def test_indice_ciego_es_estable_y_normaliza():
    assert cifrado.indice_ciego(" Ana@Ejemplo.com ") == cifrado.indice_ciego("ana@ejemplo.com")
    assert len(cifrado.indice_ciego("a@b.c")) == 64


def test_sin_clave_falla_con_mensaje_claro(monkeypatch):
    monkeypatch.delenv("ENCRYPTION_KEY")
    with pytest.raises(RuntimeError, match="ENCRYPTION_KEY"):
        cifrado.cifrar("x")


# --- contraseñas ---
def test_password_correcta_e_incorrecta():
    h = passwords.hashear("Clave-Segura-1")
    assert passwords.verificar("Clave-Segura-1", h)
    assert not passwords.verificar("otra", h)


def test_password_no_se_guarda_en_claro_y_usa_sal():
    h1, h2 = passwords.hashear("misma"), passwords.hashear("misma")
    assert "misma" not in h1 and h1 != h2


def test_hash_corrupto_no_verifica():
    assert not passwords.verificar("x", "basura")


# --- firma ---
def test_firma_valida_y_alterada():
    doc = b"%PDF contenido de prueba"
    sig = firma.firmar(doc)
    assert firma.verificar(doc, sig)
    assert not firma.verificar(doc + b"x", sig)


def test_firma_compatible_con_openssl(tmp_path):
    """Lo firmado por Python lo verifica el script verificar.sh (OpenSSL), y al revés."""
    doc = tmp_path / "doc.txt"
    doc.write_bytes(b"contenido")
    (tmp_path / "doc.txt.sig").write_bytes(firma.firmar(doc.read_bytes()))
    r = subprocess.run(["openssl", "dgst", "-sha256", "-verify", os.environ["PUBLIC_KEY_PATH"],
                        "-signature", str(tmp_path / "doc.txt.sig"), str(doc)],
                       capture_output=True, text=True)
    assert "Verified OK" in r.stdout

    sig2 = tmp_path / "otra.sig"
    subprocess.run(["openssl", "dgst", "-sha256", "-sign", os.environ["PRIVATE_KEY_PATH"],
                    "-out", str(sig2), str(doc)], check=True)
    assert firma.verificar(doc.read_bytes(), sig2.read_bytes())
