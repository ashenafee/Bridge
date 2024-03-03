<script lang="ts">
	import { ProgressBar } from "@skeletonlabs/skeleton";

    export let downloading: boolean;
    export let searching: boolean;
    export let geneName: string;
    export let taxnomyName: string;
</script>

{#if downloading && !searching}
	<div class="w-full px-2">
		<div class="flex flex-row justify-between">
			<p class="text-sm text-gray-500">
				Downloading '{geneName || 'Unknown gene'}' for all species in '{taxnomyName ||
					'Unknown taxonomy'}' which have the gene available on the NCBI.
			</p>
		</div>
		<ProgressBar class="my-2" value={undefined} />
	</div>
{:else if !downloading && searching}
	<div class="w-full px-2">
		<div class="flex flex-row justify-between">
			<p class="text-sm text-gray-500">
				Searching for '{geneName || 'Unknown gene'}' in '{taxnomyName || 'Unknown taxonomy'}'.
			</p>
		</div>
		<ProgressBar class="my-2" value={undefined} />
	</div>
{/if}
