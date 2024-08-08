<script>
    import * as d3 from 'd3';
    import { scaleLinear, scaleLog } from 'd3-scale';
    import { onMount } from 'svelte';
    
      export let datah
      export let margin
      export let chartHeight
      export let chartWidth

      export let selectedEx
      export let selectedWhy
      export let logs

      // console.log("logs: ", logs)

      let svg
  
      let insideD = [...datah]

      let exclude = ['Chinese Taipei', 'DPR Korea', 'Dpr Korea', 'Cuba']
      insideD = insideD.filter(d => !exclude.includes(d.Country))

      insideD = insideD.sort((a, b) => +b['Sort'] - +a['Sort'])

      console.log("insideD: ", insideD)
      // console.log("selectedEx: ", selectedEx)

      let exValues = insideD.map(d => +d[selectedEx])
      let whyValues = insideD.map(d => +d[selectedWhy])
      let populations = insideD.map(d => +d['Population'])

      let countries = insideD.map(d => d['Country'])
      let colours = d3.scaleOrdinal().domain(countries)
      .range(d3.schemeTableau10)

      // console.log("exValues: ", exValues) 
      // console.log("whyValues: ", whyValues)
      // console.log("d3.extent(whyValues): ", d3.extent(whyValues))
  
    let xScale
    let yScale
  
    let xTicks
    let yTicks
    let numTicks = 3
    let tooltip


    onMount(() => {
    tooltip = d3.select('#graphicContainer')
              .append("div")
              .attr("class", "tooltip chartSans")
              .style("background", "white")
              .style("position", "absolute")
              .style("z-index", "20")
              .style("visibility", "hidden")
              .style("top", "30px")
                .style("left", "55px")
              .html("")

    })

  
    $: halfo = chartWidth/ 2

    export function numberFormat(num) {
  
  if ( num > 0 ) {
      if ( num >= 1000000000 ) { 

          if ((num / 1000000000) % 1 == 0) {
              return ( num / 1000000000 ) + 'bn' 
          }
          else {
              return ( num / 1000000000 ).toFixed(1) + 'bn' 
          }
          
          }
      if ( num >= 1000000 ) { 

          if (( num / 1000000 ) % 1 == 0) {
            return ( num / 1000000 ) + 'm' 
          }  
          else {
            return ( num / 1000000 ).toFixed(1) + 'm' 
          }
          
          }
      if ( num >= 1000 ) {

          if (( num / 1000 ) % 1 == 0) {
            return ( num / 1000 ) + 'k' 
          }

          else {
            return ( num / 1000 ).toFixed(1) + 'k' 
          }
        }
      if (num % 1 != 0) { 
          return num
      } else { 
        return num }
  }
  if ( num < 0 ) {
      var posNum = num * -1;

      // if ( posNum >= 1000000000 ) return [ "-" + String(( posNum / 1000000000 ).toFixed(1)) + 'bn'];
      // if ( posNum >= 1000000 ) return ["-" + String(( posNum / 1000000 ).toFixed(1)) + 'm'];
      // if ( posNum >= 1000 ) return ["-" + String(( posNum / 1000 ).toFixed(1)) + 'k'];
      // else { return num }

      if ( posNum >= 1000000000 ) { 

        if ((posNum/ 1000000000) % 1 == 0) {
            return "-" + ( posNum / 1000000000 ) + 'bn' 
        }
        else {
            return "-" + ( posNum / 1000000000 ).toFixed(1) + 'bn' 
        }
        
          }
      if ( posNum >= 1000000 ) { 

          if (( posNum / 1000000 ) % 1 == 0) {
            return "-" + ( posNum / 1000000 ) + 'm' 
          }  
          else {
            return "-" + ( posNum / 1000000 ).toFixed(1) + 'm' 
          }
          
          }
      if ( posNum >= 1000 ) {

          if (( posNum / 1000 ) % 1 == 0) {
            return "-" + ( posNum / 1000 ) + 'k' 
          }

          else {
            return "-" + ( posNum / 1000 ).toFixed(1) + 'k' 
          }
        }
      if (posNum % 1 != 0) { 
          return "-" + posNum
      } else { 
        return "-" + posNum }

  }
  return num;
}


        if (logs.includes(selectedEx)){
          console.log("LOG X!")
          console.log("exValues: ", exValues)
          exValues = exValues.filter(d => +d > 0)
          xScale = d3.scaleLog()
          .domain(d3.extent(exValues))
          .range([(margin.left + 50), chartWidth - margin.right]);


        } else {
          console.log("NOT LOG X!")
          xScale = d3.scaleLinear()
          .domain(d3.extent(exValues))
            .range([margin.left, chartWidth - margin.right]);
        }

        if (logs.includes(selectedWhy)){
          whyValues = whyValues.filter(d => +d > 0)
          yScale = d3.scaleLog()
              .domain(d3.extent(whyValues))
              .range([(chartHeight - margin.bottom - margin.top), margin.top]);

        } else {
          yScale = d3.scaleLinear()
          .domain(d3.extent(whyValues))
              .range([(chartHeight - margin.bottom - margin.top), margin.top]);
        }
    
        xTicks = xScale.ticks(4)
        // xTicks = xScale.ticks(4)
        yTicks = yScale.ticks(4)

      
  
  
// ######## 



  // #### function for mouseover 
  function ovver(event) {
 
  let country = event.currentTarget.getAttribute("country")

//  console.log("Targeto: ", event.target)

 let boxWidth = 100
 let boxHeight = 50

 let lefto = true
 let bottom = true


 let offsetto
 let textAlign

 if (event.offsetX > halfo){

   offsetto = -boxWidth
   textAlign = 'end'
   lefto = false

 } else {

   offsetto = 10
   textAlign = 'start'
 }


 if (event.offsetY < halfo) {
   bottom = false
 }


   if (lefto == false) {

    // console.log("LEFTO")
  

       tooltip.style("left", (event.offsetX - 100) + "px");

   } else  {

       tooltip.style("left", event.offsetX + "px");

   }

   tooltip.style("visibility", "visible")
   // tooltip.style("left", xScale(dateParse(datter)) + "px")
   tooltip.style("top", (event.offsetY) +50 + "px");
   tooltip.style("left", ((event.offsetX) ) + "px");
   // tooltip.style("top", (event.offsetY  + 30)+ "px");
   tooltip.html(`<strong>${country}</strong>`)


 let circles = d3.selectAll('.circlos')
 circles.style("opacity", "0.5");

 let thingo = d3.select(this)
 thingo.style("opacity", "1");


}



// ### function for mouseout 
function outter() {
let circles = d3.selectAll('.circlos')
 circles.style("opacity", 0.5)

let recto = d3.selectAll('#recty')

recto.remove()

tooltip.style("visibility", "hidden")


}



let highlight = ['Australia', 'China', 'United States', 'Great Britain']

let radii = 10


let radScale = d3.scaleLinear()
          .domain(d3.extent(populations))
          .range([6, 10]);

  </script>
  
  <svg bind:this={svg} class='svg chartSans' width={chartWidth} height={chartHeight}>
  
  <g class='axis y-axis'>
    {#each yTicks as tick}
      <g class='tick tick-{tick}' transform='translate(0, {yScale(tick)})'>
        <line y1='0' stroke-width="2" y2='0' x1='{margin.left}' x2='{(chartWidth - 5)}'/>
        <text x='{margin.left}' dx='-25' y='4'>{numberFormat(tick)}</text>
      </g>
    {/each}
  </g>
  
  <g class='axis x-axis'>
    {#each xTicks as tick}
  
      <g class='tick' transform='translate({xScale(tick)},{-margin.bottom})'>
  
        <line class='lineo' y1='{chartHeight-margin.bottom}' y2='{margin.bottom + margin.top}' x1='0' x2='0' stroke='#ccc' opacity='0.5'/>
        <text y='{chartHeight-margin.bottom}' dy="20" dx=-5>{numberFormat(tick)}</text>
      </g>
    {/each}
  </g>
  
  
  
  <!-- <h1>{statto}</h1> -->
  
  <!-- <text style="text-anchor: middle" x="{(chartWidth /2)}" y="15" class="chartHeader">{statto}</text> -->
  <!-- <text style="text-start: middle" x="0" y="15" class="chartHeader">{statto}</text> -->
  

  
  {#each insideD as point}
          <circle class='circlos' id='{point.Country}' fill='{colours(point.Country)}' country='{point.Country}'
      cx='{xScale(+point[selectedEx])}' cy='{yScale(+point[selectedWhy])}' r='{radScale(point.Population)}' on:mouseover={ovver} on:mouseout={outter}  stroke='#000'
      strokeWidth='2'/>

      {#if highlight.includes(point.Country)}
      <text class='bubbleNames' y='{(yScale(+point[selectedWhy])-2)}' dy='{-(radScale(point.Population)/1)}' dx='-15' x='{xScale(+point[selectedEx])}'>{point.Country}</text>
      {/if}

  {/each} 
  
  <!-- <line y1='{yScale(50)}' stroke-width="1" y2='{yScale(50)}' x1='{margin.left}' x2='{xScale(dateParse("2023-11-05"))}' stroke="#767676"/> -->
  <!-- <line y1='{yScale(50)}' stroke-width="1" y2='{yScale(50)}' x1='{margin.left}' x2='{(chartWidth - 5)}' stroke="#767676"/> -->
  

  </svg>
  
  <style>

.circlos {
  opacity: 0.5;
  stroke-opacity: .7;
}

.bubbleNames {
  font-size: 0.5em;
}
  
    .tick text {
      font-size: 0.7em;
      text-align: middle;
    }
  </style>