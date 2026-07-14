<script>
  import { tick } from 'svelte';
  import { feature } from 'topojson-client';
  import { geoPath, geoMercator } from 'd3-geo';

  let { electorates, width, colours, winners = {} } = $props();

  // console.log("winners: ", winners)

  let wrapperEl;
  let canvasEl;

  let height = $derived(width);
  let margin = 0;

  let features = $derived(
    electorates ? feature(electorates, electorates.objects.hexmap).features : []
  );

  let geojson = $derived({
    type: 'FeatureCollection',
    features
  });


function getSeatName(d) {
  return (
    d.properties?.Seat ||
    d.properties?.seat ||
    d.properties?.DivisionNm ||
    d.properties?.division ||
    d.properties?.Division ||
    d.properties?.name ||
    d.properties?.Name ||
    d.properties?.electorate
  );
}

  function draw() {
    if (!canvasEl || !width || !geojson.features.length) return;

    const context = canvasEl.getContext('2d');

    context.clearRect(0, 0, width, height);

    const projection = geoMercator().fitExtent(
      [[margin, margin], [width - margin, height - margin]],
      geojson
    );

    const path = geoPath().projection(projection).context(context);

    for (const d of geojson.features) {
      const seatName = getSeatName(d);
      const winner = winners[seatName];

      context.beginPath();
      path(d);

      context.fillStyle = colours[winner] || '#eeeeee';
      context.fill();

      context.strokeStyle = '#ffffff';
      context.lineWidth = 1;
      context.stroke();
    }
  }

  $effect(() => {
    width;
    height;
    geojson;
    winners;

    tick().then(draw);
  });
</script>

<div bind:this={wrapperEl} style="width: 100%;">
  <canvas
    bind:this={canvasEl}
    width={width}
    height={height}
    style="width: 100%; height: auto"
  ></canvas>
</div>