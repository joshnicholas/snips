<script>
    import * as d3 from 'd3';
    export let innerWidth;
    export let datah

    let margin = {"top":30,"bottom":20,"left":130,"right":20}

    let dateParse = d3.timeParse(("%Y-%m-%d"))
    let dateFormat = d3.timeFormat("%Y")
    let yearParse = d3.timeParse(("%Y"))


    let chartWidth = innerWidth
    let chartHeight = chartWidth * 0.33

    let insideD = [...datah]
    let whys = [... new Set(insideD.map(d => d['League']))]
    let dates = insideD.map(d => dateParse(d['Match Date']))

    let ipl = insideD.filter(d => d['League'] == 'Indian Premier League')

    let all_years = ['2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']

    let highlight_years = ["2010", "2015", "2020","2024"]
    // console.log("insideD: ", insideD)
    // console.log("whys: ", whys)
    // console.log("dates: ", dates)

    console.log("ilp: ", ipl)


    let dataDict = {}

    whys.forEach(why => {
        let inter = [... insideD.filter(d => d['League'] == why)]
        dataDict[why] = inter
    })

console.log("dataDict: ", dataDict)

let svg


let yScale = d3.scaleBand()
	.range([0, chartHeight - margin.bottom])
	.domain(whys)
	.padding(1);

let xScale =  d3.scaleTime()
.domain([d3.min(dates), d3.max(dates)])
        .range([(margin.left + 5), chartWidth - margin.right])

let xTicks =    xScale.ticks(8)    
        
let colours = d3.scaleOrdinal().domain(whys)
      .range(d3.schemeTableau10)



      let lineGenerators = {}


whys.forEach(line => {

                    lineGenerators[line] = d3.line()
                    .defined(d => d['Count'] != '')
                    .x(d => xScale(dateParse(d['Match Date'])))
                    .y(d => yScale(d['League']))

                    })

let line = d3.line()
        .defined(d => d['Count'] != '')
        .x(d => xScale(dateParse(d['Match Date'])))
        .y(d => yScale(d["League"]))


</script>

<svg class='svg chartSans' width={chartWidth} height={chartHeight}>

    <g class='axis y-axis'>
        {#each whys as tick}
            <g class='tick tick-{tick}' transform='translate(0, {yScale(tick)})'>
                <!-- <line y1='0' stroke-width="2" y2='0' x1='{margin.left}' x2='{(chartWidth - margin.right)}'/> -->
        <!-- <line x2="100%"></line> -->
                <text x='{25}' dx='-20' y='4'>{tick}</text>
            </g>
        {/each}
    </g>
    
    <g class='axis x-axis'>
        {#each all_years as tick}
    
            <g class='tick' transform='translate({xScale(yearParse(tick))},{-margin.bottom})'>
    
            <line class='lineo' stroke-width="1" y1='{chartHeight-margin.bottom}' y2='{margin.top}' x1='0' x2='0' stroke='#ccc' opacity='0.5'/>
            {#if  highlight_years.includes(tick)}
                <text dx='-10' y='{chartHeight-margin.bottom}' dy="15">{dateFormat(yearParse(tick))}</text>
            {/if}
            </g>
        {/each}
    </g>


    {#each whys as line}
    <path class='trendy' fill="none" stroke="{colours(line)}" stroke-width="10" d="{lineGenerators[line](dataDict[line])}" />
    {/each}


    <!-- <path class='trendy' fill="none" stroke="{colours("Indian Premier League")}" stroke-width="2" d="{line(ipl)}" /> -->



</svg>



<style lang="scss">



  
    .tick {
        font-size: 0.5em !important;
    }
  

  
  
  </style>