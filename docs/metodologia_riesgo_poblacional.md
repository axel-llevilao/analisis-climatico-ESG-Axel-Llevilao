# Procedimiento de cálculo de riesgo climático poblacional

**Estado:** borrador v0.1 para revisión · 2026-10-14
**Alcance:** riesgo físico, riesgo de transición y modelado de escenarios con **unidad de análisis
territorial (comuna, CUT)** y **sujeto de riesgo poblacional** (personas y hogares), usando datos
públicos. No modela empresas ni activos financieros.

Convención de verificación: **[V]** verificado en la web en esta sesión · **[NV]** no verificado
todavía (se verifica en el Módulo 2 antes de usarse en cálculos).

---

## 1. Punto de partida: qué hace la app "ESG Suite / Climato Suite" (zip recibido)

La app (React + Electron, generada en Google AI Studio) es una calculadora **corporativa**. Su lógica
de cálculo está en `src/lib/engine.ts`, `src/lib/arclim.ts`, `src/lib/calculators.ts` y
`src/data.ts`:

| Bloque | Qué calcula | Fórmula / supuesto |
|---|---|---|
| Amenaza física | Puntaje 1–5 por región y amenaza (inundación, calor, sequía, incendios) | Tabla fija `ARCLIM_ZONES` por región. El propio código la declara **"estimación cualitativa regional de referencia, inspirada en ARClim"**: no son datos de ARClim |
| Escalamiento por escenario | Ajusta la amenaza según el escenario y el horizonte | `escala = 1 + (T_escenario/2.4 − 1) × elasticidad`, con T tomada de IPCC AR6 Tabla SPM.1 y elasticidades por amenaza (calor 1.15, incendios 1.20…) |
| Riesgo físico de una instalación | Pérdida anual esperada (EAL) | `EAL = Valor activo × (Amenaza × Vulnerabilidad / 25) × Tasa de exposición` |
| Riesgo de transición | Índice 0–100 | Promedio de `Probabilidad × Impacto / 25` de una lista de riesgos cualitativos |
| Escenarios de transición | Trayectorias 2024–2050 | 16 presets (IEA WEO 2024, NGFS Fase V, SSP1–5) con precio del carbono, PIB, aprendizaje tecnológico, CCUS, etc. |
| Motor financiero | Emisiones, CAPEX, pasivo de carbono, WACC | Proyección anual con curvas S y precio de carbono interpolado linealmente |
| Inventario GEI y agua | Alcances 1, 2 y 3; huella hídrica azul, verde y gris | Factores de emisión fijos (FE SEN, combustibles) y ET_ref por macrozona |
| Coherencia de escenarios | Asigna a cada escenario de transición un escenario físico | NZE/NZ2050 → SSP1-1.9; STEPS/NDC → SSP2-4.5; CPS/CP → SSP5-8.5; FW → SSP3-7.0 |

### Qué se reutiliza

1. **El marco de tres componentes** (amenaza × exposición × vulnerabilidad), que coincide con
   ARClim e IPCC.
2. **La tabla de niveles de calentamiento** del IPCC AR6 WG1 Tabla SPM.1. Los valores 2041–2060
   (SSP1-2.6: 1.7 °C · SSP2-4.5: 2.0 °C · SSP5-8.5: 2.4 °C) coinciden con fuentes secundarias **[V,
   fuente secundaria; contrastar con el PDF del IPCC]**.
3. **La correspondencia entre escenarios físicos y de transición**, como punto de partida.
4. **El catálogo de escenarios NGFS Fase V**, en sus nombres y familias (ordenado, desordenado,
   mundo invernadero, demasiado poco y tarde) **[V]**.
5. **La idea de reportar el riesgo como métrica de impacto** (la EAL), y no solo como índice. Aquí se
   traduce a personas afectadas.

### Qué se corrige

| Problema en la app | Consecuencia | Corrección en este procedimiento |
|---|---|---|
| Puntajes de amenaza **inventados** por región (16 valores) | No hay variación comunal ni respaldo en datos | Usar indicadores reales: las capas comunales de ARClim o índices calculados desde CMIP6 regionalizado |
| Escalamiento lineal con **elasticidades sin fuente** (1.15, 1.20, 0.95…) atribuidas al "Cap. 11 AR6" | Resultados que parecen precisos pero son arbitrarios | Calcular la amenaza futura directamente desde las salidas de modelos por escenario. Si hay que escalar, usar niveles de calentamiento global (GWL) con su incertidumbre explícita |
| Escenario SSP4-3.4 con niveles 1.5/1.9/2.2 °C | **No aparece en la Tabla SPM.1** | Excluir, salvo que se encuentre una fuente primaria |
| Trayectorias de precio del carbono **escritas a mano** por escenario | No son trazables a la base NGFS | Descargar las series del NGFS Scenario Explorer (IIASA) y versionarlas |
| Inconsistencias internas: ET_ref Norte Grande 2.200 mm (código) vs 1.800 mm (referencias); FE SEN 0,2384 (código) vs 0,298 (referencias) | No reproducible | Cada parámetro vive en un único archivo con su fuente y su fecha |
| EAL = valor × (H·V/25) × tasa | Es un puntaje multiplicado por un valor, no una función de daño | Funciones de impacto con base empírica (p. ej., mortalidad por calor) o índices compuestos transparentes |
| Riesgo de transición = encuesta de probabilidad × impacto | Subjetivo y sin datos | Indicadores observables por comuna: empleo, gasto energético, combustibles |

---

## 2. Marco conceptual

### 2.1 Definición de riesgo

Se adopta el marco del IPCC AR6 WGII: el riesgo surge de la interacción entre **amenaza**,
**exposición** y **vulnerabilidad**. La vulnerabilidad combina **sensibilidad** y **capacidad
adaptativa**.

ARClim, el Atlas de Riesgos Climáticos del MMA, operacionaliza el riesgo como **R = A × E × S**
(amenaza × exposición × sensibilidad). La evalúa a nivel comunal, compara el clima histórico
1980–2010 con el futuro 2035–2065 bajo RCP8.5, y mantiene la exposición y la sensibilidad en su
condición actual, sin proyectar la capacidad adaptativa **[V]**
([Metodología ARClim](https://ARCLim.mma.gob.cl/media/learning/Metodologia_ARCLIM.pdf);
[Minuta a nivel comunal](https://cambioclimatico.mma.gob.cl/wp-content/uploads/2020/07/Minuta-Atlas-de-Riesgo-Climatico-a-Nivel-Comunal.pdf)).

Este procedimiento **extiende** ARClim en tres puntos:
1. agrega la **capacidad adaptativa** como componente explícito;
2. incluye **varios escenarios y horizontes**, no solo RCP8.5 a mediados de siglo;
3. incorpora el **riesgo de transición** desde la perspectiva de los hogares.

### 2.2 Unidades

| Dimensión | Unidad |
|---|---|
| Territorio | Comuna (CUT vigente) con tabla de correspondencia histórica (`ref/territorial/`) |
| Sujeto | Personas y hogares; subgrupos según el riesgo (≥65 años, <5 años, hogares rurales, etc.) |
| Tiempo | Línea base observada + horizontes AR6: cercano 2021–2040, medio 2041–2060, largo 2081–2100 |
| Escenarios físicos | SSP1-2.6, SSP2-4.5, SSP5-8.5 (mínimo dos) |
| Escenarios de transición | NGFS Fase V: Net Zero 2050, Below 2 °C, Delayed Transition, NDCs, Current Policies, Fragmented World |

### 2.3 Dos formas de expresar el riesgo (ambas obligatorias)

1. **Índice compuesto** (0–1), para comparar comunas y priorizar.
2. **Métrica de impacto en unidades físicas**, para dimensionar el problema. Es el equivalente
   poblacional de la EAL de la app:
   - personas expuestas (p. ej., población en zona inundable);
   - persona-días de exposición (p. ej., personas ≥65 × días de calor extremo al año);
   - impacto en salud cuando exista una función dosis-respuesta publicada (p. ej., mortalidad
     atribuible al calor).

---

## 3. Procedimiento de riesgo físico

### Paso F1. Seleccionar las cadenas de impacto

Se parte con cadenas en las que el sujeto es la población. Las fuentes de cada componente se
catalogan y verifican en el Módulo 2.

| Cadena | Amenaza | Exposición | Sensibilidad | Capacidad adaptativa | Métrica de impacto |
|---|---|---|---|---|---|
| **Calor y salud** | Días con Tmáx > umbral; olas de calor | Población total, ≥65 y <5 años | % ≥65, enfermedades crónicas (si hay datos comunales), hacinamiento | Ingreso o pobreza (estimaciones de áreas pequeñas), acceso a salud | Persona-días ≥65 en calor extremo; mortalidad atribuible |
| **Sequía y agua potable** | SPI/SPEI; caudales; déficit de precipitación | Población abastecida por APR, camiones aljibe o red | % hogares sin red pública; ruralidad | Cobertura SISS, tipo de fuente de agua, derechos DGA | Personas en comunas con escasez hídrica decretada o proyectada |
| **Inundación y remoción en masa** | Precipitación extrema (Rx1day, Rx5day); zonas inundables | Población y viviendas en zonas de amenaza | Materialidad de la vivienda; campamentos | Ingreso; planes de emergencia | Personas en zona de amenaza × frecuencia |
| **Incendios en la interfaz urbano-forestal** | Índice de peligro meteorológico de incendios; días de riesgo | Población en la interfaz urbano-forestal | Viviendas de material ligero; campamentos | Brigadas o servicios; ingreso | Personas en la interfaz × días de riesgo alto |
| **Costa: marejadas y aumento del nivel del mar** | Marejadas; aumento del nivel del mar | Población bajo cierta cota y cerca de la costa | Viviendas precarias en borde costero | Obras de protección | Personas en la franja costera expuesta |

### Paso F2. Amenaza por comuna, escenario y horizonte

Hay dos rutas, en orden de preferencia:

1. **Ruta A: indicadores ARClim comunales.** Se usan tal cual, con su fuente y versión. Limitación:
   solo cubren RCP8.5 2035–2065 frente a 1980–2010 **[V]**.
2. **Ruta B: cálculo propio desde CMIP6 regionalizado.** Permite varios escenarios y horizontes.
   - Datos: CMIP6 con reducción de escala estadística (p. ej., NEX-GDDP-CMIP6) y observación de
     referencia (CR2MET) **[NV]**.
   - Índices: `xclim` (días sobre umbral, olas de calor, SPI/SPEI, Rx1day, índice de peligro de
     incendios) **[NV]**.
   - Agregación a comuna: promedio ponderado por la **población** de cada celda, no por el área.
     Así, la amenaza refleja dónde vive la gente.
   - Ensamble: varios modelos; se reporta la mediana y el rango p10–p90. Nunca un solo modelo.
   - Recorte a Chile antes de procesar y procesamiento por bloques (restricción de RAM).

**Escalamiento por nivel de calentamiento (solo como respaldo):** si para un escenario u horizonte
no hay salidas de modelos, se puede interpolar entre niveles de calentamiento global (1.5, 2, 3 °C),
usando cambios calculados en la Ruta B para cada nivel. **No** se usan elasticidades fijas como en
la app.

### Paso F3. Exposición

- Población por comuna y grupo de edad: Censo 2024 (línea base), Censo 2017 (comparación) y
  proyecciones INE **[NV]**.
- Población dentro de zonas de amenaza: intersección espacial de manzanas o entidades censales con
  capas de amenaza (zonas inundables, interfaz urbano-forestal, franja costera). Si no hay
  cartografía a ese nivel, se usa la proporción comunal y se documenta.
- **Exposición futura:** proyecciones INE hasta donde existan. Para horizontes posteriores,
  población SSP nacional (IIASA/Wittgenstein) **[NV]**, distribuida entre comunas según su
  participación actual (supuesto explícito, con sensibilidad).

### Paso F4. Vulnerabilidad (sensibilidad + capacidad adaptativa)

- Indicadores comunales desde el Censo (edad, hogares, vivienda, hacinamiento, fuente de agua,
  combustible de calefacción y cocina), registros administrativos (SISS, MINVU campamentos,
  DEIS) y **estimaciones para áreas pequeñas** del MDSF para pobreza **[NV]**.
- **Regla para encuestas:** CASEN, ENE, EPF y ENUT **no se usan directamente a nivel comunal**,
  porque no son representativas a esa escala. Se usan:
  1. las estimaciones comunales oficiales para áreas pequeñas, cuando existan; o
  2. la estimación al nivel en que sí son representativas (región, área urbana/rural), con el
     diseño muestral completo (factores de expansión, estratos, conglomerados, `survey`/`srvyr`),
     reportando el error estándar y el coeficiente de variación.
- Supuesto base: la vulnerabilidad se mantiene constante en el tiempo, igual que en ARClim. Como
  variante, se proyecta solo la estructura de edad, que sí tiene proyección oficial.

### Paso F5. Normalización y agregación (índice compuesto)

1. **Orientación:** cada indicador se orienta de modo que un valor mayor signifique más riesgo.
2. **Normalización:** por rango percentílico entre todas las comunas, o min-max con límites fijos
   tomados de la línea base. Los límites **se fijan con la línea base y se reutilizan en los
   escenarios futuros**. Si no, el índice futuro no es comparable.
3. **Subíndices:** A, E y V se calculan cada uno como media ponderada de sus indicadores. Los pesos
   son iguales por defecto y se registran en `catalog/`.
4. **Agregación:** `R = A × E × V`, consistente con ARClim. Si conviene evitar compensación total
   entre componentes, se usa la media geométrica `(A·E·V)^(1/3)`.
5. **Robustez:** análisis de sensibilidad a pesos y a la normalización (variación aleatoria de
   pesos, Monte Carlo). Se reporta cuánto cambia el ranking de comunas.

### Paso F6. Métrica de impacto

| Cadena | Fórmula |
|---|---|
| Calor | `persona_dias = Σ_comuna (población ≥65 × días_calor_extremo)` |
| Calor (avanzado) | `muertes_atribuibles = población × tasa_base × (1 − 1/RR(T))`, con RR de un estudio publicado para Chile o la región **[NV]** y tasa base de DEIS |
| Inundación / incendio / costa | `personas_expuestas = población_en_zona × probabilidad_anual` (si existe período de retorno); si no, conteo de personas expuestas |
| Sequía | `personas_en_riesgo = población abastecida por APR/aljibe en comunas con déficit severo` |

---

## 4. Procedimiento de riesgo de transición (perspectiva de hogares y territorios)

Para una empresa, el riesgo de transición es costo, ingreso o activo varado. Para una población, la
transición actúa por **tres canales**:

| Canal | Mecanismo | Indicador comunal (o el nivel más fino disponible) | Fuente candidata |
|---|---|---|---|
| **Empleo e ingreso** | Cierre o reconversión de actividades intensivas en carbono (centrales a carbón, refinación, cadenas de combustibles) y cambios en la demanda | % de trabajadores dependientes en rubros intensivos en carbono o en transición | Estadísticas de empresas por comuna (SII) **[NV]**; ENE (regional) **[NV]**; cronograma de retiro de centrales a carbón **[NV]** |
| **Costo de la energía para el hogar** | Alza del precio de combustibles y electricidad por el precio del carbono o por regulaciones | Gasto energético como % del gasto total; hogares en pobreza energética | EPF (representativa en capitales regionales) **[NV]**; indicadores de pobreza energética **[NV]** |
| **Dependencia de combustibles regulados** | Restricciones a la leña (planes de descontaminación), cambios en la calefacción y la movilidad | % hogares con calefacción a leña; % hogares con vehículo; dependencia de diésel o gas en zonas aisladas | Censo; CASEN (regional) **[NV]** |

**Procedimiento:**

1. **Trayectorias de escenario:** desde el NGFS Scenario Explorer **[NV para las cifras]** se
   descargan, para cada escenario NGFS y la región más cercana a Chile, el precio del carbono, el
   precio de los energéticos y el PIB. Se guardan en `raw/ngfs_phase5/` con su versión. Ningún
   valor se escribe a mano.
   - Referencia de orden de magnitud: NGFS Fase V indica que se necesitaría un precio de alrededor
     de **US$300/tCO₂ al 2035** para una transición a cero neto en 2050 **[V]**
     ([NGFS Phase V outreach, nov. 2024](https://www.ngfs.net/system/files/2025-01/20241108_ngfs_scenarios_phasev_outreach_public_v2.pdf)).
2. **Traspaso a precios:** `Δprecio_energético = intensidad_de_carbono_del_energético × Δprecio_carbono × tasa_de_traspaso`.
   La intensidad sale de factores de emisión oficiales y la tasa de traspaso es un supuesto
   explícito (base 100 %, con sensibilidad).
3. **Impacto en el hogar:** `Δcarga_energética = Σ_energético (gasto_base × Δprecio_relativo) / ingreso`,
   por decil o quintil y por macrozona, con EPF/CASEN y su diseño muestral.
4. **Exposición laboral comunal:** `E_lab = trabajadores en rubros en transición / trabajadores totales`.
5. **Índice de transición comunal:** igual que en F5, con subíndices exposición laboral + carga
   energética + dependencia de combustibles, combinados con la capacidad adaptativa (ingreso,
   diversificación productiva).
6. **Oportunidades** (IFRS S2 también las pide): empleo potencial en renovables o hidrógeno verde
   por región, como contrapeso. Es opcional en la primera versión.

---

## 5. Modelado de escenarios

### 5.1 Pares coherentes (físico × transición)

Se parte de la correspondencia de la app, revisada:

| Escenario NGFS (transición) | Escenario físico consistente | Lectura |
|---|---|---|
| Net Zero 2050 / Low Demand | SSP1-1.9 / SSP1-2.6 | Transición alta, riesgo físico bajo |
| Below 2 °C | SSP1-2.6 | Transición media-alta |
| Delayed Transition | SSP1-2.6 / SSP2-4.5 | Shock de transición tardío |
| NDCs | SSP2-4.5 | Intermedio |
| Fragmented World | SSP2-4.5 / SSP3-7.0 | Alto en ambos riesgos |
| Current Policies | SSP3-7.0 / SSP5-8.5 | Transición baja, riesgo físico alto |

Las correspondencias se verifican contra la documentación NGFS (temperatura 2100 por escenario)
**[NV]**. SSP4-3.4 queda fuera hasta encontrar una fuente primaria.

### 5.2 Matriz de corridas

`comuna × cadena de impacto × escenario × horizonte × miembro del ensamble`

Es una tabla larga en `marts/riesgo_comunal/` (Parquet particionado por escenario y horizonte),
con estas columnas:
`cut, cadena, componente (A/E/V/R/impacto), indicador, escenario, horizonte, valor, p10, p90, fuente, version`.

### 5.3 Incertidumbre (obligatoria en todo resultado publicado)

1. **Climática:** rango del ensamble de modelos (p10–p90).
2. **De escenario:** se muestran siempre al menos dos escenarios.
3. **De construcción del índice:** sensibilidad a pesos y a la normalización (F5.5).
4. **Muestral:** error estándar y coeficiente de variación de las estimaciones de encuestas.
   Se marcan las celdas con CV > 30 %.

---

## 6. Implementación en el repositorio

| Paso | Dónde | Herramienta |
|---|---|---|
| Parámetros (umbrales, pesos, tasas de traspaso, pares de escenarios) | `catalog/parametros.yaml`: cada parámetro con valor, unidad, fuente y estado [V]/[NV] | Fuente única. Se elimina el problema de la app |
| Descarga de amenaza (ARClim, CMIP6, CR2MET) | `src/climachile/conectores/<fuente>/` → `raw/`, `grids/` | Python (xarray, xclim), por bloques |
| Índices climáticos por comuna | `src/climachile/indicadores/` → `staging/amenaza_comunal/` | xclim + promedio ponderado por población |
| Exposición y vulnerabilidad | conectores INE, MDSF, SISS, MINVU → `staging/` | Python; encuestas en R con `survey` |
| Índices y métricas de riesgo | `src/climachile/riesgo/` → `marts/riesgo_comunal/` | Python/SQL (DuckDB) |
| Transición | conector NGFS → `staging/ngfs/`; carga de hogares en R (`survey`) → `marts/transicion_comunal/` | Python + R |
| Informe y visualización | `reports/` (Quarto), `app/` (Shiny) | R |

---

## 7. Orden de implementación sugerido

1. Tabla territorial CUT (sin ella no se puede cruzar nada).
2. `catalog/parametros.yaml` con los parámetros de este documento y su estado de verificación.
3. **Primera cadena completa: calor y salud** (Ruta B, SSP1-2.6 y SSP5-8.5, horizontes cercano y
   medio). Es la cadena con los datos más accesibles y coincide con el piloto recomendado.
4. Segunda cadena: sequía y agua potable.
5. Riesgo de transición: primero el canal de costo energético, luego el de empleo.
6. Las demás cadenas.

## 8. Limitaciones conocidas

- La vulnerabilidad comunal depende de los registros y estimaciones para áreas pequeñas que
  existan. Lo que no existe a nivel comunal se documenta en el análisis de vacíos (Módulo 3).
- Las cartografías de amenaza (inundación, interfaz urbano-forestal) pueden no cubrir todo el país
  de forma homogénea.
- Las funciones dosis-respuesta (calor y mortalidad) dependen de estudios publicados. Si no hay uno
  para Chile, se usa uno regional y se declara.
- El riesgo de transición en hogares es un campo menos estandarizado que el físico. Los resultados
  son de **orden de magnitud y comparativos**, no predicciones.

## 9. Pendientes de verificación (antes de calcular)

- [ ] Valores de la Tabla SPM.1 contra el PDF del IPCC AR6 WG1.
- [ ] Disponibilidad y licencia de las capas comunales de ARClim (descarga programática).
- [ ] NEX-GDDP-CMIP6: acceso, variables, licencia; alternativa con CR2 o ARClim regionalizado.
- [ ] CR2MET: versión, acceso y licencia.
- [ ] NGFS Scenario Explorer: variables y regiones disponibles para Chile o Latinoamérica; licencia de uso.
- [ ] Estimaciones comunales para áreas pequeñas del MDSF (pobreza): años y acceso.
- [ ] Estadísticas de empresas del SII por comuna y rubro: nivel de detalle.
- [ ] Función dosis-respuesta calor-mortalidad aplicable a Chile.
- [ ] Población SSP para Chile (IIASA/Wittgenstein).
