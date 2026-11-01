# Acceso a datos públicos del Estado desde la nube

**Fecha de la prueba:** 2026-10-14 · **Detalle por fuente:** `catalog/fuentes.yaml`

Se probó, desde una sesión en la nube, el acceso a portales del Estado de Chile y la **descarga
real** de una muestra de cada fuente útil para el procedimiento de riesgo poblacional
(`docs/metodologia_riesgo_poblacional.md`).

## Resultado general

| Situación | Fuentes |
|---|---|
| **Descarga verificada desde la nube** | INE (Censo 2024 completo, proyecciones comunales), MDSF (CASEN 2022 y 2024, pobreza comunal SAE), SII (empresas por comuna), MINVU (campamentos), DGA (derechos de agua), Minsal (defunciones semanales), ARClim, SISS (cuadros 2019 en datos.gob.cl) |
| **Bloqueado desde la nube; probar desde el laptop** | Sitio de SISS (`siss.gob.cl`), repositorio DEIS, `estadisticas.sii.cl`, `api.energiaabierta.cl`, mapas vectoriales de BCN, sitio principal del CR2 |
| **Pendiente de explorar** | Energía Abierta/CNE y SEC (consumo por comuna), SINIM, Banco Central |

## Lo que ya se puede usar

| Necesidad del procedimiento | Fuente verificada | Nivel | Nota |
|---|---|---|---|
| Población por edad (exposición) | **Censo 2024**, bucket público del INE | manzana → comuna | Suma 18.480.432 personas en 346 comunas, igual a la cifra oficial. La base por manzana trae 60+; para 65+ se usan los microdatos de personas (355 MB) |
| Población futura | **Proyecciones INE 2002-2035** | comuna × sexo × edad simple | Base Censo 2017 |
| Vivienda, hacinamiento, agua, saneamiento, combustibles, transporte, rama de empleo | **Censo 2024**, base por manzana | manzana → comuna | 212 variables. Cubre gran parte de la vulnerabilidad y del canal de dependencia de combustibles de la transición |
| Pobreza | **SAE 2024** (MDSF) | comuna | Con intervalo de confianza |
| Encuesta de hogares (gasto, ingreso, salud) | **CASEN 2022 y 2024** | región / urbano-rural | No representativa a nivel comunal |
| Empleo por rubro (canal laboral de la transición) | **SII** empresas por comuna y actividad | comuna | Requiere correspondencia con el CUT |
| Asentamientos precarios | **MINVU** catastro de campamentos | polígono con CUT | 2024: 1.432 campamentos |
| Agua: derechos y usos | **DGA** derechos concedidos (2025) | comuna | ~152 mil registros, CC BY |
| Mortalidad para la función calor-salud | **Minsal** defunciones semanales | región × edad × sexo | 2010-2026, CC0 |
| Amenaza climática | **ARClim** GeoJSON | comuna | 59 indicadores |

## Lo que falta y cómo resolverlo

| Brecha | Opción |
|---|---|
| **SISS reciente** (clientes, consumo y cobertura por empresa y comuna): el sitio rechaza conexiones desde la nube | Descargar desde el laptop y subir con `make push RUTA=raw/siss/<versión>`. El cuadro de datos.gob.cl está desactualizado (2019) |
| **Defunciones por comuna y causa** (DEIS): el repositorio responde 403 | Probar desde el laptop. Mientras tanto, la serie regional semanal del Minsal sirve para estimar la curva temperatura-mortalidad |
| **Consumo eléctrico y de combustibles por comuna** (CNE, SEC) | Explorar Energía Abierta desde el laptop; la API está bloqueada desde la nube |
| **Términos de uso**: la mayoría de las fuentes no declara licencia en el archivo | Revisar los términos de cada institución antes de publicar resultados |

## Comportamiento observado

- Las respuestas de datos.gob.cl a veces fallan con error 502 de forma intermitente: los conectores
  deben reintentar.
- Algunos sitios cargan sus enlaces con JavaScript (INE). La descarga se hace con la URL directa
  del archivo, que queda registrada en el catálogo.
- El INE publica el Censo 2024 en un bucket público
  (`storage.googleapis.com/bktdescargascenso2024`) que se puede listar y descargar sin
  credenciales.
