<script>
    import * as d3 from 'd3';
    import { scaleLinear, scaleBand } from 'd3-scale';

    import { windowInnerWidth, windowInnerHeight } from '$lib/stores/dimensions.js';
  
      export let datah
      export let thing
      export let margin
      export let colours
      export let chartHeight
      export let chartWidth
      export let keys 
      export let rename
      export let generations

      
      let svg
  

      // console.log("datah: ", datah)

      // $: console.log("Chatwidth: ", chartWidth)
      // console.log("Keys: ", keys)
  
  
      let interno = datah.map(d => d)
      let newsy = interno.filter(d => d['Thing'] == thing)

        let values = []

        generations.forEach(d => {
            values.push(+newsy[0][d])
        })
      // console.log("newsy: ", newsy)
    // console.log("values: ", values)

      let lower = d3.min(values) 
      let upper = d3.max(values)
  
      // console.log("lower: ", lower)
      // console.log("upper: ", upper)
  
    let xScale
    let yScale
  
    let xTicks
    let yTicks
    let numTicks = 4
  
 
  
      $: {
        // console.log('margin.right', margin.right)
  
        xScale = scaleLinear()
            .domain([0, upper])
            .range([0, (chartWidth - margin.left) - margin.right])
  
        yScale = scaleBand()
        .domain(generations)
        // .range([chartHeight - margin.bottom - margin.top, margin.top]);
        .range([margin.top, (chartHeight - margin.bottom)])

        xTicks = xScale.ticks(5)
        // // xTicks = xScale.ticks(4)
        // yTicks = yScale.ticks()

        // console.log('yScale: ', yScale)

  
      }

      // console.log("xTicks: ", xTicks)
  
      console.log(newsy)
  
  </script>

<h1 class='chartHeader'>{rename[thing]}</h1>

<svg bind:this={svg} class='svg chartSans' width={chartWidth} height={chartHeight}>

  <div class={thing}></div>

  <g class="bars">

    {#each generations as key, i}

    <rect 
    x = {margin.left}
    y = {(yScale(key) - 10)}
    width = {xScale(+newsy[0][key])}
    height = 20
    style="fill:{colours(key)}"
    />

    {/each}

  </g>


  <g class='axis y-axis'>
    {#each generations as tick}
      <g class='tick tick-{tick}' transform='translate({margin.left}, {yScale(tick)})'>
        <!-- <line y1='0' stroke-width="2" y2='0' x1='{margin.left}' x2='{xScale(d3.max(dates))}'/> -->
        <!-- <line y1='0' stroke-width="2" y2='0' x1='{margin.left}' x2='{((chartWidth + margin.left) - margin.right)}'/> -->
        <!-- <line x2="100%"></line> -->
        <text class='yTickText' x='{3}'  y='4'>{tick}</text>
      </g>
    {/each}
  </g>


  <g class='axis x-axis'>
    {#each xTicks as tick}
  
      <!-- <g class='tick' transform='translate({xScale(tick)},{-margin.bottom})'> -->
        <g class='tick' transform='translate({(xScale(tick) + margin.left)},{-margin.bottom})'>
  
        <line class='lineo' y1='{(chartHeight - margin.bottom - margin.top)}' y2='{margin.top}' x1='0' x2='0' stroke='#ccc' opacity='0.5'/>
        <text y='{chartHeight-margin.bottom}' dy="" dx="-5">{tick}%</text>
      </g>
    {/each}
  </g>

</svg>



<style>

.barText {
  color: "white";
}

  .tick text {
    font-size: 0.7em;
    text-align: middle;
  }

.yTickText {
  text-align: start;
  /* color: white !important; */
  fill: white !important
}


</style>