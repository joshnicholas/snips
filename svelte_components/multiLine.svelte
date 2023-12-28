<script>
    import * as d3 from 'd3';
    // import { scaleLinear, scaleTime } from 'd3-scale';
    var dateParse = d3.timeParse("%Y-%m-%d")
    var dateFormat = d3.timeFormat("%Y")

    import { numberFormat } from '$lib/helpers/toolbelt.js';

    import { windowInnerWidth, windowInnerHeight } from '$lib/stores/dimensions.js';
  
      export let datah
      export let thing
      export let margin
      export let colours
      export let chartHeight
      export let chartWidth

      
      let parties = ['Arrivals', 'Departures']
      
      let svg
  

      console.log("datah: ", datah)


      // $: console.log("Chatwidth: ", chartWidth)
      // console.log("Keys: ", keys)

  
      let interno = datah.map(d => d)
      let newsy = interno.filter(d => d['Thing'] == thing)
      let dates = newsy.map(d => dateParse(d.Date))

      $: console.log("newsy: ", newsy)


      let values = []


        newsy.forEach(row =>{
          parties.forEach(party => {
            if (row[party] != ""){
              values.push(+row[party])
            }
          })
        })

        // let final = []

        // newsy.forEach(row => {

        //   final.push(Object.keys(row).reduce((acc, k) => (!row[k] && delete acc[k],  acc), row))

        // })

        // $: console.log("final: ", final)
        $: console.log("values: ", values)




      let lower = d3.min(values) 
      let upper = d3.max(values)

      $: console.log("lower: ", lower)
      $: console.log("upper: ", upper)
  

  
    let xScale
    let yScale
  
    let xTicks
    let yTicks
    let numTicks = 4
  let line 
  let lineGenerators = {}

  let coalition 
  let greens
  let labor 

      $: {
  
        xScale = d3.scaleTime()
          .domain([d3.min(dates), d3.max(dates)])
          .range([margin.left, (chartWidth ) - margin.right])

        yScale = d3.scaleLinear()
          .domain([upper, lower])
          .range([margin.top, (chartHeight - margin.bottom)])


        xTicks = xScale.ticks(5)
        yTicks = yScale.ticks(3)


        parties.forEach(line => {

          lineGenerators[line] = d3.line()
          .defined(d => d[line] != '')
          .x(d => xScale(dateParse(d.Date)))
          .y(d => yScale(d[line]))

        })



      }
  

      $: console.log("lineGenerators: ", lineGenerators)
      $: console.log("yTicks: ", yTicks)
  </script>

<h1 class='chartHeader'>{thing}</h1>

<svg bind:this={svg} class='svg chartSans' width={chartWidth} height={chartHeight}>

  <div class={thing}></div>

  <g class='axis y-axis'>
    {#each yTicks as tick}
      <g class='tick tick-{tick}' transform='translate(0, {yScale(tick)})'>
        <!-- <line y1='0' stroke-width="2" y2='0' x1='{margin.left}' x2='{xScale(d3.max(dates))}'/> -->
        <line y1='0' stroke-width="2" y2='0' x1='{margin.left}' x2='{(chartWidth - 5)}'/>
        <!-- <line x2="100%"></line> -->
        <text x='{margin.left}' dx='-25' y='4'>{numberFormat(tick)}</text>
      </g>
    {/each}
  </g>

  
  <g class='axis x-axis'>
    {#each xTicks as tick}
  
    <g class='tick' transform='translate({(xScale(tick))},{-margin.bottom})'>
  
        <line class='lineo' y1='{chartHeight-margin.bottom}' y2='{margin.bottom + margin.top}' x1='0' x2='0' stroke='#ccc' opacity='0.5'/>
        <text y='{chartHeight-margin.bottom}' dy="20" dx=-15>{dateFormat(tick)}</text>
      </g>
    {/each}
  </g>

  {#each parties as line}
    <path class='trendy' fill="none" stroke="{colours(line)}" stroke-width="2" d="{lineGenerators[line](newsy)}" />
  {/each}


  <!-- <path class='trendy' fill="none" stroke="{colours("Greens")}" stroke-width="1" d="{greens(newsy)}" />



  <path class='trendy' fill="none" stroke="{colours("Labor")}" stroke-width="1" d="{labor(newsy)}" />
  <path class='trendy' fill="none" stroke="{colours("Coalition")}" stroke-width="1" d="{coalition(newsy)}" /> -->


<!-- {#each parties as party}
  <path class='trendy' fill="none" stroke="#002c59" stroke-width="1" d="{lineGenerators[party](newsy)}" />

  {/each} -->

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