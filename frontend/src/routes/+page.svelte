<script lang="ts">
	import { writable, type Writable } from "svelte/store";
	import { ProgressBar } from '@skeletonlabs/skeleton';

	const taxnomyName: Writable<string> = writable("");
	const geneName: Writable<string> = writable("");
	const downloading: Writable<boolean> = writable(false);

	/**
	 * Resets the values of $taxnomyName and $geneName to an empty string.
	 */
	const resetButtonHandler = () => {
		$taxnomyName = "";
		$geneName = "";
	};

	const downloadButtonHandler = () => {
		// TODO: Implement download functionality
	};
</script>

<div class="flex flex-col m-10 justify-center items-center">
	<div class="flex flex-col w-full">
		<input class="input my-2" title="Taxonomy Name" type="text" placeholder="Taxonomy Name" bind:value={$taxnomyName} />
		<input class="input" title="Gene Name" type="text" placeholder="Gene Name" bind:value={$geneName} />
	</div>

	<!-- Buttons -->
	<div class="flex flex-row w-full space-x-2">
		<!-- Reset -->
		<button type="button" class="btn variant-filled my-2 w-full" on:click={resetButtonHandler}>Reset</button>
		<!-- Download -->
		<button type="button" class="btn variant-filled my-2 w-full" on:click={downloadButtonHandler}>Download</button>
	</div>

	<!-- Progress -->
	{#if !$downloading}
		<div class="w-full px-2">
			<div class="flex flex-row justify-between">
				<p class="text-sm text-gray-500">Downloading '{($geneName || 'Unknown gene')}' for all species in '{($taxnomyName || 'Unknown taxonomy')}' which have the gene available on the NCBI.</p>
			</div>
			<ProgressBar class="my-2" value={undefined} />
		</div>
	{/if}
</div>
