"""Contrato revisado de la versión documental 1.0: nombres, condiciones y firmas.

No contiene documentos. La fuente de las validaciones se recupera de Qdrant.
"""

CATEGORY_FIELDS = {
    "microservicio": {
        "microservicio": "Siempre",
        "repositorio": "Siempre",
        "version_actual / version_objetivo": "Siempre",
        "artefacto": "Siempre",
        "identificador_inmutable": "Antes de ejecutar el despliegue",
        "dependencias": "Siempre",
        "cambio_datos / compatibilidad": "Si cambia un contrato o datos",
        "pruebas_y_reversion": "Siempre",
    },
    "azure": {
        "tipo_servicio / recurso": "Siempre",
        "suscripcion / grupo_recursos / region": "Siempre",
        "configuracion_actual": "Siempre",
        "configuracion_propuesta": "Siempre",
        "dependencias / efecto": "Siempre",
        "referencias_credenciales": "Si intervienen secretos o certificados",
        "criterio_prueba": "Siempre",
    },
    "red": {
        "origen / ambiente_origen": "Siempre",
        "destino / ambiente_destino": "Siempre",
        "nombre_dns": "Si se utiliza resolución de nombres",
        "protocolo / puerto_destino": "Siempre",
        "puerto_origen": "Al definir la regla ejecutable",
        "sentido / finalidad": "Siempre",
        "punto_control / regla": "Antes de ejecutar",
        "regla_anterior / reversion": "Siempre",
    },
    "identidad": {
        "tenant / nombre_identidad": "Siempre",
        "consumidor / finalidad": "Siempre",
        "identidad_nueva / existente": "Siempre",
        "client_id / object_id": "Si existe la identidad",
        "mecanismo_autenticacion": "Siempre",
        "confianza_o_certificado": "Según el mecanismo",
        "destino / tipo_autorizacion": "Siempre",
        "rol_y_alcance": "Siempre",
        "pruebas / revocacion": "Siempre",
    },
}

RULE_SIGNATURES = {
    "OCD-C01": "1a9a9c7b0a563012884570ab19b433732642e69d7983044d6dd3438399c65bed",
    "OCD-C02": "7399ac4c5a8ea26d935ed3d5909f98aab0c83d7da1803bc2ded5e184ef0f61ff",
    "OCD-C03": "fa519f398f3c18001e4dde3a6918610ebf98311da12f37001df0609319dc55ba",
    "OCD-C04": "d474463cb2f3ff84eb57491b049668815a3de4b251c22148ed63197313cf6111",
    "OCD-C05": "e0d11d776def53acd8271a380cbccf1c0326fb8dc7246f736ac88821728f231a",
    "OCD-C06": "b77f64162e92ad3f2699f0f6fd6229dc59223356afd8fde0cbd5cee8af3d8a59",
    "MIC-R01": "44fde4c4da5f591e7d568830daaff6bb1051f462b7d1d19f9d4987af64c88db3",
    "MIC-R02": "5f394e91db6c0d26553c4bb98b19645541099ce6fb6d4dd987597df56c1eeb44",
    "MIC-R03": "50005bb2f77503207fe8cf694b57e21c90341bb83462e4c36b1940df452313de",
    "MIC-R04": "e8660dd22e199786469d74c86e9b028222f7dc05e8bbc20e85d8e47bd2a0cbf2",
    "MIC-R05": "4f7855d9845ab17ec0b73cc0bf93439991b3eb1077f3012f029b294bd7d22de3",
    "AZ-R01": "ada5937a44f33ff0ecc8465403530509ded47fcd5a37c6c10e9075ee9bae598f",
    "AZ-R02": "63ed5b75b44f75ee71e1e0a2e733091cb7ba3aee15bcf5c4da149b59463989ac",
    "AZ-R03": "77a0594dd0a3cc3422ddc2f3499b88f184a2d7c1d1b484e9d5b7c54b254f5ef7",
    "AZ-R04": "23a27630212f357db46e7df994a11dedf7ca7c7343ff10653d691c9deecd1dee",
    "AZ-R05": "0fb2c8f38d86f4ef0f1f6c27f521cac2405be231a6eade9430df300ba687402b",
    "RED-R01": "84ac7baa2e498eef1a5438e08a91da16fa108f31f65a8e70387381dc34ba43c8",
    "RED-R02": "b02eab4457b88d73bef30788798bd718ac2ebfce57c7bfee6509106117c133fe",
    "RED-R03": "8ea5db0092fc241153a9e1e4831509b10957b85f2a5b49187bacb86f73f149fd",
    "RED-R04": "6a08bdf147610fa8ab4c2ee0bbfbaddfdc0695a61af6d9a2432b3a86fc4bfef4",
    "RED-R05": "e3fd159dc825b84ded2924559273dda706f3552e095404acc286e1915f095327",
    "ID-R01": "8e69c757881183f48bdc2a976fa43ab397f3f7500829194151a374aab134f46f",
    "ID-R02": "d8c96464dc9586051f2bb84f4774936c6e64950a71761a9f8b85d87df55fa8dd",
    "ID-R03": "877bc05bbe7d26fc56193551cd263ecce7636fc1a76c0efc7f85d60e26435c70",
    "ID-R04": "ee8a85167cf5a796a651f853a9ad0a270187148c7d0ed002f60d67e43fb4a0ea",
    "ID-R05": "a28086470d336b437af5e63b0c5af930b607acce49a61b50e3680a98a8a18d5d",
}

RULE_IDS = {
    "comun": ["OCD-C01", "OCD-C02", "OCD-C03", "OCD-C04", "OCD-C05", "OCD-C06"],
    "microservicio": ["MIC-R01", "MIC-R02", "MIC-R03", "MIC-R04", "MIC-R05"],
    "azure": ["AZ-R01", "AZ-R02", "AZ-R03", "AZ-R04", "AZ-R05"],
    "red": ["RED-R01", "RED-R02", "RED-R03", "RED-R04", "RED-R05"],
    "identidad": ["ID-R01", "ID-R02", "ID-R03", "ID-R04", "ID-R05"],
}

SOURCE_PAGES = {
    "comun": ("MO-OCD-000", "66048"),
    "microservicio": ("MO-MIC-001", "294922"),
    "azure": ("MO-AZ-001", "131339"),
    "red": ("MO-RED-001", "98314"),
    "identidad": ("MO-ID-001", "294943"),
}
