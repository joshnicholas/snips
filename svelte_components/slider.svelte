<script>
	let { min = -20, max = 20, step = 1, value = $bindable(0), header, leftText, rightText, colours } = $props();
</script>

	{#if value == 0}
<div id="heady" class="vis-chart-standfirst">Preference flows at previous elections</div>
	{:else}

	{#if value > 0}

	<div id="heady" class="vis-chart-standfirst"><span class='src-article-bold-15' >+{value}pp</span> <span style="color:{colours[rightText]}">{rightText}</span> compared to previous elections</div>
	
	{:else}

	<div id="heady" class="vis-chart-standfirst"><span class='src-article-bold-15'>+{Math.abs(value)}pp</span> <span style="color:{colours[leftText]}">{leftText}</span> compared to previous elections</div>
	{/if}

{/if}



<div class="slider">
	<!-- <span id='right'>{min}</span> -->
	<span id='right' style="color:{colours[leftText]}">{leftText}</span>



    <input
		type="range"
		min={min}
		max={max}
		step={step}
		bind:value
	/>
	<!-- <span id='left'>{max}</span> -->
	<span id='left' style="color:{colours[rightText]}">{rightText}</span>

</div>

<style>
	.slider {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		width: 100%;
	}

	input[type="range"] {
		flex: 1;
	}

	span {
		min-width: 4rem;
		/* text-align: right; */
	}

#heady {
	text-align: center;
	margin:auto;
	margin-top: 10px;
	min-height: 3em;
}

.right {min-width: 100px;
}

</style>