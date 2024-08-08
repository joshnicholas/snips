<script>
import Resizer from "$lib/components/resizer.svelte";

let innerWidth = 620
let isMobile = false
let chartWidth
let chartHeight

let margin = {top: 20, bottom: 12, left: 60, right: 80}

$: isMobile = innerWidth <= 400 ? true : false;

$: chartWidth =  innerWidth < 800 ? innerWidth : 800
$: chartHeight = chartWidth / 2

let atomName = 'multiLine'

</script>


<svelte:window bind:innerWidth={innerWidth} />
<Resizer {atomName} />

<div id="outer-wrapper" class="atom interactive-wrapper">

  <div id="graphicContainer" class="row">

      <div class='figureTitle' id="chartTitle">What countries exceeded expectations?</div>
      <div class='subTitle' id="subTitle">Select any two variables to see how they correlate. Last updated 7 August 2024</div>

  </div>

</div>



  <div class='footer'>
    <span id="footnote"></span>Guardian Graphic <span id="sourceText"> | Sources: Robert C. Duncan, Andrew Parece</span>
  </div>
  
  


<style lang="scss">
  h2 {
    @include f-headline();
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 20px;
  }
</style>
