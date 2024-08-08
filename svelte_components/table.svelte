<script>
    import * as d3 from 'd3';
    // import { Styles,Input } from 'sveltestrap';
    import { onMount } from 'svelte';
  
    export let keys
    export let datah

    export let selectedOption
    export let search
    export let howMany

    let insideD = [...datah]
    insideD = insideD.sort((a, b) => +b[selectedOption] - +a[selectedOption])

    insideD = insideD.filter(d => d['Country'].toLowerCase().includes(search.toLowerCase()))


    insideD = insideD.slice(0, howMany)
    console.log("insideD: ", insideD)

    let tableKeys = ['Country', 'Gold medals', 'Total medals', selectedOption]

    let rankKey = selectedOption
    
    // console.log("Search: ", search)

onMount(() => {


        
        if (window.frameElement) {
        const target = document.querySelector("#gv-atom");

        //   console.log("Inside version 1.1");

        // Post message to parent window to adjust the height
        window.parent.postMessage({
        sentinel: 'amp',
        type: 'embed-size',
        height: document.body.scrollHeight
        }, '*');

        // Hide the overflow to avoid scrollbars
        document.body.style.overflow = 'hidden';

        // Set the initial height of the iframe
        window.frameElement.height = target.offsetHeight;

        // Function to detect height changes of an element
        function onElementHeightChange(elm, callback) {
        let lastHeight = elm.clientHeight;
        let newHeight;
        (function run() {
        newHeight = elm.clientHeight;
        if (lastHeight !== newHeight) callback();
        lastHeight = newHeight;

        if (elm.onElementHeightChangeTimer) {
            clearTimeout(elm.onElementHeightChangeTimer);
        }
        elm.onElementHeightChangeTimer = setTimeout(run, 200);
        })();
        }

        // Watch for changes in the body's height
        onElementHeightChange(document.body, function() {
        window.frameElement.height = target.offsetHeight;
        });
        }

})


    let tableData =[
              {
                  vitae : "dolorem",
                  lectus : "ipsum",
                  quisquam : "quia"
              },
              {
                  vitae : "amet",
                  lectus : "consectetur",
                  quisquam : "adipisci"
              }
          ];
  
    // tableData = [...insideD]

    tableData = insideD.map(row => {

        // console.log("row: ", row)

        row[selectedOption] = row[selectedOption]
        // row['Per 100bn GDP'] = +row['Medals'] / (+row['GDP'] / 100000000000)

        if (+row['GDP'] > 0){
            row['Per 100bn GDP'] = (+row[selectedOption] / (+row['GDP'] / 100000000000)).toFixed(2)
        } else {
            row['Per 100bn GDP'] = '-'
        }

        if (+row['Population'] > 0){
            row['Per 10m people'] = (+row[selectedOption] / (+row['Population'] / 10000000)).toFixed(2)
        } else {
            row['Per 10m people'] = '-'
        }

        

        return row

    })

    // tableKeys.push('Per 100bn GDP')
    // tableKeys.push('Per 10m people')

    

// # Divide GDP by 100bn to get medals per 100bn GDP

// merge2["GDP"] = merge2["GDP"] / 100000000000

// # Divide pop by 10m to get medals per 10m people

// merge2["Population"] = merge2["Population"] / 10000000

// merge2['gdp_per_medal'] = merge2['n_Total']/merge2['GDP']
// merge2['medals_per_pop'] = merge2['n_Total']/merge2['Population']

    // console.log("TableData: ", tableData)

 
    let non_rank = keys.map(d => d)
    non_rank = non_rank.filter(d => d != "Rank")


    let sortBy = {col: rankKey, ascending: false};
let clicked = ''
let descending=true


    $: sort = (column) => {

        // console.log("column: ", column.toLowerCase().replace(/\s/g, ""))
        clicked=column
        rankKey = column

        const arrows = document.getElementsByClassName('arrows');

        for(var i = 0; i < arrows.length; i++){

            if (arrows[i].id == rankKey.toLowerCase().replace(/\s/g, "")){
                arrows[i].classList.remove("greyArrow")
                arrows[i].classList.add("blackArrow")
                // arrows[i].style.color("black")
                let interId = arrows[i].id
                
                console.log("interId: ", interId)
                let elem = document.getElementById(interId)
                elem.style.color = "black"

                if (descending == true){
                    elem.innerHTML = '&#9650'
                    descending = false
                } else {
                    elem.innerHTML = '&#9660'
                    descending = true
                }

            } else {
                arrows[i].classList.add("greyArrow")
                arrows[i].classList.remove("blackArrow")
                // arrows[i].style.color("black")

                let interId = arrows[i].id

                let elem = document.getElementById(interId)
                elem.style.color = "#ccc"


            }

            }






            
            if (sortBy.col == column) {
                sortBy.ascending = !sortBy.ascending
            } else {
                sortBy.col = column
                sortBy.ascending = false
            }
            
            // Modifier to sorting function for ascending or descending
            let sortModifier = (sortBy.ascending) ? 1 : -1;
            
            let sort = (a, b) => 
                (a[column] < b[column]) 
                ? -1 * sortModifier 
                : (a[column] > b[column]) 
                ? 1 * sortModifier 
                : 0;

        //   tableData = keep.map(d => d)

            tableData = tableData.sort(sort);


        }
  

        // $: tableData = tableData.filter(d => d['Country'].toLowerCase().includes(search.toLowerCase()))


  </script>

 

  <div>



  <div>
      <table>
          <thead>
              <tr >

                  {#each tableKeys as columnHeading}
                      <th class='column-header' on:click={sort(columnHeading)}>{columnHeading} <span class='arrows' id={columnHeading.toLowerCase().replace(/\s/g, "")} style={'color:grey; font-size:0.4em;'}>&#9660</span></th>
                  {/each}

              <tr/>
          </thead>
          <tbody>
              {#each Object.values(tableData) as row}

                        <tr>
                      {#each tableKeys as key}
                        
                      {#if key == selectedOption}<td class='cellText'><span style='color:#197caa'>{row[key]}</span></td>
                      {:else}<td class='cellText'>{row[key]}</td>{/if}
                          
                 
                        {/each}
                
                    <td></td>
                  </tr>
              {/each}
          </tbody>
      </table>
      </div>
  </div>



  <style>
  
      /* table {
          background-color: #fff;
      } */

/* .search {
    margin-top: 10px;
    margin-bottom: 10px;
} */

table {
  width: 100%;
  margin: 20px auto;
  table-layout: auto;
}

.cellText {
    text-align: center;
}


.column-header {text-align:center;
    /* color:#121212; */
    padding-left:4px;
    font-weight:700;
    /* font-size:11px; */
    vertical-align:top;
    font-weight:bold;
    line-height:13px;
    max-width:calc(100% - 30px);
    border-bottom:1px solid #bdbdbd;
    position:relative;
    padding-bottom: 5px;
 }

    th{ 
        margin-bottom: 25px;
        content: "\25b2";
    }



    td{padding-top: 2px;
        padding-bottom: 2px;
        border-bottom:1px dotted #d3d3d3}

        
    .greyArrow {
        fill: grey !important;
        font-size: 0.5em;
    }

    .blackArrow {
        fill: black !important;
    }


  </style>