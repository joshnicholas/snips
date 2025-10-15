<script>
  import * as d3 from 'd3';

let {datah, margin, clientWidth, variables, titles, units, labels} = $props();

let width = clientWidth - margin.right - margin.left
// let height = $derived(width * 0.6)
let height = $derived(clientWidth)

    let colourDict = {}


  const xScale = d3.scaleBand()
    .domain(variables)
    .range([margin.left, width - margin.right])
    .paddingInner(0.1);

let parties = datah.map(d => d.Party)
  const yParty = d3.scaleBand()
    .domain(parties)
    .range([margin.top, height - margin.bottom])
    .paddingInner(0.3);



  const barHeightPx = (party, valueObj) => {
    const maxUnit = d3.max(variables, v => yScales[v](+valueObj[v] || 0)) || 0;
    if (maxUnit <= 0) return (v) => 0;
    const rowH = yParty.bandwidth();
    return (v) => (yScales[v](+valueObj[v] || 0) / maxUnit) * rowH;
  };


  const x1Border = xScale(variables[0]);
  const x2Border = xScale(variables[variables.length - 1]) + xScale.bandwidth();
  const hInRow = (v, row) => {
    const maxUnit = d3.max(variables, k => yScales[k](+row[k] || 0)) || 0;
    if (maxUnit <= 0) return 0;
    return (yScales[v](+row[v] || 0) / maxUnit) * yParty.bandwidth();
  };

  const centerX = (v) => xScale(v) + xScale.bandwidth() / 2;
  const fmt = d3.format('.0f');

  const yScales = Object.fromEntries(
    variables.map(v => {
      const maxV = d3.max(datah, d => +d[v] || 0) || 1;
      return [v, d3.scaleLinear().domain([0, maxV]).range([0, yParty.bandwidth()])];
    })
  );

  let hatched = ['Fortyfour', 'Forty']

</script>

<div class="color-key">
  {#each parties as g}
    <span class="key-item">
      <span class="dot" style="background: {colourDict[g]}"></span>
      <span>{g}</span>
    </span>
  {/each}
</div>

<svg {width} {height}>

<defs>
  <pattern id="diagHatch" patternUnits="userSpaceOnUse" width="8" height="8">
    <line x1="0" y1="8" x2="8" y2="0"
      stroke="#ccc" stroke-width="1"
      stroke-dasharray="5 5." stroke-opacity="0.9" />
  </pattern>
</defs>

    {#each hatched as v}
  {#if xScale(v) != null}
    <rect
      x={xScale(v)}
      y={0}
      width={xScale.bandwidth()}
      height={height}
      fill="url(#diagHatch)"

    />
  {/if}
{/each}

  {#each variables as v}
    <g>
      <text
        x={centerX(v)}
        y={margin.top -30}
        text-anchor="middle"
        dominant-baseline="middle"
        font-size="12"
        fill="#000"

      >
        {titles[v] ?? v}
      </text>
    </g>
  {/each}

    
{#each datah as d}
  <g transform={`translate(0, ${yParty(d.Party)})`}>
    <text
      x={margin.left + 100 - 6}
      y={yParty.bandwidth() / 2}
      text-anchor="end"
      dominant-baseline="middle"
      font-size="12"
      fill="#000"
    >{d.Party}</text>

    {#each variables as v}
      {@const val = +d[v] || 0}
      {@const h = yScales[v](val)}
      <rect
        x={xScale(v)}
        y={yParty.bandwidth() - h}
        width={xScale.bandwidth()}
        height={h}
        fill={colourDict[d.Party]}
      />
      {#if v !== 'Party'}
        <text
          x={xScale(v) + xScale.bandwidth() / 2}
          y={yParty.bandwidth() - h - 4}
          text-anchor="middle"
          dominant-baseline="alphabetic"
          font-size="11"
          fill="#000"
          pointer-events="none"
        >
          {fmt(val)}{units[v] ?? ''}
        </text>
      {/if}
    {/each}

    <line
      x1={margin.left}
      x2={width - margin.right}
      y1={yParty.bandwidth()}
      y2={yParty.bandwidth()}
      stroke="#000"
      stroke-width="1"
      shape-rendering="crispEdges"
    />
  </g>
{/each}

</svg>

<style>
  .color-key {
    display: inline-flex;        
    align-items: center;
    gap: 5px;                  
    flex-wrap: wrap;            
    margin-bottom: 10px;
  }
  .key-item {
    display: inline-flex;        
    align-items: center;
    gap: 6px;
    white-space: nowrap;
  }
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    border: 1px solid #000;
    display: inline-block;
  }
</style>
