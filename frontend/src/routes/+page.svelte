<script lang="ts">
	import { writable, type Writable } from "svelte/store";
	import { getSpecies, downloadSpecies } from "../services/apiService";
	import SpeciesList from "../components/SpeciesList.svelte";
	import Progress from "../components/Progress.svelte";


	interface Identifiers {
		txid: string;
		gene_id: string;
		nuc_id: string;
	}

	interface Species {
		name: string;
		identifiers: Identifiers[]
	}

	const taxnomyName: Writable<string> = writable("");
	const geneName: Writable<string> = writable("");
	const searching: Writable<boolean> = writable(false);
	const downloading: Writable<boolean> = writable(false);
	
	const species: Writable<Species[]> = writable([]);
	const speciesMap: Writable<{[txid: string]: string}> = writable({});
	
	let selectAll: boolean = false;
	let selectedSpecies: string[] = [];


	const searchButtonHandler = async () => {
		$searching = true;

		try {
			$species = await getSpecies($taxnomyName, $geneName, $speciesMap);
		} catch (error) {
			console.error("There has been a problem with your fetch operation:", error);
		} finally {
			$searching = false;
		}
	};

	const downloadButtonHandler = async () => {
		$downloading = true;

		const speciesSubset: {[key: string]: Identifiers[]} = parseSelectedSpecies();

		try {
			await downloadSpecies(speciesSubset, $taxnomyName, $geneName);
		} catch (error) {
			console.error("There has been a problem with your fetch operation:", error);
		} finally {
			$downloading = false;
			selectedSpecies = [];
			selectAll = false;
			$species = [];
		}
	};

	const resetButtonHandler = () => {
		$taxnomyName = "";
		$geneName = "";
		$species = [];
		$speciesMap = {};
		selectedSpecies = [];
		selectAll = false;
	};

	/**
	 * Parses the selected species and returns a dictionary of species names to identifiers.
	 * @returns {Object} - A dictionary where the key is the name of the species and the value is the list of identifiers.
	 */
	const parseSelectedSpecies = (): {[key: string]: Identifiers[]} => {
		// Map the selection of txids to the species names
		const selectedSpeciesNames = selectedSpecies.map((txid) => $speciesMap[txid]);

		// Subset the species to only include the selected species
		const selectedSpeciesData = $species.filter((s) => selectedSpeciesNames.includes(s.name));

		// Create the dictionary of names to identifiers
		const selectedSpeciesDataDict = selectedSpeciesData.reduce((acc: {[key: string]: Identifiers[]}, s) => {
			acc[s.name] = s.identifiers;
			return acc;
		}, {});

		return selectedSpeciesDataDict;
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
		<!-- Search -->
		{#if $species.length > 0}
			<button type="button" class="btn variant-filled my-2 w-full" on:click={searchButtonHandler} disabled>Search</button>
		{:else}
			<button type="button" class="btn variant-filled my-2 w-full" on:click={searchButtonHandler}>Search</button>
		{/if}
	</div>

	<!-- Progress -->
	<Progress downloading={$downloading} searching={$searching} geneName={$geneName} taxnomyName={$taxnomyName} />

	{#if $species.length > 0}
		<SpeciesList {species} bind:selectedSpecies={selectedSpecies} {selectAll} />

		<!-- Download Button -->
		<div class="flex flex-row w-full space-x-2">
			<button type="button" class="btn variant-filled my-2 w-full" on:click={downloadButtonHandler}>Download</button>
		</div>
	{/if}
</div>
