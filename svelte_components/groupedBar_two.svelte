<script>
    import * as d3 from 'd3';
    // import { scaleLinear, scaleBand } from 'd3-scale';

    import { windowInnerWidth, windowInnerHeight } from '$lib/stores/dimensions.js';
  
      export let datah
      export let thing
      export let margin
      export let colours
      export let chartHeight
      export let chartWidth
      export let categories


      // console.log("Bars: ", bars)
      // let svg

    let interno = datah.map(d => d)
    // let newsy = interno.filter(d => d['Year'] == thing)
    let newsy = interno.filter(d => d['Thing'] == thing)



    let new_categories = [... new Set(newsy.map(d => d['Industry']))]
    let new_visas = [... new Set(newsy.map(d => d['variable']))]

    console.log("Thing: ", thing)
    console.log("newsy: ", newsy)
    console.log("new_categories: ", new_categories)

    // let values = []

    // bars.forEach(d => {
    //     values.push(+newsy[0][d])
    // })

    let values = newsy.map(row => +row['Other'])



    let lower = d3.min(values) 
    let upper = d3.max(values)
  
  
    let xScale
    let yScale
  
    let xTicks
    let yTicks
    let numTicks = 4
  
 
  
      $: {
        // console.log('margin.right', margin.right)
  
        xScale = d3.scaleLinear()
            .domain([0, upper])
            .range([0, (chartWidth - margin.left) - margin.right])
  
        yScale = d3.scaleBand()
        .domain(categories)
        // .range([chartHeight - margin.bottom - margin.top, margin.top]);
        .range([margin.top, (chartHeight - margin.bottom)])

        xTicks = xScale.ticks(5)
        // // xTicks = xScale.ticks(4)
        // yTicks = yScale.ticks()

      }

function drawChart(data){

  let lefter = margin.left 

  // if (thing == '2021'){
    // lefter = margin.middle
  // }

  const series = d3.stack()
      // .keys(d3.union(data.map(d => d.variable))) // distinct series keys, in input order
      .keys(new_visas)
      .value(([, D], key) => D.get(key).value) // get value for each series key and stack
    (d3.index(data, d => d.Industry, d => d.variable));

    console.log("series: ", series)

  // Compute the height from the number of stacks.
  const height = new_categories.length * 75 + margin.top + margin.bottom;


  // Prepare the scales for positional and color encodings.
  const x = d3.scaleLinear()
      .domain([0, d3.max(series, d => d3.max(d, d => d[1]))])
      .range([lefter, chartWidth - margin.right]);

  const y =  d3.scaleBand()
      // .domain(d3.groupSort(data, D => -d3.sum(D, d => d.value), d => d.Industry))
      .domain(new_categories)
      .range([margin.top, height - margin.bottom])
      // .padding(0.1);
      .paddingInner(0.45)
      .paddingOuter(0.45)


      console.log("y.bandwidth(): ", y.bandwidth())



       // Append a group for each series, and a rect for each element in the series.


       
    const svg = d3.select(`._${thing.replace(" ", "_")}`)
      // .attr("height", 775)
      .attr("height", height)

    var texto = svg.selectAll('.barText').remove()


      let keyDiv = svg.append("div")
    .attr("class", "keyDiv")

    new_visas.forEach((key) => {


      keyDiv.append("span")
      .attr("class", "keyCircle")
      .style("background-color", () => colours(key))

      keyDiv
      .append("span")
      .attr("class", "keyText")
      .text(key)

})

    console.log("Height: ", height)


    svg.append("g")
    .selectAll()
    .data(series)
    .join("g")
    .attr("fill", d => colours(d.key))
    .selectAll("rect")
    .data(D => D.map(d => (d.key = D.key, d)))
    .join("rect")
    .attr("x", d => x(d[0]))
    .attr("y", d => y(d.data[0]))
    .attr("class", d => d.key)
    .attr("height", y.bandwidth())
    .attr("width", d => x(d[1]) - x(d[0]))


      // Append the horizontal axis.
      svg.append("g")
      .attr("transform", `translate(0,${height - margin.bottom - margin.top - 10})`)
      .attr("class", "axisgroup") 
      .call(d3.axisBottom(x).ticks(3).tickSize(-height, 0, 0))
      .attr("stroke-opacity", 0.5)
      .attr("stroke-dasharray", "2,2")
      .style("stroke", '#ccc')
      .call(g => g.selectAll(".domain").remove());

  // xAxis = g => g
  //   .attr("transform", `translate(0,${0})`)
  //   .attr("class", "axisgroup") 
  //   .call(d3.axisTop(x).tickSizeOuter(0))
  //   .call(d3.axisTop(x)
  //   .tickSize(-height, 0, 0)
  //   .ticks(xTicks)
  //   .tickFormat((d) => {
  //     return numberFormat(d)
  //   })
  //   .tickPadding(10))

    // features
    // .append("g")
    // .attr("class", "x")
    // .attr("transform", "translate(0," + height + ")")
    // .call(xAxis)


  // svg.selectAll(".barText")
  //   .data(data)
  //   .enter()
  //   .append("text")
  //   .attr("class", "barText")
  //   .attr("x", margin.left)
  //   .attr("text-anchor","start")
  //   .attr("y", (d) => y(d['Industry']) - 5)
  //   .text((d) => d['Industry'])

  svg.selectAll(".barText")
    .data(new_categories)
    .enter()
    .append("text")
    .attr("class", "barText")
    .attr("x", margin.left)
    .attr("text-anchor","start")
    .attr("y", (d) => y(d) - 5)
    .text((d) => d)



}




  
  </script>



<h1 class='chartHeader'>{thing}</h1>

<div class='keyDiv chartSans row'>

  {#each new_visas as visa}
  <span class='keyCircle' style='background-color:{colours(visa)}'></span>
  <span class='keyText'>{visa} </span>
  {/each}

</div>

<svg on:load={drawChart(newsy)} class='_{thing.replace(" ", "_")}' width={chartWidth}>

  

</svg>



<style>

  .keyDiv {
    padding-left: 20px;
    min-height: 2em;
  }

  .keyCircle {
    width: 0.75rem;
    height: 0.75rem;
    border-radius: 50%;
    display: inline-block;
  }

  .keyText {
    padding-right: 5px
  }


.barText {
  color: "white";
  font-size: 0.5em !important;
}


.chartHeader {
  padding-left: 20px
}

.yTickText {
  text-align: start;
  /* color: white !important; */
  fill: white !important
}


</style>

<!-- .tick text {
  /* font-size: 0.7em; */
  text-align: middle;
} -->