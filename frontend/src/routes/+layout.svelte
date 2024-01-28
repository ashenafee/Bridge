<script lang="ts">
	import '../app.postcss';
	import { AppShell, AppBar } from '@skeletonlabs/skeleton';
	import Icon from '@iconify/svelte';
</script>

<AppShell>
	<svelte:fragment slot="header">
		<AppBar>
			<svelte:fragment slot="lead">
				<Icon icon="mdi:download" />
			</svelte:fragment>
			Batch Download
		</AppBar>
	</svelte:fragment>
	
	<slot />
</AppShell>
