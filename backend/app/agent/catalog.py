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
    "MIC-R01": "3d753d3c245565b18b9ad32f204b6b812f060e856c2ca2a4122013138b761439",
    "MIC-R02": "20bfe492cd457e497ef75f9efd301e2d7e1bd01a94ac7f5b73ca15290c3be9e0",
    "MIC-R03": "6c524dc4aa434957b4e1852710559f803e6d3973fdb9a30adb955ed7a7520a2d",
    "MIC-R04": "95a75bab3899707687c1d34bc86ebcec2c00739d365c8e6924ddb2828c41c207",
    "MIC-R05": "d37fff865f1476beee434563d16b72377734855bad790ca3f4b480f442f6cfde",
    "AZ-R01": "8e5ca78628e129a13271831fd38f285c28af678e819a244d410780e0940dac48",
    "AZ-R02": "bf64474774b707b2af207b82078edc3757d5e001625b55fa2bdea8a0ea0b3398",
    "AZ-R03": "1e65e157dad76cd0d8e313e0b20dee64ee15fa7c367ad73ca8924a8a36b94ac8",
    "AZ-R04": "000993428582b309007c9780930fac5ac4068c75b78fed00bcb2d775011f4918",
    "AZ-R05": "7056ceb64ca4c20408568a7218b78c802253a322b05409cdede5c44e6fb35736",
    "RED-R01": "f31a26de521121633a4024d3d7bbe11924e6b1d59ec42b88330f866eb87b1b08",
    "RED-R02": "57bab9d6225bcf90e29cf2bd7b800d2bae5599517f4e2bc644fac590edfc2402",
    "RED-R03": "e2ba73e981f907721fb86e6c9ccec0b31b0268988e550d742d06283f0a8b789b",
    "RED-R04": "68a1bab52ee4052b3b34a4fefe13a392a2feed75d42aa71a451668d9a48b1c45",
    "RED-R05": "2a69dd4231c4a844429ec15a923eb099556c45fe5cdac841c93c4ebe47ff09d3",
    "ID-R01": "95941458b7f17a18f7b41270a9c9f2750f040340bca1a2831a92822688ec5330",
    "ID-R02": "1e8baf2def27f805058887697c24ea0b23f47ebb1fa3bef4492b23d53d560756",
    "ID-R03": "0e0d7b6e21d48bd93e9706fa9df7291773a16cbd6f10485824f961da7f67d580",
    "ID-R04": "96ce9e439c2f35d069585ec015c985e38138a1f1261c0bb254ff9baeef7ec2ed",
    "ID-R05": "9e925e65e894fbda065649b1eeebb043edd984b0d773617c029493514f3e5b12",
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
