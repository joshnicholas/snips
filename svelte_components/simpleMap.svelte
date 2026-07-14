<!-- SimpleMap.svelte -->
<script>
  import { onMount } from "svelte"
  import maplibregl from "maplibre-gl"
  import { Protocol } from "pmtiles"
  import { feature } from "topojson-client"
  import "maplibre-gl/dist/maplibre-gl.css"

  import basemapLight from "$lib/mapstyles/ml_basemapLight.json"
  import basemapLabels from "$lib/mapstyles/ml_mapLabels.json"
  import farrer from "$assets/farrer.json"
  import mapJumpRegions from "$assets/mapJumpRegions.json"
  import { scaleSqrt } from "d3-scale"
  import { extent } from "d3-array"

  let pmtilesProtocolRegistered = false

  function ensurePmtilesProtocol() {
    if (pmtilesProtocolRegistered) return
    maplibregl.addProtocol("pmtiles", new Protocol().tile)
    pmtilesProtocolRegistered = true
  }

  let {
    centreLon = 135,
    centreLat = -28,
    zoom = 4,
    width = "100%",
    height = "500px",
    points = [],
    radiusKey = "2025_share",
    minRadius = 3,
    maxRadius = 20,
    /**Toggle circle radii scaling like a gangsta*/
    scaleRadiiByZoom = true,
  } = $props()


  let mapEl
  let map = $state(null)
  let borderPaths = $state([])
  let canResetMap = $state(false)

  function topoToGeo(topo) {
    const key = Object.keys(topo.objects)[0]
    return feature(topo, topo.objects[key])
  }

  let mapWidth = $derived(typeof width === "number" ? `${width}px` : width)

  let mapHeight = $derived(typeof height === "number" ? `${height}px` : height)

  const geo = topoToGeo(farrer)

  function zoomRadiusMultiplier(mapZoom, {
    lowZoom = 4.5,
    highZoom = 9.5,
    minFactor = 0.22,
    maxFactor = 1,
  } = {}) {
    if (mapZoom <= lowZoom) return minFactor
    if (mapZoom >= highZoom) return maxFactor
    const t = (mapZoom - lowZoom) / (highZoom - lowZoom)
    return minFactor + (maxFactor - minFactor) * t
  }

  function jumpToRegion(regionId) {
    if (!map) return
    const f = mapJumpRegions.features.find((x) => x.properties.id === regionId)
    const bbox = f?.bbox
    if (!bbox || bbox.length !== 4) return
    const [w, s, e, n] = bbox
    map.fitBounds(
      [
        [w, s],
        [e, n],
      ],
      { padding: 52, duration: 750, maxZoom: 11.5 },
    )
  }

  function updateViewDriftState() {
    if (!map) return
    const c = map.getCenter()
    const z = map.getZoom()
    const lngClose = Math.abs(c.lng - centreLon) < 1e-4
    const latClose = Math.abs(c.lat - centreLat) < 1e-4
    const zoomClose = Math.abs(z - zoom) < 0.02
    canResetMap = !(lngClose && latClose && zoomClose)
  }

  function resetMapView() {
    if (!map) return
    map.flyTo({
      center: [centreLon, centreLat],
      zoom,
      duration: 750,
    })
  }

  function projectCoord(coord) {
    const p = map.project(coord)
    return [p.x, p.y]
  }

  function lineToPath(coords) {
    return coords
      .map((c, i) => {
        const [x, y] = projectCoord(c)
        return `${i === 0 ? "M" : "L"} ${x} ${y}`
      })
      .join(" ")
  }

  function polygonToPath(rings) {
    return rings.map((r) => `${lineToPath(r)} Z`).join(" ")
  }

  function geojsonToPaths(gj) {
    const features = gj.type === "FeatureCollection" ? gj.features : [gj]

    return features.flatMap((f) => {
      const g = f.geometry
      if (!g) return []

      if (g.type === "Polygon") return [polygonToPath(g.coordinates)]
      if (g.type === "MultiPolygon") return g.coordinates.map(polygonToPath)
      if (g.type === "LineString") return [lineToPath(g.coordinates)]
      if (g.type === "MultiLineString") return g.coordinates.map(lineToPath)

      return []
    })
  }

  let projectedPoints = $state([])
  let hoveredPoint = $state(null)

  function update() {
    if (!map) return

    borderPaths = geojsonToPaths(geo)

    const values = points
      .map((p) => +p[radiusKey])
      .filter((v) => Number.isFinite(v))

    const radiusScale = scaleSqrt()
      .domain(extent(values))
      .range([minRadius, maxRadius])

    const z = map.getZoom()
    const zoomFactor = scaleRadiiByZoom ? zoomRadiusMultiplier(z) : 1

    projectedPoints = points.map((p) => {
      const projected = map.project([p.lon, p.lat])
      const value = +p[radiusKey]
      const baseR = Number.isFinite(value) ? radiusScale(value) : minRadius

      return {
        ...p,
        x: projected.x,
        y: projected.y,
        value,
        r: baseR * zoomFactor,
      }
    })
  }

  onMount(() => {
    ensurePmtilesProtocol()

    const mapStyle = {
      ...basemapLight,
      layers: [...basemapLight.layers, ...basemapLabels.layers],
    }

    map = new maplibregl.Map({
      container: mapEl,
      style: mapStyle,
      center: [centreLon, centreLat],
      zoom,
      interactive: true,
      attributionControl: false,
    })

    map.addControl(
      new maplibregl.AttributionControl({
        compact: true,
      }),
      "bottom-right",
    )

    map.addControl(
      new maplibregl.NavigationControl({ showCompass: false }),
      "top-left",
    )

    map.on("load", () => {
      update()
      updateViewDriftState()
    })
    map.on("move", update)
    map.on("zoom", update)
    map.on("moveend", updateViewDriftState)
    map.on("zoomend", updateViewDriftState)

    return () => map?.remove()
  })

  $effect(() => {
    if (!map) return
    void [centreLon, centreLat, zoom]
    map.jumpTo({
      center: [centreLon, centreLat],
      zoom,
    })
    updateViewDriftState()
  })

  $effect(() => {
    if (!map) return
    void [mapWidth, mapHeight]
    map.resize()
    update()
  })

  $effect(() => {
    if (!map) return
    void [points, radiusKey, minRadius, maxRadius, scaleRadiiByZoom]
    update()
  })
</script>

<div
  class="wrapper"
  style={`--map-width: ${mapWidth}; --map-height: ${mapHeight};`}
>
  <div class="region-jumps" aria-label="Map region shortcuts">
    {#each mapJumpRegions.features as r (r.properties.id)}
      <button type="button" onclick={() => jumpToRegion(r.properties.id)}>
        {r.properties.label}
      </button>
    {/each}
    {#if canResetMap}
      <button type="button" class="reset-map" onclick={resetMapView}>
        Reset
      </button>
    {/if}
  </div>

  <div class="map-stage">
    <div bind:this={mapEl} class="map"></div>

    <svg class="overlay">
    {#each projectedPoints as point}
      <circle
        cx={point.x}
        cy={point.y}
        r={point.r}
        fill={point.fill ?? "red"}
        stroke="black"
        stroke-width="1"
        opacity="0.8"
        onpointerenter={() => (hoveredPoint = point)}
        onpointerleave={() => (hoveredPoint = null)}
      />
    {/each}

    {#each borderPaths as path}
      <path
        class="border"
        d={path}
        fill="none"
        stroke="black"
        stroke-width="1"
        opacity="0.8"
        vector-effect="non-scaling-stroke"
      />
    {/each}

    
  </svg>

    {#if hoveredPoint}
      <div
        class="tooltip"
        style={`left: ${hoveredPoint.x}px; top: ${hoveredPoint.y}px;`}
      >
        <strong>{hoveredPoint.PollingPlace}</strong><br />
        Primary: {hoveredPoint.value}%
      </div>
    {/if}
  </div>
</div>

<style>
  .map {
    z-index: 1;
  }

  .region-jumps {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    gap: 20px;
    margin-bottom: 12px;
    pointer-events: auto;
  }

  .region-jumps button {
    font-family: GuardianTextSans, "Guardian Text Sans Web", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif;
    font-size: 12px;
    line-height: var(--sans-line-height);
    font-weight: 400;
    padding: 8px 18px;
    border: 1px solid #b8b8b8;
    border-radius: 9999px;
    background: #fff;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
    cursor: pointer;
    text-align: center;
    white-space: nowrap;
    color: #121212;
  }

  .region-jumps button:hover {
    background: #f3f3f3;
  }

  .region-jumps button:focus-visible {
    outline: 2px solid #121212;
    outline-offset: 2px;
  }

  .wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    width: var(--map-width);
    max-width: none;
    padding: 0;
  }

  .map-stage {
    position: relative;
    width: 100%;
    height: var(--map-height);
    flex-shrink: 0;
  }

  .map,
  .overlay {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
  }

  .overlay {
    pointer-events: none;
    z-index: 2;
  }

  .overlay circle {
    pointer-events: auto;
    cursor: pointer;
  }

  .border {
    pointer-events: none;
  }

  .tooltip {
    position: absolute;
    z-index: 3;
    transform: translate(10px, -100%);
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #999;
    padding: 4px 6px;
    font-family: GuardianTextSans, "Guardian Text Sans Web", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif;
    font-size: 12px;
    line-height: 1.3;
    pointer-events: none;
    white-space: nowrap;
  }


</style>
