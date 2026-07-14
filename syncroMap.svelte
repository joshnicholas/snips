<script>
  // TODO:

  // Svelte stuff

  import { onMount, tick } from 'svelte'
  
  // Mapping stuff

  import maplibregl from 'maplibre-gl';
  import 'maplibre-gl/dist/maplibre-gl.css';
  const { Map, ScaleControl, NavigationControl } = maplibregl;
  import { Protocol, PMTiles } from "pmtiles";
  import { geoOrthographic, geoPath } from 'd3-geo';
  import { select } from 'd3-selection';
  import { feature } from 'topojson-client';
  import basemapLight from '$lib/mapstyles/ml_basemapLight.json';
  import basemapLabels from '$lib/mapstyles/ml_mapLabels.json';
  import Tooltip from '$lib/components/guardian/Tooltip.svelte';

  // These need to be re-done from the ground up in a more comprehensive way
  import disputedBorders from '$lib/mapstyles/disputed_borders.json';
  import world from '$lib/mapstyles/ne_110m_land.json';
  
  // Helpers / utility
  import { getJson } from '$lib/helpers/guardian/toolbelt.js';
  import { updateScaleControlPosition, updateMinimap } from '$lib/helpers/mapping/mappingUtils.js'
  import {
    registerSyncMap,
    unregisterSyncMap,
    syncFromMap,
    isSyncing,
    twinMapsView,
  } from '$lib/stores/twinMapsView.svelte.js'
  import {
    publishTwinChoroplethTooltip,
    clearTwinChoroplethTooltip,
    twinChoroplethTooltip,
  } from '$lib/stores/twinMapsChoroplethTooltip.svelte.js'
  import {
    choroplethFillColorExpression,
    choroplethSalHoverLineFilter,
    salCodeFromGeoProps,
  } from '$lib/helpers/mapping/suburbsChoropleth.js'
  import {
    suburbNameFromProps,
    choroplethNumericValueFromProps,
    buildChoroplethTooltipHtml,
  } from '$lib/helpers/mapping/choroplethMapTooltip.js'
  import MapLegend from '$lib/components/MapLegend.svelte'

  // Use `props.*` (do not destructure) so choropleth data can arrive after mount.
  // Optional `showScale` — imperial + metric scale controls; default false (hidden).
  // Optional `onUserInteraction` — fired on pan, wheel zoom, zoom +/- controls (not programmatic camera moves).
  // Optional `showChoroplethLegend` — horizontal ramp key (default true when `choroplethColors` is set).
  // Optional `choroplethSuburbProperty` — GeoJSON property for label (default SAL_NAME21).
  // Optional `choroplethTooltipValueSuffix` — e.g. "%" for percentage columns.
  const props = $props();
  const choroplethFc = $derived(props.choroplethGeojson ?? null);
  const choroplethValueKey = $derived(props.choroplethValueProperty ?? null);
  const choroplethScaleType = $derived(props.choroplethScaleType ?? 'equalInterval');
  const choroplethColors = $derived(props.choroplethColors ?? undefined);
  const choroplethBreaks = $derived(props.choroplethBreaks ?? undefined);
  const choroplethNoDataColor = $derived(props.choroplethNoDataColor ?? undefined);
  const showChoroplethLegend = $derived(props.showChoroplethLegend !== false);
  /** Paired maps (`syncInstanceId` set) share one hover: both show suburb + each map’s value column. */
  const isTwinTooltipSync = $derived(Boolean(props.syncInstanceId));

  /** Solo maps: SAL under cursor. Twin maps: both use `twinChoroplethTooltip.salCode`. */
  let choroplethLocalHoveredSal = $state(/** @type {string | null} */ (null));
  const choroplethHoveredSalForOutline = $derived(
    isTwinTooltipSync ? twinChoroplethTooltip.salCode : choroplethLocalHoveredSal,
  );

  // Map libre setup

  let protocol = new Protocol();
  maplibregl.addProtocol("pmtiles",protocol.tile);
  let mapInstance = $state(null);
  let minimapSvg;
  let minimapPath;
  let viewportRect;
  let minimapProjection;
  /** MapLibre mounts here only — do not put Tooltip/legend/minimap in this node (Map clears the container). */
  let mapMountEl;
  let minimapContainerEl;

  let mapReadyForSync = $state(false);
  let mapStyleReady = $state(false);

  let tooltipX = $state(0);
  let tooltipY = $state(0);
  let tooltipVisible = $state(false);
  let tooltipHtml = $state('');
  let choroplethTooltipHandlersAttached = false;
  /** @type {(() => void) | null} */
  let choroplethTooltipCanvasLeaveCleanup = null;

  function hideChoroplethTooltip() {
    tooltipVisible = false;
    tooltipHtml = '';
    if (!isTwinTooltipSync) choroplethLocalHoveredSal = null;
    if (mapInstance) mapInstance.getCanvas().style.cursor = '';
  }

  /** @param {any} e */
  function onChoroplethFillMouseMove(e) {
    const f = e.features?.[0];
    const valueKey = props.choroplethValueProperty;
    const suburbKey = props.choroplethSuburbProperty ?? 'SAL_NAME21';
    const suffix = props.choroplethTooltipValueSuffix ?? '';

    if (!f || !valueKey) {
      if (isTwinTooltipSync) clearTwinChoroplethTooltip();
      hideChoroplethTooltip();
      return;
    }

    const suburb = suburbNameFromProps(f.properties, suburbKey);
    const value = choroplethNumericValueFromProps(f.properties, valueKey);

    if (suburb == null || value == null) {
      if (isTwinTooltipSync) clearTwinChoroplethTooltip();
      hideChoroplethTooltip();
      return;
    }

    if (isTwinTooltipSync) {
      const salCode = salCodeFromGeoProps(f.properties);
      if (!salCode || !e.lngLat) {
        clearTwinChoroplethTooltip();
        hideChoroplethTooltip();
        return;
      }
      publishTwinChoroplethTooltip(salCode, { lng: e.lngLat.lng, lat: e.lngLat.lat });
      if (mapInstance) mapInstance.getCanvas().style.cursor = 'pointer';
      return;
    }

    tooltipHtml = buildChoroplethTooltipHtml(suburb, value, suffix);
    tooltipX = e.point.x;
    tooltipY = e.point.y;
    tooltipVisible = true;
    choroplethLocalHoveredSal = salCodeFromGeoProps(f.properties);
    if (mapInstance) mapInstance.getCanvas().style.cursor = 'pointer';
  }

  function onChoroplethFillMouseLeave() {
    if (isTwinTooltipSync) clearTwinChoroplethTooltip();
    hideChoroplethTooltip();
  }

  function attachChoroplethTooltipHandlers() {
    const map = mapInstance;
    if (!map || choroplethTooltipHandlersAttached) return;
    if (props.mapSettings?.interactive === false) return;

    const sid = props.syncInstanceId ?? 'solo';
    const fillId = `suburbs-choropleth-${sid}-fill`;
    if (!map.getLayer(fillId)) return;

    choroplethTooltipHandlersAttached = true;
    map.on('mousemove', fillId, onChoroplethFillMouseMove);
    map.on('mouseleave', fillId, onChoroplethFillMouseLeave);

    const canvas = map.getCanvasContainer();
    if (canvas) {
      const onCanvasLeave = () => {
        if (isTwinTooltipSync) clearTwinChoroplethTooltip();
        hideChoroplethTooltip();
      };
      canvas.addEventListener('mouseleave', onCanvasLeave);
      choroplethTooltipCanvasLeaveCleanup = () => {
        canvas.removeEventListener('mouseleave', onCanvasLeave);
        choroplethTooltipCanvasLeaveCleanup = null;
      };
    }
  }

  function detachChoroplethTooltipHandlers() {
    const map = mapInstance;
    if (!map || !choroplethTooltipHandlersAttached) return;
    const sid = props.syncInstanceId ?? 'solo';
    const fillId = `suburbs-choropleth-${sid}-fill`;
    if (map.getLayer(fillId)) {
      map.off('mousemove', fillId, onChoroplethFillMouseMove);
      map.off('mouseleave', fillId, onChoroplethFillMouseLeave);
    }
    choroplethTooltipCanvasLeaveCleanup?.();
    choroplethTooltipCanvasLeaveCleanup = null;
    choroplethTooltipHandlersAttached = false;
    if (props.syncInstanceId) clearTwinChoroplethTooltip();
    hideChoroplethTooltip();
  }

  /** Twin maps: apply shared SAL + lng/lat; each instance shows its own value column. */
  $effect(() => {
    if (!isTwinTooltipSync || !mapInstance) return;
    void twinMapsView.revision;
    void twinChoroplethTooltip.revision;
    void props.width;

    const fc = choroplethFc;
    const valueKey = choroplethValueKey;
    const suburbKey = props.choroplethSuburbProperty ?? 'SAL_NAME21';
    const suffix = props.choroplethTooltipValueSuffix ?? '';

    const salCode = twinChoroplethTooltip.salCode;
    const lngLat = twinChoroplethTooltip.lngLat;

    if (!salCode || !lngLat || !fc?.features?.length || !valueKey) {
      hideChoroplethTooltip();
      return;
    }

    const feat = fc.features.find((f) => salCodeFromGeoProps(f.properties) === salCode);
    if (!feat) {
      hideChoroplethTooltip();
      return;
    }

    const suburb = suburbNameFromProps(feat.properties, suburbKey);
    const value = choroplethNumericValueFromProps(feat.properties, valueKey);
    if (suburb == null) {
      hideChoroplethTooltip();
      return;
    }

    tooltipHtml = buildChoroplethTooltipHtml(suburb, value, suffix);
    const pt = mapInstance.project([lngLat.lng, lngLat.lat]);
    tooltipX = pt.x;
    tooltipY = pt.y;
    tooltipVisible = true;
    mapInstance.getCanvas().style.cursor = 'pointer';
  });

  /** White outline on the SA whose SAL matches the active choropleth tooltip. */
  $effect(() => {
    const map = mapInstance;
    if (!map) return;
    void mapStyleReady;
    void choroplethFc?.features?.length;
    void twinChoroplethTooltip.revision;

    const sid = props.syncInstanceId ?? 'solo';
    const hoverLineId = `suburbs-choropleth-${sid}-hover-line`;
    const sal = choroplethHoveredSalForOutline;

    if (!map.getLayer(hoverLineId)) return;

    if (!sal) {
      map.setLayoutProperty(hoverLineId, 'visibility', 'none');
      return;
    }
    map.setLayoutProperty(hoverLineId, 'visibility', 'visible');
    map.setFilter(hoverLineId, /** @type {any} */ (choroplethSalHoverLineFilter(sal)));
  });

  function applySuburbsChoropleth() {
    const map = mapInstance;
    const fc = choroplethFc;
    const prop = choroplethValueKey;
    if (!map || !fc?.features?.length || !prop) return;

    const sid = props.syncInstanceId ?? 'solo';
    const suburbsSourceId = `suburbs-choropleth-${sid}`;
    const suburbsFillLayerId = `${suburbsSourceId}-fill`;
    const suburbsLineLayerId = `${suburbsSourceId}-line`;
    const suburbsHoverLineLayerId = `${suburbsSourceId}-hover-line`;

    const beforeId = map.getStyle()?.layers?.find((l) => l.type === 'symbol')?.id;
    const fillExpr = choroplethFillColorExpression(fc, prop, {
      scaleType: choroplethScaleType,
      colors: choroplethColors,
      breaks: choroplethBreaks,
      noDataColor: choroplethNoDataColor,
    });

    if (map.getSource(suburbsSourceId)) {
      map.getSource(suburbsSourceId).setData(fc);
      map.setPaintProperty(suburbsFillLayerId, 'fill-color', fillExpr);
    } else {
      map.addSource(suburbsSourceId, { type: 'geojson', data: fc });
      map.addLayer(
        {
          id: suburbsFillLayerId,
          type: 'fill',
          source: suburbsSourceId,
          paint: {
            'fill-color': fillExpr,
            'fill-opacity': 0.92,
          },
        },
        beforeId,
      );
      map.addLayer(
        {
          id: suburbsLineLayerId,
          type: 'line',
          source: suburbsSourceId,
          paint: {
            'line-color': '#121212',
            'line-width': 0.6,
            'line-opacity': 0.55,
          },
        },
        beforeId,
      );
    }

    if (!map.getLayer(suburbsHoverLineLayerId)) {
      map.addLayer(
        {
          id: suburbsHoverLineLayerId,
          type: 'line',
          source: suburbsSourceId,
          layout: { visibility: 'none' },
          paint: {
            'line-color': '#ffffff',
            'line-width': [
              'interpolate',
              ['linear'],
              ['zoom'],
              5,
              1,
              9,
              1.5,
              12,
              2,
              16,
              2.5,
            ],
            'line-opacity': 1,
          },
        },
        beforeId,
      );
    }

    attachChoroplethTooltipHandlers();
  }

  $effect(() => {
    const ready = mapStyleReady;
    const fc = choroplethFc;
    const prop = choroplethValueKey;
    const map = mapInstance;
    // Track scale options so the effect re-runs when they change
    void choroplethScaleType;
    void choroplethColors;
    void choroplethBreaks;
    void choroplethNoDataColor;
    if (!ready || !fc?.features?.length || !prop || !map) return;

    try {
      applySuburbsChoropleth();
    } catch (err) {
      console.warn('[SyncroMap] choropleth apply:', err);
    }
  });

  /** Sync handler: forward this map's camera to all registered peers. */
  function handleSyncMove() {
    const sid = props.syncInstanceId;
    if (!sid || !mapReadyForSync) return;
    syncFromMap(sid);
  }

  // Watch for width changes and resize map
  $effect(() => {
    // Track width changes
    props.width;
    if (mapInstance && mapInstance.loaded()) {
      // Wait for DOM to update, then resize the map
      tick().then(() => {
        // Use double requestAnimationFrame to ensure browser has painted
        // and container dimensions are updated
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            mapInstance.resize();
          });
        });
      });
    }
  });

  // Component lifecycle
  onMount(() => {
    const showScale = props.showScale === true;

    function notifyUserInteraction() {
      props.onUserInteraction?.();
    }

    /** +/- control without easeTo animation so twin maps stay aligned with the shared store. */
    function createSyncedZoomNavControl() {
      return {
        onAdd(map) {
          this._map = map;
          this._container = document.createElement('div');
          this._container.className = 'maplibregl-ctrl maplibregl-ctrl-group';

          const addBtn = (label, extraClass, delta) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = extraClass;
            btn.title = label;
            btn.setAttribute('aria-label', label);
            // MapLibre’s CSS targets `button … .maplibregl-ctrl-icon` for the +/- SVG backgrounds.
            const icon = document.createElement('span');
            icon.className = 'maplibregl-ctrl-icon';
            icon.setAttribute('aria-hidden', 'true');
            btn.appendChild(icon);
            btn.addEventListener('click', (ev) => {
              ev.preventDefault();
              if (isSyncing() || !map.loaded()) return;
              const c = map.getCenter();
              const cur = map.getZoom();
              const minZ = map.getMinZoom();
              const maxZ = map.getMaxZoom();
              const z = Math.min(maxZ, Math.max(minZ, cur + delta));
              if (z === cur) return;
              map.jumpTo({ center: c, zoom: z, duration: 0 });
              // The move/zoom event handlers will call syncFromMap automatically
            });
            return btn;
          };

          this._container.appendChild(addBtn('Zoom in', 'maplibregl-ctrl-zoom-in', 1));
          this._container.appendChild(addBtn('Zoom out', 'maplibregl-ctrl-zoom-out', -1));
          return this._container;
        },
        onRemove() {
          this._container?.remove();
          this._container = undefined;
          this._map = undefined;
        },
      };
    }

    // Example of fetching data to show
    // const strikesData = await getJson("https://interactive.guim.co.uk/docsdata/13BFRha2pzO3WTwEIiezHejJv3EtK2O6sm07jmgNMxuU.json");

    const mapStyle =  {
      ...basemapLight,
      layers: [...basemapLight.layers, ...basemapLabels.layers]
    };


    mapInstance = new Map({
      container: mapMountEl,
      style: mapStyle,
      center: props.mapSettings.center,
      cooperativeGestures: props.width != null && props.width < 480 ? true : false,
      zoom: props.mapSettings.zoom,
      attributionControl: false,
      bearing: 0,
      pitch: 0,
      maxPitch: 0,
      pitchWithRotate: false,
      touchPitch: false,
    })

  
    // Disable interactions if mapSettings.interactive is false

    if (!props.mapSettings.interactive) {
      mapInstance.dragPan.disable();
      mapInstance.scrollZoom.disable();
      mapInstance.boxZoom.disable();
      mapInstance.doubleClickZoom.disable();
      mapInstance.touchZoomRotate.disable();
    } else if (props.syncInstanceId) {
      mapInstance.scrollZoom.disable();
      mapInstance.doubleClickZoom.disable();
      mapInstance.boxZoom.disable();
    }

    if (showScale) {
      mapInstance.addControl(new ScaleControl({
        unit: 'imperial'
      }), 'bottom-right');

      mapInstance.addControl(new ScaleControl({
        unit: 'metric'
      }), 'bottom-right');
    }

    if (props.syncInstanceId) {
      mapInstance.addControl(createSyncedZoomNavControl(), 'top-left');
    } else {
      mapInstance.addControl(new NavigationControl({
        showCompass: false
      }), 'top-left');
    }



    // Convert TopoJSON world land boundaries to GeoJSON FeatureCollection
    const worldGeo = feature(world, world.objects.ne_110m_land);

    // Set up minimap
    // Maybe later move all the minimap to its own component because it will look neater

    const minimapWidth = 150;
    const minimapHeight = 100;

    // Use orthographic projection for globe-style minimap, centered on main map `center`
    // Fix this later to update as required with panning etc

    minimapProjection = geoOrthographic()
      .rotate([-props.mapSettings.center[0], -props.mapSettings.center[1]])
      .fitExtent([[0, 0], [minimapWidth, minimapHeight]], worldGeo);

    minimapPath = geoPath().projection(minimapProjection);

    // Create SVG for minimap
    minimapSvg = select(minimapContainerEl)
      .append('svg')
      .attr('width', minimapWidth)
      .attr('height', minimapHeight);

    // Circular clip path and outline
    const radius = Math.min(minimapWidth, minimapHeight) / 2;
    const cx = minimapWidth / 2;
    const cy = minimapHeight / 2;

    const defs = minimapSvg.append('defs');
    
    const minimapClipId = `minimap-clip-${props.syncInstanceId ?? 'solo'}`;
    defs.append('clipPath')
      .attr('id', minimapClipId)
      .append('circle')
      .attr('cx', cx)
      .attr('cy', cy)
      .attr('r', radius);

    // Group for globe content, clipped to circle
    const minimapGroup = minimapSvg.append('g')
      .attr('clip-path', `url(#${minimapClipId})`);

    // White circular background so non-land areas inside globe are white
    minimapGroup.append('circle')
      .attr('cx', cx)
      .attr('cy', cy)
      .attr('r', radius)
      .attr('fill', '#FFFFFF')
      .attr('stroke', 'none');


    minimapSvg.append('circle')
      .attr('cx', cx)
      .attr('cy', cy)
      .attr('r', radius)
      .attr('fill', 'none')
      .attr('stroke', '#000')
      .attr('stroke-width', 1);  

    minimapGroup
      .selectAll('path')
      .data(worldGeo.features)
      .enter()
      .append('path')
        .attr('d', minimapPath)
        .attr('fill', '#F3F3F3')
        .attr('stroke', '#121212')
        .attr('stroke-width', 0.5)
        .attr('fill-rule', 'evenodd');

    // Add viewport rectangle (on top of globe, inside clip)
    viewportRect = minimapGroup.append('path')
      .attr('fill', 'none')
      .attr('stroke', '#CC0A11')
      .attr('stroke-width', 1);

    // Function to log map center and zoom

    function logMapState() {
      const center = mapInstance.getCenter();
      const zoom = mapInstance.getZoom();
      const bounds = mapInstance.getBounds();
      const sw = bounds.getSouthWest();
      const ne = bounds.getNorthEast();
      /*console.log(
        `Center: ${center.lng}, ${center.lat}, Zoom: ${zoom}`,
        `Bounds SW: ${sw.lng}, ${sw.lat}, NE: ${ne.lng}, ${ne.lat}`
      );*/
    }

    // Function to set up map after it loads  
    function setupMapAfterLoad() {
      updateMinimap(mapInstance, minimapPath, viewportRect); // Initial update
      if (showScale) updateScaleControlPosition();

      if (props.mapSettings?.interactive !== false) {
        mapInstance.on('dragstart', notifyUserInteraction);
        mapInstance.on('wheel', notifyUserInteraction);
        mapInstance.on('boxzoomstart', notifyUserInteraction);
        requestAnimationFrame(() => {
          mapInstance
            .getContainer()
            .querySelectorAll('.maplibregl-ctrl-zoom-in, .maplibregl-ctrl-zoom-out')
            .forEach((btn) => btn.addEventListener('click', notifyUserInteraction));
        });
      }

      // Listen to map movement and zoom events
      mapInstance.on('move', () => {
        updateMinimap(mapInstance, minimapPath, viewportRect);
        logMapState();
        if (showScale) updateScaleControlPosition();
      });
      // IMPORTANT: pass a function reference. Passing `updateMinimap(...)` would call it immediately
      // and register `undefined` as the handler, which MapLibre will later try to `.call` during events.
      mapInstance.on('moveend', () => updateMinimap(mapInstance, minimapPath, viewportRect));
      mapInstance.on('zoom', () => {
        updateMinimap(mapInstance, minimapPath, viewportRect);
        logMapState();
        if (showScale) updateScaleControlPosition();
      });
      mapInstance.on('zoomend', () => updateMinimap(mapInstance, minimapPath, viewportRect));
      mapInstance.on('resize', () => updateMinimap(mapInstance, minimapPath, viewportRect));

      if (props.syncInstanceId) {
        mapInstance.on('move', handleSyncMove);
        mapInstance.on('zoom', handleSyncMove);
        mapInstance.on('moveend', handleSyncMove);
        mapInstance.on('zoomend', handleSyncMove);
      }
    }

    /**
     * When the style is already loaded (embed/cache), `load` will not fire again.
     * We must still run this block or `mapStyleReady` stays false and the choropleth never applies.
     */
    function onMapFullyLoaded() {
      setupMapAfterLoad();

      // mapInstance.setCenter(center);
      // mapInstance.resize();
      const canvas = mapInstance.getCanvas();
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      const aspect = width / height;
      // optional padding for desktop / mobile, currently not in use 
      // let padding = aspect > 1 ? paddingDesktop : paddingMobile;
     
      if (props.mapSettings.viewBounds) {
        mapInstance.fitBounds(props.mapSettings.viewBounds, {
          duration: 0
        });
      }

      requestAnimationFrame(() => {
        mapReadyForSync = true;
        if (props.syncInstanceId) {
          registerSyncMap(props.syncInstanceId, mapInstance);
        }
      });


      // Manual disputed borders from file, these need to be updated
      // There are also dispuated borders in the underlying pmtiles data
      // We probably need to discuss disputed borders approach generally


      mapInstance.addSource('disputed-borders', {
        type: 'geojson',
        data: disputedBorders
      });

      mapInstance.addLayer({
        id: 'disputed-borders-layer',
        type: 'line',
        source: 'disputed-borders',
        paint: {
          'line-color': '#A1A1A1',
          'line-width': [
                "interpolate",
                ["linear"],
                ["zoom"],
                4, 0.4,
                8, 0.6,
                12, 0.8,
                16, 1.2
                ],
          'line-dasharray': [1.5, 1.5]
        }
      });


      // All the map settings toggles

      mapInstance.setLayoutProperty("county", "visibility", props.mapSettings.showCounties ? "visible" : "none");
      mapInstance.setLayoutProperty("city-labels", "visibility", props.mapSettings.showCityLabels ? "visible" : "none");
      mapInstance.setLayoutProperty("town-labels", "visibility", props.mapSettings.showTownAndLocalityLabels ? "visible" : "none");
      mapInstance.setLayoutProperty("country-labels", "visibility", props.mapSettings.showCountryLabels ? "visible" : "none");
      mapInstance.setLayoutProperty("capital-labels-lowzoom", "visibility", props.mapSettings.showCapitalLabels ? "visible" : "none");
      mapInstance.setLayoutProperty("capital-labels-highzoom", "visibility", props.mapSettings.showCapitalLabels ? "visible" : "none");

      // Demo code to highlight a particular country label in the same style that graphics uses
      // To do: add the option to do this at the spreadsheet level

      if (props.mapSettings.highlightCountry) {
        
        mapInstance.setFilter("country-labels", [
          "all",
          ["==", ["get", "kind"], "country"],
          ["!=", ["get", "name:en"], props.mapSettings.highlightCountry]
        ]);

        mapInstance.addLayer({
          id: `places-labels-highlight-${props.syncInstanceId ?? 'solo'}`,
          type: "symbol",
          source: "pmvt",
          "source-layer": "places",
          filter: ["all", ["==", ["get", "kind"], "country"], ["==", ["get", "name:en"], props.mapSettings.highlightCountry]],
          layout: {
            "text-field": ["get", "name:en"],
            "text-font": ["GH Guardian Headline Bold"], // or whatever bold family you have
            "text-size": 16
          },
          paint: {
            "text-color": "#121212",
            "text-halo-width": 0
          }
        }, "country-labels"); 

      }


      // Demo code to replace label text from the underlying data
      // We need to go through the style guide and check for country names

      mapInstance.setLayoutProperty("country-labels", "text-field", [
      "case",
      ["==", ["get", "name:en"], "United Arab Emirates"],
      "UAE",                  // replacement text
      ["get", "name:en"]      // default: original label
      ]);  


  //   mapInstance.addSource('strikes', {
  //     type: 'geojson',
  //     data: strikesGeoJSON
  //   }); 

  //   // console.log(strikesGeoJSON);
  //   mapInstance.addLayer({
  //     id: 'strikes-layer',
  //     type: 'circle',
  //     source: 'strikes',
  //     paint: {
  //       'circle-radius': 3,
  //       'circle-color': ['get', 'color'],
  //       'circle-stroke-color': '#ffffff',
  //       'circle-stroke-width': 1,
  //       'circle-opacity': [
  //         'match',
  //         ['get', 'recency'],
  //         'old', 0.5,   // old strikes
  //         0.9           // default (recent or anything else)
  //       ]
  //     }
  //   },
  //   'town-labels'
  // );

    // Log data for clicked strike features
    // mapInstance.on('click', 'strikes-layer', (e) => {
    //   const feature = e.features && e.features[0];
    //   if (feature) {
    //     console.log('Strike clicked:', feature.properties, feature);
    //   }
    // });

      mapStyleReady = true;
      // Run once the flag is committed; avoids rare ordering gaps vs the choropleth $effect.
      requestAnimationFrame(() => {
        try {
          applySuburbsChoropleth();
        } catch (err) {
          console.warn("[SyncroMap] choropleth apply after load:", err);
        }
      });
    }

    if (mapInstance.loaded()) {
      onMapFullyLoaded();
    } else {
      mapInstance.once('load', onMapFullyLoaded);
    }

    // mapInstance.on('resize', () => {
    //   console.log('resize');
    //   mapInstance.setCenter(center);
    //   // mapInstance.resize();
    // });

    return () => {
      detachChoroplethTooltipHandlers();
      if (props.syncInstanceId) {
        unregisterSyncMap(props.syncInstanceId);
      }
      mapReadyForSync = false;
      mapStyleReady = false;
      mapInstance?.remove();
      mapInstance = null;
    };
  });

</script>


  <div
    class="syncro-map-root {props.mapSettings?.interactive ? 'interactive' : 'non-interactive'}"
  >
    <div class="syncro-map-canvas" bind:this={mapMountEl}></div>
    {#if showChoroplethLegend && (props.choroplethColors?.length ?? 0) > 0}
      <MapLegend colors={props.choroplethColors} lessLabel = '0%' moreLabel = '100%' />
    {/if}
    <div class="minimap" bind:this={minimapContainerEl}></div>
    <div class="map-choropleth-tooltip" aria-hidden="true">
      <Tooltip x={tooltipX} y={tooltipY} visible={tooltipVisible} text={tooltipHtml} />
    </div>
  </div>

   
<style lang="scss">

  :global(.non-interactive .maplibregl-canvas-container.maplibregl-interactive) {
      cursor: default !important;
  }


  .syncro-map-root {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 0;
  }

  .syncro-map-canvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
  }

  /* Above WebGL canvas + map controls; match / exceed global `.minimap { z-index: 1000 }` */
  .map-choropleth-tooltip {
    position: absolute;
    inset: 0;
    z-index: 1001;
    pointer-events: none;
  }

  :global(.tooltip .choropleth-tooltip-name) {
    font-weight: 700;
    margin-bottom: 4px;
  }

  :global(.tooltip .choropleth-tooltip-value) {
    font-size: 13px;
    color: #121212;
  }

</style>
