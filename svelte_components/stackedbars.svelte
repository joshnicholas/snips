<script>



  import * as d3 from "d3";

let {datah, margin, clientWidth, variables, titles, units, labels} = $props();




console.log("clientWidth: ", clientWidth)

// console.log("Hi")

let width = clientWidth - margin.right - margin.left
// let height = $derived(width * 0.6)
let height = $derived(clientWidth)


    let colourDict = {}


let innerH = height - margin.bottom

let xScale = $derived(
    d3.scaleBand()
      .domain(variables)
      .range([margin.left, width - margin.left])
      .paddingInner(0.3)
      .paddingOuter(0)
  );

let totalsByVar = $derived(
    Object.fromEntries(variables.map(v => [v, d3.sum(datah, d => +d[v] || 0)]))
  );


let scales = $derived(
    Object.fromEntries(
      variables.map(v =>
        [v, d3.scaleLinear().domain([totalsByVar[v], 0]).range([margin.top, innerH])]
      )
    )
  );

let segmentsByVar = $derived(
    Object.fromEntries(
      variables.map(v => {
        let acc = 0;
        const segs = datah.map(d => {
          const val = +d[v] || 0;
          const s = { Party: d.Party, y0: acc, y1: acc + val };
          acc += val;
          return s;
        });
        return [v, segs];
      })
    )
  );

const byParty = $derived(
    Object.fromEntries(
      variables.map(v => [v, new Map(segmentsByVar[v].map(s => [s.Party, s]))])
    )
  );

  const centerX = (v) => xScale(v) + xScale.bandwidth() / 2;
  const fmt = d3.format('.0f');

  const midBetween = (i) => {
    if (i < 0 || i >= variables.length - 1) return null;
    const a = xScale(variables[i]);
    const b = xScale(variables[i + 1]);
    if (a == null || b == null) return null;
    const rightEdge = a + xScale.bandwidth();
    const leftEdgeNext = b;
    return (rightEdge + leftEdgeNext) / 2;
  };



</script>



<svg {width} {height}>

    <text x={midBetween(0)} y={margin.top / 3} text-anchor="middle"></text>
<text x={midBetween(2)} y={margin.top / 3} text-anchor="middle"></text>
    
  {#each variables as v}
    <g>
      <text
        x={centerX(v)}
        y={margin.top -10}
        text-anchor="middle"
        dominant-baseline="middle"
        font-size="12"
        fill="#000"
        pointer-events="none"
      >
        {titles[v] ?? v}
      </text>
    </g>
  {/each}


{#each variables as v, i}
  {#each segmentsByVar[v] as s}
    <rect
      class="segment"
      x={xScale(v)}
      y={scales[v](s.y1)}
      width={xScale.bandwidth()}
      height={scales[v](s.y0) - scales[v](s.y1)}
      fill={colourDict[s.Party]}
    />
    {#if s.y0 > 0}
      <line
        x1={xScale(v)}
        x2={xScale(v) + xScale.bandwidth()}
        y1={scales[v](s.y0)}
        y2={scales[v](s.y0)}
        stroke="#fff"
        stroke-width="1"
      />
    {/if}
  {/each}

  {#if v === 'Current' && i < variables.length - 1}
    {@const next = variables[i + 1]}
    {@const rightEdge = xScale(v) + xScale.bandwidth()}
    {@const leftEdgeNext = xScale(next)}
    {@const mid = (rightEdge + leftEdgeNext) / 2}
    <line
      x1={mid}
      x2={mid}
      y1={margin.top}
      y2={height - margin.bottom}
      stroke="#000"
      stroke-width="1"
      shape-rendering="crispEdges"
      pointer-events="none"
    />
  {/if}


{/each}



{#each labels as party}
  {#each variables as v}
    {@const seg = byParty[v]?.get(party)}
    {#if seg}
      <text
        x={centerX(v)}
        y={scales[v]((seg.y0 + seg.y1) / 2)}
        text-anchor="middle"
        dominant-baseline="middle"
        font-size="15"
        fill="#fff"
        pointer-events="none"
      >
        {fmt(seg.y1 - seg.y0)}{units[v] ?? ''}
      </text>
    {/if}
  {/each}
{/each}
</svg>


<style>

.segment {
border-top: 1px solid #fff;

}

</style>
