<script>

  import Resizer from "$lib/components/resizer.svelte";
  let atomName ='#tracker'


  let innerWidth

  let datah

  async function fetchData() {
    const res = await fetch("");
    const data = await res.json();

    
    if (res.ok) {

      datah = JSON.parse(JSON.stringify(data));
      console.log('datah: ', datah)


      return data;
    } else {
      throw new Error(data);
    }
  }



</script>

<Resizer {atomName} />


<svelte:window bind:innerWidth={innerWidth} />

<div id="outer-wrapper" class="atom interactive-wrapper">

  <div id="graphicContainer" class="row">

      <div class='figureTitle' id="chartTitle">Something something</div>
      <div class='subTitle' id="subTitle">Subtitle</div>


      {#await fetchData()}

      {:then datah} 
      <span>Hello:</span>

      {/await}
  

  </div>

  <div class='footer'>
    <span id="footnote"></span>Guardian Graphic <span id="sourceText"> | Sources: Something else.</span>
  </div>
  
  
</div>


<style lang="scss">
  h2 {
    @include f-headline();
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 20px;
  }


</style>
