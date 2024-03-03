<script lang="ts">
	import type { Writable } from "svelte/store";


    interface Identifiers {
		txid: string;
		gene_id: string;
		nuc_id: string;
	}

    interface Species {
        name: string;
        identifiers: Identifiers[]
    }

    export let species: Writable<Species[]>;
    export let selectedSpecies: string[] = [];
    export let selectAll: boolean = false;

    const handleSelectAllChange = (event: Event): void => {
		selectAll = (event.target as HTMLInputElement).checked;
		if (selectAll) {
			selectedSpecies = $species.map((s) => s.identifiers[0].txid);
		} else {
			selectedSpecies = [];
		}
	};

	const handleCheckboxChange = (txid: string, event: Event): void => {
		// If the checkbox is checked, add the txid to the selectedSpecies
		if ((event.target as HTMLInputElement).checked) {
			selectedSpecies.push(txid);
		} else {
			// If the checkbox is unchecked, remove the txid from the selectedSpecies
			selectedSpecies = selectedSpecies.filter((s) => s !== txid);
			selectAll = false;
		}
	}
</script>

<div class="flex flex-col w-full overflow-y-auto max-h-[30vh]">
    <!-- Select All -->
    <div class="flex flex-row items-center">
        <input class="checkbox mr-2" type="checkbox" id="select-all" name="select-all" bind:checked={selectAll} on:change={handleSelectAllChange} />
        <label for="select-all">Select All</label>
    </div>

    <div class="flex flex-col w-full">
        {#each $species as s}
            <div class="flex flex-row items-center">
                <input class="checkbox mr-2" type="checkbox" id={s.identifiers[0].txid} name={s.identifiers[0].txid} value={s.identifiers[0].txid} on:change={(e) => handleCheckboxChange(s.identifiers[0].txid, e)} bind:group={selectedSpecies} />
                <label for={s.identifiers[0].txid}>{s.name}</label>
            </div>
        {/each}
    </div>
</div>