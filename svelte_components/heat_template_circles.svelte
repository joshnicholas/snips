<script>
import * as d3 from 'd3';
export let chartWidth;
export let chartHeight;

export let datah
export let chosen

export let innerWidth

// let insideD = datah.map(d => d)
let insideD

let halfo
$: halfo = innerWidth / 2
// $: console.log("chosen: ", chosen)
// $: console.log("Keys: ", Object.keys(datah[0]))

var dateParse = d3.timeParse(("%Y-%m-%d"))
var dateFormat = d3.timeFormat("%-d %b")
var toolDateFormat = d3.timeFormat("%-d %b %Y")

let margin = {"top":10,"bottom":10,"left":26,"right":60}

// $: insideD = insideD.filter(d => d.Combined_key == chosen)
$: insideD = datah.filter(d => d.Combined_key == chosen)

// $: console.log("insideD: ", insideD)

let dates = []
let values = []

// let numCols = ['Max temp','Median', 'Max', 'Min', '10th', '90th']
let numCols = ['Max temp']

let xScale
let yScale

let xTicks
let yTicks
let lower
let upper

$: {
    dates = insideD.map(d => dateParse(d['Chart_date']))

        values = insideD.map(d => d['Max temp'])

        xScale = d3.scaleTime()
        .domain([d3.min(dates), d3.max(dates)])
        .range([(margin.left + 5), chartWidth - margin.right])

    yScale = d3.scaleLinear()
    .domain([d3.min(values), d3.max(values)])
    .range([chartHeight - margin.bottom - margin.top, margin.top]);

    xTicks = xScale.ticks(3)
    yTicks = yScale.ticks(3)

    lower = d3.min(values)
    upper = d3.max(values)

}

let first
let ninety_threshold
let ten_threshold
let median 
let colours 
let aaarrrgh
let tooltip


$: {
    first = insideD[0]
    // console.log("first: ", first)

    ninety_threshold = +first['90th']
    ten_threshold = +first['10th']
    median = +first['Median']

    colours = d3.scaleThreshold(["#005689", "#ffbb00", "#ffbb00", "#cc2b12"])
    .domain([ten_threshold, median, ninety_threshold])

    aaarrrgh = d3.scaleOrdinal([4, 5, 5])
    .domain(["notnow", 'now', 'forecast'])

    // console.log("now: ", aaarrrgh("notnow"))

    d3.select('#graphicContainer').selectAll(".tooltip").remove()
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


}

  // #### function for mouseover 
  function ovver(event) {
 

 let datter = event.currentTarget.getAttribute("datto")
//  console.log("Datto: ", datter)
 let yesser = event.currentTarget.getAttribute("why")
//  console.log("Yesser: ", yesser)
 let yearo = event.currentTarget.getAttribute("yearo")

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

       tooltip.style("left", (event.offsetX - 100) + "px");

   } else  {

       tooltip.style("left", event.offsetX + "px");

   }

   tooltip.style("visibility", "visible")
   tooltip.style("top", (yScale(yesser) + 150)  + "px");
//    tooltip.html(`
//    <strong>${yearo}</span></strong>: ${yesser}°C`)

tooltip.html(`
   <strong>${toolDateFormat(dateParse(datter))}</span></strong>: ${yesser}°C`)


 let circles = d3.selectAll('.circlos')
 circles.style("opacity", "0.4");


}




function outter() {
  let circles = d3.selectAll('.circlos')
    circles.style("opacity", 1)

  let recto = d3.selectAll('#recty')

  recto.remove()

  tooltip.style("visibility", "hidden")

}



let changeArea = d3.area()
      .x(d => xScale(dateParse((d.Date))))
      .y0(d => yScale(+d.Bottom))
        .y1(d => yScale(+d.Top))


      let mockData 
      let fore
      let foreDates = []
      
      $: {
        fore = insideD.map(d => d)
        fore = fore.filter(d => d.Now == 'forecast')
        foreDates = fore.map(d => d.Date)
        console.log("fore: ", fore)
        
        mockData = [{
        "Date": d3.min(foreDates),
        "Bottom": lower,
        "Top": upper
      },
      {
        "Date": d3.max(foreDates),
        "Bottom": lower,
        "Top": upper
      }]

}


</script>

<!-- <text style="text-anchor: end" x={(chartWidth - margin.right - 2)} y="{(15+2)}" class="changedText">Forecast*</text> -->
<path id='changed' fill="#bdbdbd" d="{changeArea(mockData)}" />

<g class='axis y-axis'>
    {#each yTicks as tick}
        <g class='tick tick-{tick}' transform='translate(0, {yScale(tick)})'>
            <line y1='0' stroke-width="2" y2='0' x1='{margin.left}' x2='{(chartWidth - margin.right)}'/>
    <!-- <line x2="100%"></line> -->
            <text x='{margin.left}' dx='-25' y='4'>{tick}°C</text>
        </g>
    {/each}
</g>




<g>
<g class='yline' transform='translate(0, {yScale(ninety_threshold)})'>
    <line y1='0' stroke-width="2" y2='0' x1={margin.left} x2='{(chartWidth)}'/>


    <!-- <text class='ytext' style="text-anchor: start" x='' y='-8'>Top 10%</text>
    <text class='ytext' style="text-anchor: start" x='' y='15'>{Math.round(ninety_threshold)}°C</text> -->

   <text class='ytext' style="text-anchor: end" x={chartWidth} y='-5'>Top 10%</text>
    <!-- <text class='ytext' style="text-anchor: start" x='' y='-5'>{Math.round(ninety_threshold)}°C</text> -->
</g>

<g class='yline' transform='translate(0, {yScale(ten_threshold)})'>
    <line y1='0' stroke-width="2" y2='0' x1={margin.left} x2='{chartWidth}'/>

    <text class='ytext' style="text-anchor: end" x={chartWidth} y='15'>Bottom 10%</text>
    <!-- <text class='ytext' style="text-anchor: start" x='' y='15'>{Math.round(ten_threshold)}°C</text> -->

    <!-- <text class='ytext' style="text-anchor: start" x='' y='15'>Bottom 10%</text> -->
    <!-- <text class='ytext' style="text-anchor: start" x='' y='-8'>{Math.round(ten_threshold)}°C</text> -->
</g>
</g> 

<g class='axis x-axis'>
    {#each xTicks as tick}

        <g class='tick' transform='translate({xScale(tick)},{-margin.bottom})'>

    <line class='lineo' stroke-width="1" y1='{chartHeight-margin.bottom}' y2='{yScale(d3.max(values))}' x1='25' x2='25' stroke='#ccc' opacity='0.5'/>
            <text dx='10' y='{chartHeight-margin.bottom}' dy="15">{dateFormat(tick)}</text>
        </g>
{/each}
</g>



{#each insideD as point}
		<circle class={point['Now']} 
        cx='{xScale(dateParse(point['Chart_date']))}' 
        cy='{yScale(+point['Max temp'])}' fill={colours(point['Max temp'])} 
        why={point['Max temp']}
        yearo = {point['Year']}
        datto = {point['Date']}
        r='{aaarrrgh(point['Now'])}' on:mouseover={ovver} on:mouseout={outter} on:focus={ovver} on:blur={ovver}/>
{/each} 


<style>

#changed {
    opacity: 0.2;
    /* border-style: dashed; */
    /* stroke-width: 2px; */
	  /* stroke:#000; */
    /* stroke-dasharray:2 2; */
  }

  .changedText {
    font-size: 0.5em
  }

.forecast {
    stroke-width:1px;
        stroke: black;
        /* fill: #4e0375; */
        stroke-dasharray:2 2;
    }


    .notnow {
        opacity: 0.1;
    }

    .now {
        /* border: 1px solid black; */

        stroke-width:1px;
        stroke: black;
    }

.ytext {
    font-size: 0.6em
}

.yline line {
    stroke-width: 2px;
	  stroke:#bdbdbd;
      stroke-dasharray:5 5;
    }
</style>